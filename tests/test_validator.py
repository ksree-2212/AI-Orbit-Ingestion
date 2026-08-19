"""Unit tests for DataValidator."""

import unittest
from src.validators.validator import DataValidator
from src.models.schemas import BaseEntity, Relationship, EntityType, RelationshipType, SourceInfo


class TestDataValidator(unittest.TestCase):
    def test_valid_entity(self):
        entity = BaseEntity(
            id="a1000000-0000-0000-0000-000000000002",
            entity_type=EntityType.TOOL,
            name="Cursor",
            description="AI Code Editor.",
            url="https://cursor.com",
            categories=["Developer Tools"],
            source=SourceInfo(name="Web", url="https://cursor.com")
        )
        errors = DataValidator.validate_entity(entity)
        self.assertEqual(len(errors), 0)

    def test_invalid_entity_url_and_uuid(self):
        entity = BaseEntity(
            id="not-a-uuid",
            entity_type=EntityType.TOOL,
            name="Invalid Tool",
            description="Short",
            url="not_a_url",
            categories=[],
            source=SourceInfo(name="Web", url="invalid")
        )
        errors = DataValidator.validate_entity(entity)
        self.assertTrue(len(errors) >= 3)


if __name__ == "__main__":
    unittest.main()
