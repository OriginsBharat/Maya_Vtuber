import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

class VectorMemory:
    """
    Handles the vector database for storing and retrieving long-term memories.
    """
    def __init__(self, db_path="vector_db", collection_name="maya_memory", allow_reset=False, in_memory=False):
        print("🧠 Vector Memory initializing...")
        # Load a sentence transformer model for creating embeddings
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        if in_memory:
            # Use an in-memory, ephemeral client for testing
            print("Using in-memory vector database.")
            self.client = chromadb.Client()
        else:
            # Configure settings for a persistent client
            client_settings = Settings()
            if allow_reset:
                client_settings.allow_reset = True
            print(f"Using persistent vector database at: {db_path}")
            self.client = chromadb.PersistentClient(path=db_path, settings=client_settings)

        # Get or create the collection (like a table in a traditional DB)
        self.collection = self.client.get_or_create_collection(name=collection_name)
        print("✅ Vector Memory initialized.")

    def add_memory(self, text: str, metadata: dict = None):
        """
        Adds a piece of text to the vector memory.

        Args:
            text: The text to be stored as a memory.
            metadata: Optional dictionary of metadata associated with the memory.
        """
        if not text.strip():
            return

        print(f"Adding memory: '{text[:50]}...'")

        # The text itself is used as the document and the ID
        self.collection.add(
            documents=[text],
            ids=[text] # Using text as ID is simple, but can cause collisions.
                      # A more robust system would use unique IDs.
        )

    def search_memory(self, query: str, n_results: int = 3, max_distance: float = 1.0) -> list[str]:
        """
        Searches for relevant memories based on a query, filtering by distance.

        Args:
            query: The text to search for.
            n_results: The max number of results to retrieve.
            max_distance: The maximum similarity distance to be considered relevant.
                          Lower is more similar.

        Returns:
            A list of the most relevant memories.
        """
        if not query.strip():
            return []

        print(f"Searching memory for: '{query}'")
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )

        memories = []
        documents = results.get('documents', [[]])[0]
        distances = results.get('distances', [[]])[0]

        for i, doc in enumerate(documents):
            if distances[i] <= max_distance:
                memories.append(doc)

        print(f"Found {len(memories)} relevant memories within distance {max_distance}.")
        return memories