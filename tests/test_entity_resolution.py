"""Unit tests for EntityResolver."""

import unittest
from src.transformers.entity_resolution import EntityResolver
from src.models.schemas import EntityType


class TestEntityResolution(unittest.TestCase):
    def setUp(self):
        self.resolver = EntityResolver(fuzzy_threshold=0.88)

    def test_exact_deduplication_and_merging(self):
        record1 = {
            "entity_type": "Company",
            "name": "OpenAI Inc.",
            "description": "Short description of OpenAI.",
            "url": "https://openai.com?utm_source=test",
            "categories": ["llm"],
            "source": {"name": "Test1", "url": "https://test1.com"},
            "founding_year": 2015
        }
        record2 = {
            "entity_type": "Company",
            "name": "Open AI",
            "description": "A much longer and comprehensive description of OpenAI AI lab.",
            "url": "https://openai.com",
            "categories": ["generative ai", "ai safety"],
            "source": {"name": "Test2", "url": "https://test2.com"},
            "headquarters": "San Francisco, CA"
        }

        e1, is_new1 = self.resolver.register_entity(record1)
        self.assertTrue(is_new1)
        self.assertEqual(e1.name, "OpenAI")

        e2, is_new2 = self.resolver.register_entity(record2)
        self.assertFalse(is_new2)
        self.assertEqual(e1.id, e2.id)
        # Verify longest description preserved
        self.assertIn("much longer and comprehensive", e1.description)
        # Verify category union
        self.assertTrue(len(e1.categories) >= 2)

    def test_uuid_stability(self):
        from src.utils.uuid_generator import generate_entity_id
        id1 = generate_entity_id("Model", "Claude 3.5 Sonnet", "https://anthropic.com/claude")
        id2 = generate_entity_id("Model", "Claude 3.5 Sonnet", "https://anthropic.com/claude")
        self.assertEqual(id1, id2)


if __name__ == "__main__":
    unittest.main()
