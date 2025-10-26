import chromadb
from chromadb.utils import embedding_functions

class MemoryManager:
    """
    Manages the long-term, persistent memory for a persona using a vector database.
    """
    def __init__(self, persona_name: str):
        """
        Initializes the MemoryManager for a specific persona.

        Args:
            persona_name: The name of the persona to create a memory for.
        """
        self.persona_name = persona_name
        self.client = chromadb.Client()

        # Use a sentence-transformer model for creating embeddings
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        # Create or get a collection (like a table in a database) for the persona
        self.collection = self.client.get_or_create_collection(
            name=f"memory_{self.persona_name}",
            embedding_function=self.embedding_function
        )

    def add_memory(self, memory_text: str, memory_id: str):
        """
        Adds a new memory to the persona's database.

        Args:
            memory_text: The text content of the memory.
            memory_id: A unique identifier for the memory.
        """
        self.collection.add(
            documents=[memory_text],
            ids=[memory_id]
        )

    def recall_memories(self, query_text: str, num_memories: int = 5) -> list:
        """
        Recalls the most relevant memories based on a query.

        Args:
            query_text: The text to search for relevant memories.
            num_memories: The maximum number of memories to return.

        Returns:
            A list of the most relevant memory documents.
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=num_memories
        )
        return results['documents'][0] if results['documents'] else []

    def get_all_memories(self) -> list:
        """
        Retrieves all memories from the collection.
        """
        return self.collection.get()['documents']

    def edit_memory(self, memory_id: str, new_memory_text: str):
        """
        Updates an existing memory.
        """
        self.collection.update(
            ids=[memory_id],
            documents=[new_memory_text]
        )

    def delete_memory(self, memory_id: str):
        """
        Deletes a memory from the collection.
        """
        self.collection.delete(ids=[memory_id])
