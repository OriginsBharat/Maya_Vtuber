from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from maya_ai.config.config_manager import ConfigManager
import uuid

class MemoryManager:
    """
    Manages the long-term, persistent memory for a persona using Pinecone.
    """
    def __init__(self, persona_name: str, config_manager: ConfigManager):
        """
        Initializes the MemoryManager and connects to Pinecone.
        """
        self.persona_name = persona_name
        self.config_manager = config_manager

        # Initialize Pinecone
        self.api_key = self.config_manager.get_key("PINECONE_API_KEY")
        if not self.api_key:
            raise ValueError("PINECONE_API_KEY not found in configuration.")

        self.pc = Pinecone(api_key=self.api_key)

        # Load the sentence transformer model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.dimension = self.model.get_sentence_embedding_dimension()

        # Create or connect to the Pinecone index for this persona
        self.index_name = f"maya-memory-{self.persona_name.lower()}"
        if self.index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric='cosine',
                spec=ServerlessSpec(cloud='aws', region='us-east-1') # Use serverless for the free tier
            )
        self.index = self.pc.Index(self.index_name)

    def add_memory(self, memory_text: str, memory_id: str = None):
        """
        Adds a new memory to the persona's Pinecone index.
        """
        if not memory_id:
            memory_id = str(uuid.uuid4())

        embedding = self.model.encode(memory_text).tolist()
        self.index.upsert(vectors=[{'id': memory_id, 'values': embedding, 'metadata': {'text': memory_text}}])

    def recall_memories(self, query_text: str, num_memories: int = 5) -> list:
        """
        Recalls the most relevant memories from Pinecone.
        """
        query_embedding = self.model.encode(query_text).tolist()
        results = self.index.query(vector=query_embedding, top_k=num_memories, include_metadata=True)

        return [match['metadata']['text'] for match in results['matches']]

    def delete_memory(self, memory_id: str):
        """
        Deletes a memory from the Pinecone index.
        """
        self.index.delete(ids=[memory_id])

# Example usage will be part of the main application.
