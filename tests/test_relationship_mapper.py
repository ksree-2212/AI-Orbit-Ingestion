"""Unit tests for RelationshipExtractor."""

import unittest
from src.transformers.entity_resolution import EntityResolver
from src.transformers.relationship_mapper import RelationshipExtractor
from src.models.schemas import RelationshipType, EntityType


class TestRelationshipMapper(unittest.TestCase):
    def setUp(self):
        self.resolver = EntityResolver()
        self.company, _ = self.resolver.register_entity({
            "entity_type": "Company",
            "name": "Anthropic",
            "description": "AI safety company.",
            "url": "https://anthropic.com",
            "categories": ["Generative AI"],
            "source": {"name": "Web", "url": "https://anthropic.com"}
        })
        self.model, _ = self.resolver.register_entity({
            "entity_type": "Model",
            "name": "Claude 3.5 Sonnet",
            "description": "Frontier model developed by Anthropic.",
            "url": "https://anthropic.com/claude",
            "categories": ["Large Language Models"],
            "source": {"name": "Web", "url": "https://anthropic.com"},
            "provider": "Anthropic"
        })
        self.extractor = RelationshipExtractor(self.resolver)

    def test_developed_by_relationship(self):
        rels = self.extractor.extract_all()
        dev_rels = [r for r in rels if r.relationship_type == RelationshipType.DEVELOPED_BY]
        self.assertTrue(len(dev_rels) >= 1)
        rel = dev_rels[0]
        self.assertEqual(rel.source_id, self.model.id)
        self.assertEqual(rel.target_id, self.company.id)


if __name__ == "__main__":
    unittest.main()
