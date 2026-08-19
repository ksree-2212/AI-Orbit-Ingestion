"""
Data Validation Engine.
Validates entity schemas, referential integrity of graph relationships,
and computes quality metrics according to Section 3 & 4 of the AI Orbit specification.
"""

import uuid
import logging
from urllib.parse import urlparse
from typing import List, Dict, Any, Tuple, Set
from ..models.schemas import BaseEntity, Relationship, EntityType, RelationshipType, PipelineStats
from ..utils.uuid_generator import generate_entity_id, generate_relationship_id

logger = logging.getLogger(__name__)


class DataValidator:
    """
    Performs comprehensive schema and graph integrity checks on AI Orbit dataset.
    """

    @classmethod
    def validate_uuid(cls, val: str) -> bool:
        """Verifies if a string is a valid UUID."""
        try:
            uuid.UUID(str(val))
            return True
        except ValueError:
            return False

    @classmethod
    def validate_url(cls, val: str) -> bool:
        """Verifies if a string is a valid HTTP/HTTPS URL."""
        if not val or not isinstance(val, str):
            return False
        try:
            parsed = urlparse(val)
            return bool(parsed.scheme in ("http", "https") and parsed.netloc)
        except Exception:
            return False

    @classmethod
    def validate_entity(cls, entity: BaseEntity) -> List[str]:
        """
        Validates an entity against the Common Entity Schema standards (Section 4.1).
        Returns a list of error descriptions (empty if valid).
        """
        errors = []

        # 1. UUID Check
        if not entity.id or not cls.validate_uuid(entity.id):
            errors.append(f"Entity '{entity.name}' has invalid UUID id: {entity.id}")

        # 2. Required Fields
        if not entity.name or not entity.name.strip():
            errors.append("Entity missing required field 'name'")

        if not entity.description or len(entity.description.strip()) < 5:
            errors.append(f"Entity '{entity.name}' has missing or too short description")

        if not entity.url or not cls.validate_url(entity.url):
            errors.append(f"Entity '{entity.name}' has invalid URL: {entity.url}")

        if not entity.categories or not isinstance(entity.categories, list) or len(entity.categories) == 0:
            errors.append(f"Entity '{entity.name}' missing categories list")

        if not entity.source or not entity.source.name or not entity.source.url:
            errors.append(f"Entity '{entity.name}' has invalid source attribution")

        # 3. Entity Type validation
        if not entity.entity_type or entity.entity_type not in EntityType:
            errors.append(f"Entity '{entity.name}' has unrecognized entity_type: {entity.entity_type}")

        return errors

    @classmethod
    def validate_relationship(
        cls, rel: Relationship, valid_entity_ids: Set[str]
    ) -> List[str]:
        """
        Validates referential integrity and structure of a relationship edge.
        """
        errors = []

        if not rel.id or not cls.validate_uuid(rel.id):
            errors.append(f"Relationship {rel.source_name} -> {rel.target_name} has invalid UUID")

        if rel.source_id not in valid_entity_ids:
            errors.append(f"Relationship source_id '{rel.source_id}' ({rel.source_name}) does not exist in entity registry")

        if rel.target_id not in valid_entity_ids:
            errors.append(f"Relationship target_id '{rel.target_id}' ({rel.target_name}) does not exist in entity registry")

        if rel.source_id == rel.target_id:
            errors.append(f"Relationship has identical source and target (self-loop): {rel.source_id}")

        if not rel.relationship_type or rel.relationship_type not in RelationshipType:
            errors.append(f"Invalid relationship_type: {rel.relationship_type}")

        return errors

    @classmethod
    def validate_dataset(
        cls, entities: List[BaseEntity], relationships: List[Relationship]
    ) -> Tuple[bool, List[str], List[str], PipelineStats]:
        """
        Runs complete validation suite over entities and relationships.
        Returns: (is_passed, errors_list, warnings_list, pipeline_stats)
        """
        errors: List[str] = []
        warnings: List[str] = []
        entity_id_set: Set[str] = set()

        # Group entities by category
        by_category: Dict[str, int] = {}
        for et in EntityType:
            by_category[et.value] = 0

        # Validate each entity
        for entity in entities:
            e_errors = cls.validate_entity(entity)
            if e_errors:
                errors.extend(e_errors)
            
            if entity.id in entity_id_set:
                errors.append(f"Duplicate entity ID detected in dataset: {entity.id} ({entity.name})")
            entity_id_set.add(entity.id)

            # Tally category
            cat_key = entity.entity_type.value if hasattr(entity.entity_type, "value") else str(entity.entity_type)
            by_category[cat_key] = by_category.get(cat_key, 0) + 1

        # Check total record count against target scope (250-300 records)
        total_records = len(entities)
        if total_records < 250:
            warnings.append(f"Dataset count ({total_records}) is below the recommended 250-300 records.")
        elif total_records > 320:
            warnings.append(f"Dataset count ({total_records}) exceeds the target 250-300 records.")

        # Check category representation
        for cat_name, count in by_category.items():
            if count == 0 and cat_name != EntityType.RECENTLY_ADDED.value:
                warnings.append(f"Category '{cat_name}' has 0 records.")

        # Validate relationships
        rel_by_type: Dict[str, int] = {}
        for r_type in RelationshipType:
            rel_by_type[r_type.value] = 0

        for rel in relationships:
            r_errors = cls.validate_relationship(rel, entity_id_set)
            if r_errors:
                errors.extend(r_errors)

            rtype_key = rel.relationship_type.value if hasattr(rel.relationship_type, "value") else str(rel.relationship_type)
            rel_by_type[rtype_key] = rel_by_type.get(rtype_key, 0) + 1

        # Calculate relationship density
        density = (len(relationships) / total_records) if total_records > 0 else 0.0

        # Calculate data quality score (0 to 100)
        quality_score = 100.0
        if errors:
            quality_score = max(0.0, 100.0 - (len(errors) * 5.0))
        if warnings:
            quality_score = max(0.0, quality_score - (len(warnings) * 1.5))

        stats = PipelineStats(
            total_raw_records=total_records,
            total_entities_processed=total_records,
            total_unique_entities=total_records,
            entities_by_category=by_category,
            total_relationships=len(relationships),
            relationships_by_type=rel_by_type,
            validation_status="PASS" if len(errors) == 0 else "FAIL",
            validation_errors_count=len(errors),
            validation_warnings_count=len(warnings),
            relationship_density=round(density, 2),
            quality_score=round(quality_score, 2),
        )

        is_passed = (len(errors) == 0)
        return is_passed, errors, warnings, stats
