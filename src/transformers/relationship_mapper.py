"""
Relationship Extraction & Graph Mapping Engine.
Discovers and extracts interconnected relationships across the AI ecosystem
to generate relationships.json according to Section 5 of the AI Orbit specification.
"""

import logging
import re
from typing import List, Dict, Any, Optional, Set, Tuple
from ..models.schemas import BaseEntity, EntityType, Relationship, RelationshipType
from ..utils.uuid_generator import generate_relationship_id
from .entity_resolution import EntityResolver

logger = logging.getLogger(__name__)


class RelationshipExtractor:
    """
    Extracts semantic and structural relationships between entities in the AI Orbit ecosystem.
    Ensures referential integrity across the entire graph.
    """

    def __init__(self, resolver: EntityResolver):
        self.resolver = resolver
        # Map of entity_id -> BaseEntity
        self.entities_by_id: Dict[str, BaseEntity] = resolver.entities_by_id
        self.relationships: Dict[str, Relationship] = {}

    def add_relationship(
        self,
        source_id: str,
        rel_type: RelationshipType,
        target_id: str,
        description: str,
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Relationship]:
        """
        Safely creates and registers a relationship edge between two existing entities.
        Validates referential integrity (both source and target must exist in registry).
        """
        if not source_id or not target_id or source_id == target_id:
            return None

        source_entity = self.entities_by_id.get(source_id)
        target_entity = self.entities_by_id.get(target_id)

        if not source_entity or not target_entity:
            logger.debug(f"Skipping relationship {source_id} -> {rel_type} -> {target_id}: entity not found in index")
            return None

        rel_id = generate_relationship_id(source_id, rel_type.value, target_id)

        rel = Relationship(
            id=rel_id,
            source_id=source_id,
            source_name=source_entity.name,
            source_type=source_entity.entity_type,
            relationship_type=rel_type,
            target_id=target_id,
            target_name=target_entity.name,
            target_type=target_entity.entity_type,
            description=description,
            confidence=confidence,
            metadata=metadata or {},
        )

        self.relationships[rel_id] = rel
        return rel

    def extract_from_metadata(self, entity: BaseEntity):
        """
        Extracts structural relationships directly from specialized entity fields.
        """
        meta = entity.metadata or {}
        e_id = entity.id
        e_name = entity.name
        e_type = entity.entity_type

        # 1. Company Develops / Developed By
        # Check provider/manufacturer/vendor/creator/author
        org_names = []
        if hasattr(entity, "provider") and getattr(entity, "provider"):
            org_names.append(getattr(entity, "provider"))
        if hasattr(entity, "manufacturer") and getattr(entity, "manufacturer"):
            org_names.append(getattr(entity, "manufacturer"))
        if hasattr(entity, "vendor") and getattr(entity, "vendor"):
            org_names.append(getattr(entity, "vendor"))
        if "provider" in meta:
            org_names.append(meta["provider"])
        if "manufacturer" in meta:
            org_names.append(meta["manufacturer"])
        if "company" in meta:
            org_names.append(meta["company"])
        if "developer" in meta:
            org_names.append(meta["developer"])

        for org_name in org_names:
            company_id = self.resolver.resolve_name_to_id(str(org_name), expected_type=EntityType.COMPANY)
            if company_id:
                # Entity DEVELOPED_BY Company
                self.add_relationship(
                    source_id=e_id,
                    rel_type=RelationshipType.DEVELOPED_BY,
                    target_id=company_id,
                    description=f"{e_name} was developed/built by {org_name}",
                    confidence=1.0,
                    metadata={"source_field": "provider_or_manufacturer"}
                )

        # 2. Tool / Personal / Creative POWERED_BY Model
        if "powered_by_model" in meta or "base_model" in meta or "underlying_model" in meta:
            model_names = [meta.get("powered_by_model"), meta.get("base_model"), meta.get("underlying_model")]
            for m_name in model_names:
                if m_name:
                    model_id = self.resolver.resolve_name_to_id(str(m_name), expected_type=EntityType.MODEL)
                    if model_id:
                        # Model POWERS Tool
                        self.add_relationship(
                            source_id=model_id,
                            rel_type=RelationshipType.POWERS,
                            target_id=e_id,
                            description=f"{m_name} powers the AI functionality of {e_name}",
                            confidence=0.98,
                            metadata={"source_field": "powered_by_model"}
                        )

        # 3. Tool SOLVES_TASK Task
        if "solved_tasks" in meta and isinstance(meta["solved_tasks"], list):
            for task_name in meta["solved_tasks"]:
                task_id = self.resolver.resolve_name_to_id(str(task_name), expected_type=EntityType.TASK)
                if task_id:
                    self.add_relationship(
                        source_id=e_id,
                        rel_type=RelationshipType.SOLVES_TASK,
                        target_id=task_id,
                        description=f"{e_name} assists users in performing {task_name}",
                        confidence=0.95,
                    )

        # 4. MCP INTEGRATES_WITH Tool
        if e_type == EntityType.MCP:
            compatible = meta.get("compatible_clients", [])
            if hasattr(entity, "compatible_clients") and getattr(entity, "compatible_clients"):
                compatible += getattr(entity, "compatible_clients")
            for client_name in compatible:
                client_id = self.resolver.resolve_name_to_id(str(client_name), expected_type=EntityType.TOOL)
                if client_id:
                    self.add_relationship(
                        source_id=e_id,
                        rel_type=RelationshipType.INTEGRATES_WITH,
                        target_id=client_id,
                        description=f"MCP server {e_name} integrates directly with {client_name}",
                        confidence=1.0,
                    )

        # 5. Device RUNS Model
        if e_type == EntityType.DEVICE and "supported_models" in meta:
            for m_name in meta.get("supported_models", []):
                model_id = self.resolver.resolve_name_to_id(str(m_name), expected_type=EntityType.MODEL)
                if model_id:
                    self.add_relationship(
                        source_id=e_id,
                        rel_type=RelationshipType.RUNS,
                        target_id=model_id,
                        description=f"{e_name} provides specialized hardware acceleration to run {m_name}",
                        confidence=0.95,
                    )

        # 6. Repository IMPLEMENTS Model / Tool / MCP
        if e_type == EntityType.REPOSITORY:
            target_impl = meta.get("implements_entity") or meta.get("target_entity")
            if target_impl:
                target_id = self.resolver.resolve_name_to_id(str(target_impl))
                if target_id:
                    self.add_relationship(
                        source_id=e_id,
                        rel_type=RelationshipType.IMPLEMENTS,
                        target_id=target_id,
                        description=f"Repository {e_name} contains the core source code for {target_impl}",
                        confidence=1.0,
                    )

        # 7. Collection CONTAINS Entities
        if e_type == EntityType.COLLECTION:
            items = meta.get("item_references", [])
            if hasattr(entity, "item_references") and getattr(entity, "item_references"):
                items += getattr(entity, "item_references")
            for item_name in items:
                item_id = self.resolver.resolve_name_to_id(str(item_name))
                if item_id:
                    self.add_relationship(
                        source_id=e_id,
                        rel_type=RelationshipType.CONTAINS,
                        target_id=item_id,
                        description=f"Curated collection {e_name} features {item_name}",
                        confidence=1.0,
                    )

        # 8. Video REVIEWS / DEMOS Entity
        if e_type == EntityType.VIDEO:
            subject = meta.get("featured_entity") or meta.get("subject")
            if subject:
                target_id = self.resolver.resolve_name_to_id(str(subject))
                if target_id:
                    self.add_relationship(
                        source_id=e_id,
                        rel_type=RelationshipType.REVIEWS,
                        target_id=target_id,
                        description=f"Video '{e_name}' demos and reviews {subject}",
                        confidence=0.95,
                    )

        # 9. News COVERS Entity
        if e_type == EntityType.NEWS:
            topics = meta.get("covered_entities", [])
            if isinstance(topics, list):
                for topic_entity in topics:
                    target_id = self.resolver.resolve_name_to_id(str(topic_entity))
                    if target_id:
                        self.add_relationship(
                            source_id=e_id,
                            rel_type=RelationshipType.COVERS,
                            target_id=target_id,
                            description=f"News article reports key developments on {topic_entity}",
                            confidence=0.95,
                        )

    def extract_semantic_mentions(self):
        """
        Performs entity linking across descriptions to extract high-confidence semantic relationships.
        """
        # Pre-build lookup of prominent entities
        prominent_entities: List[Tuple[str, str, EntityType]] = []
        for eid, entity in self.entities_by_id.items():
            if len(entity.name) >= 3 and entity.entity_type in (
                EntityType.COMPANY, EntityType.MODEL, EntityType.TOOL, EntityType.ROBOT, EntityType.DEVICE, EntityType.TASK
            ):
                prominent_entities.append((eid, entity.name, entity.entity_type))

        for eid, entity in self.entities_by_id.items():
            desc_lower = (entity.description or "").lower()

            for target_id, target_name, target_type in prominent_entities:
                if target_id == eid:
                    continue

                # Regex word boundary match
                pattern = r"\b" + re.escape(target_name.lower()) + r"\b"
                if re.search(pattern, desc_lower):
                    # Determine appropriate relationship based on types
                    if entity.entity_type == EntityType.TOOL and target_type == EntityType.MODEL:
                        self.add_relationship(
                            source_id=target_id,
                            rel_type=RelationshipType.POWERS,
                            target_id=eid,
                            description=f"{target_name} powers features in {entity.name}",
                            confidence=0.90,
                            metadata={"method": "text_entity_linking"}
                        )
                    elif entity.entity_type in (EntityType.MODEL, EntityType.TOOL, EntityType.ROBOT, EntityType.DEVICE) and target_type == EntityType.COMPANY:
                        self.add_relationship(
                            source_id=eid,
                            rel_type=RelationshipType.DEVELOPED_BY,
                            target_id=target_id,
                            description=f"{entity.name} is associated with / developed by {target_name}",
                            confidence=0.90,
                            metadata={"method": "text_entity_linking"}
                        )
                    elif entity.entity_type == EntityType.TOOL and target_type == EntityType.TASK:
                        self.add_relationship(
                            source_id=eid,
                            rel_type=RelationshipType.SOLVES_TASK,
                            target_id=target_id,
                            description=f"{entity.name} is used to accomplish {target_name}",
                            confidence=0.88,
                            metadata={"method": "text_entity_linking"}
                        )
                    elif entity.entity_type == EntityType.NEWS and target_type in (EntityType.COMPANY, EntityType.MODEL, EntityType.TOOL, EntityType.ROBOT):
                        self.add_relationship(
                            source_id=eid,
                            rel_type=RelationshipType.COVERS,
                            target_id=target_id,
                            description=f"News announcement covers {target_name}",
                            confidence=0.92,
                            metadata={"method": "text_entity_linking"}
                        )

    def extract_all(self) -> List[Relationship]:
        """
        Executes full relationship extraction pipeline across metadata and text mentions.
        Returns validated list of Relationship objects.
        """
        # Step 1: Metadata extraction
        for entity in self.entities_by_id.values():
            self.extract_from_metadata(entity)

        # Step 2: Semantic text mention linking
        self.extract_semantic_mentions()

        logger.info(f"Extracted {len(self.relationships)} high-confidence graph relationships.")
        return list(self.relationships.values())
