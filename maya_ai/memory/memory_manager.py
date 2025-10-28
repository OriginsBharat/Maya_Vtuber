from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from maya_ai.config.config_manager import ConfigManager
import uuid

class MemoryManager:
    """
    Manages the long-term memory for a persona using Pinecone.
    """
    def __init__(self, persona_name: str, config_manager: ConfigManager):
        self.persona_name = persona_name
        self.config_manager = config_manager

        self.api_key = self.config_manager.get_key("PINECONE_API_KEY")
        if not self.api_key or self.api_key == "dummy_key":
            print("Warning: PINECONE_API_KEY is not valid. MemoryManager will be disabled.")
            self.pc = None
            self.index = None
            return

        self.pc = Pinecone(api_key=self.api_key)
        self.index_name = f"maya-memory-{self.persona_name.lower()}"

        if self.index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=self.index_name,
                dimension=384,
                metric='cosine'
            )
        self.index = self.pc.Index(self.index_name)
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')

    def add(self, content: str):
        if not self.index:
            return

        vector = self.encoder.encode([content]).tolist()
        self.index.upsert(vectors=[(str(uuid.uuid4()), vector, {"content": content})])

    def search(self, query: str, top_k: int = 5) -> list:
        if not self.index:
            return []

        query_vector = self.encoder.encode([query]).tolist()
        results = self.index.query(vector=query_vector, top_k=top_k, include_metadata=True)
        return [match['metadata']['content'] for match in results['matches']]

    def get_all_memories(self) -> list:
        if not self.index:
            return []

        # This is a hack to get all vectors. In a real application, you'd want to paginate.
        results = self.index.query(vector=[0]*384, top_k=1000, include_metadata=True)
        return [{"id": match['id'], "content": match['metadata']['content']} for match in results['matches']]

    def delete(self, ids: list):
        if not self.index:
            return

        self.index.delete(ids=ids)
