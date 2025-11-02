from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from maya_ai.config.config_loader import get_config
from loguru import logger
import uuid
import datetime

class MemoryManager:
    """
    Manages the long-term memory for a persona using Pinecone.
    """
    def __init__(self, persona_name: str):
        self.persona_name = persona_name
        self.config = get_config()

        self.api_key = self.config.get_api_key('PINECONE_API_KEY')
        if not self.api_key:
            raise ValueError(
                "PINECONE_API_KEY not found in environment variables.\n"
                "Please add it to your .env file:\n"
                "PINECONE_API_KEY=your_key_here"
            )

        self.pc = Pinecone(api_key=self.api_key)
        self.index_name = f"{self.config.get('memory', 'pinecone_index_prefix', 'maya-memory')}-{self.persona_name.lower()}"

        if self.index_name not in self.pc.list_indexes().names():
            logger.info(f"Creating new Pinecone index: {self.index_name}")
            self.pc.create_index(
                name=self.index_name,
                dimension=384,
                metric='cosine'
            )
        self.index = self.pc.Index(self.index_name)
        self.encoder = SentenceTransformer(self.config.get('memory', 'embedding_model'))

    def _add_memory(self, content: str, memory_type: str, speaker: str = None):
        if not self.index:
            return

        try:
            vector = self.encoder.encode([content]).tolist()
            metadata = {
                "content": content,
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "type": memory_type,
                "speaker": speaker or self.persona_name
            }
            self.index.upsert(vectors=[(str(uuid.uuid4()), vector, metadata)])
            logger.info(f"Added {memory_type} memory for {self.persona_name}: {content}")
        except Exception as e:
            logger.error(f"Failed to add memory: {e}", exc_info=True)

    def add_conversation_turn(self, speaker: str, text: str):
        self._add_memory(text, "conversation", speaker)

    def add_fact(self, fact: str):
        self._add_memory(fact, "fact")

    def recall_facts(self, query: str, top_k: int = None) -> list:
        if not self.index:
            return []

        if top_k is None:
            top_k = self.config.get('memory', 'recall_top_k', 5)

        try:
            query_vector = self.encoder.encode([query]).tolist()
            results = self.index.query(
                vector=query_vector,
                top_k=top_k,
                include_metadata=True,
                filter={"type": "fact"}
            )
            return [match['metadata']['content'] for match in results['matches']]
        except Exception as e:
            logger.error(f"Failed to recall facts: {e}", exc_info=True)
            return []

    def get_all_memories(self) -> list:
        if not self.index:
            return []

        try:
            results = self.index.query(vector=[0]*384, top_k=1000, include_metadata=True)
            return [{"id": match['id'], "content": match['metadata']['content']} for match in results['matches']]
        except Exception as e:
            logger.error(f"Failed to get all memories: {e}", exc_info=True)
            return []

    def delete(self, ids: list):
        if not self.index:
            return

        try:
            self.index.delete(ids=ids)
            logger.info(f"Deleted memories with ids: {ids}")
        except Exception as e:
            logger.error(f"Failed to delete memories: {e}", exc_info=True)
