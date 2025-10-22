import unittest
import os
import shutil
from maya_ai.memory.vector_memory import VectorMemory

class TestVectorMemory(unittest.TestCase):

    def setUp(self):
        """Set up an in-memory database with a unique collection for each test."""
        import uuid
        self.collection_name = f"test_collection_{uuid.uuid4()}"
        self.vector_memory = VectorMemory(in_memory=True, collection_name=self.collection_name)

    def tearDown(self):
        """Clean up the collection."""
        self.vector_memory.client.delete_collection(name=self.collection_name)
        del self.vector_memory

    def test_add_and_search_memory(self):
        """Test that a memory can be added and then retrieved."""
        memory_text = "Maya learned that the user's favorite color is blue."
        self.vector_memory.add_memory(memory_text)

        # Search for a relevant query
        search_results = self.vector_memory.search_memory("what is the user's favorite color?")

        self.assertEqual(len(search_results), 1)
        self.assertEqual(search_results[0], memory_text)

    def test_search_no_results(self):
        """Test that searching for an irrelevant topic yields no results."""
        memory_text = "Maya played Minecraft and built a house."
        self.vector_memory.add_memory(memory_text)

        # Search for an irrelevant query
        search_results = self.vector_memory.search_memory("what is the capital of France?")

        self.assertEqual(len(search_results), 0)

    def test_add_multiple_memories(self):
        """Test adding multiple memories and retrieving the most relevant one."""
        memories = [
            "The user's name is Alex.",
            "Maya's creator is named originsbharat.",
            "The user likes dogs."
        ]
        for memory in memories:
            self.vector_memory.add_memory(memory)

        search_results = self.vector_memory.search_memory("who created maya?")
        self.assertEqual(len(search_results), 1)
        self.assertIn("originsbharat", search_results[0])

if __name__ == '__main__':
    unittest.main()