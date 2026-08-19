"""
AI Orbit Data Ingestion Pipeline Orchestrator.
Executes the modular workflow:
Discovery -> Extraction -> Cleaning -> Normalization -> Deduplication -> Classification -> Relationship Mapping -> Validation -> Export.
"""

import os
import json
import logging
from typing import List, Dict, Any, Tuple, Optional

from .models.schemas import BaseEntity, Relationship, EntityType, RelationshipType, PipelineStats
from .transformers.cleaner import DataCleaner
from .transformers.normalizer import DataNormalizer
from .transformers.entity_resolution import EntityResolver
from .transformers.classifier import DataClassifier
from .transformers.relationship_mapper import RelationshipExtractor
from .validators.validator import DataValidator
from .extractors.seed_data_provider import SeedDataProvider

logger = logging.getLogger("ai_orbit.pipeline")


class DataIngestionPipeline:
    """
    Production-grade bulk data ingestion pipeline for the AI Orbit ecosystem.
    """

    def __init__(self, output_dir: Optional[str] = None, fuzzy_threshold: float = 0.88):
        self.fuzzy_threshold = fuzzy_threshold
        if output_dir:
            self.output_dir = output_dir
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.output_dir = os.path.join(base_dir, "data", "processed")

        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "by_category"), exist_ok=True)

        self.resolver = EntityResolver(fuzzy_threshold=self.fuzzy_threshold)
        self.relationship_extractor = RelationshipExtractor(self.resolver)
        self.entities: List[BaseEntity] = []
        self.relationships: List[Relationship] = []
        self.stats: Optional[PipelineStats] = None

    def step_1_extract(self, additional_records: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Extracts raw records from seed data and optional supplementary live feeds.
        """
        logger.info("--- Step 1: Multi-Source Extraction & Discovery ---")
        raw_records = SeedDataProvider.get_seed_data()
        if additional_records:
            raw_records.extend(additional_records)
            logger.info(f"Appended {len(additional_records)} additional records to raw extraction batch.")

        logger.info(f"Extracted {len(raw_records)} total raw records.")
        return raw_records

    def step_2_clean(self, raw_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sanitizes text fields, removes HTML/RSS markup and boilerplate.
        """
        logger.info("--- Step 2: Data Cleaning & Sanitization ---")
        cleaned_records = []
        for rec in raw_records:
            cleaned = DataCleaner.sanitize_entity_dict(rec)
            cleaned_records.append(cleaned)
        logger.info(f"Cleaned and sanitized {len(cleaned_records)} records.")
        return cleaned_records

    def step_3_normalize_and_resolve(self, cleaned_records: List[Dict[str, Any]]) -> Tuple[List[BaseEntity], int]:
        """
        Normalizes URLs, canonicalizes entity names, and performs multi-stage entity resolution.
        """
        logger.info("--- Step 3 & 4: Normalization & Entity Resolution ---")
        resolved_entities, duplicate_count = self.resolver.resolve_all(cleaned_records)
        logger.info(f"Resolved {len(resolved_entities)} unique canonical entities. Merged {duplicate_count} duplicate records.")
        return resolved_entities, duplicate_count

    def step_5_classify_and_enrich(self, entities: List[BaseEntity]) -> List[BaseEntity]:
        """
        Classifies modalities, licenses, and enriches metadata.
        """
        logger.info("--- Step 5: Classification & Metadata Enrichment ---")
        enriched = []
        for entity in entities:
            e = DataClassifier.enrich_entity(entity)
            enriched.append(e)
        return enriched

    def step_6_extract_relationships(self) -> List[Relationship]:
        """
        Extracts structural and semantic relationships across the AI ecosystem.
        """
        logger.info("--- Step 6: Relationship Extraction & Graph Mapping ---")
        relationships = self.relationship_extractor.extract_all()
        logger.info(f"Extracted {len(relationships)} graph relationships.")
        return relationships

    def step_7_validate(
        self, entities: List[BaseEntity], relationships: List[Relationship], duplicate_count: int
    ) -> Tuple[bool, List[str], List[str], PipelineStats]:
        """
        Validates entity schemas, referential integrity, and quality metrics.
        """
        logger.info("--- Step 7: Schema & Graph Referential Integrity Validation ---")
        is_passed, errors, warnings, stats = DataValidator.validate_dataset(entities, relationships)
        stats.deduplicated_count = duplicate_count
        self.stats = stats

        if errors:
            logger.error(f"Validation FAILED with {len(errors)} errors:")
            for err in errors[:10]:
                logger.error(f"  - {err}")
        else:
            logger.info("Validation PASSED flawlessly with 0 schema or integrity errors.")

        if warnings:
            logger.warning(f"Validation generated {len(warnings)} warnings:")
            for warn in warnings:
                logger.warning(f"  - {warn}")

        return is_passed, errors, warnings, stats

    def step_8_export(
        self, entities: List[BaseEntity], relationships: List[Relationship], stats: PipelineStats
    ) -> Dict[str, str]:
        """
        Exports final JSON datasets and summary statistics to disk.
        """
        logger.info("--- Step 8: Dataset Serialization & Export ---")
        exported_files = {}

        # 1. Master Entities JSON
        entities_path = os.path.join(self.output_dir, "entities.json")
        entities_dicts = [json.loads(e.json()) for e in entities]
        with open(entities_path, "w", encoding="utf-8") as f:
            json.dump(entities_dicts, f, indent=2)
        exported_files["entities"] = entities_path

        # 2. Master Relationships JSON (Section 5)
        relationships_path = os.path.join(self.output_dir, "relationships.json")
        rel_dicts = [json.loads(r.json()) for r in relationships]
        with open(relationships_path, "w", encoding="utf-8") as f:
            json.dump(rel_dicts, f, indent=2)
        exported_files["relationships"] = relationships_path

        # 3. Category Split Files
        by_category_dir = os.path.join(self.output_dir, "by_category")
        category_map = {
            "Tool": "tools.json",
            "Task": "tasks.json",
            "Company": "companies.json",
            "News": "news.json",
            "Video": "videos.json",
            "Robot": "robots.json",
            "Device": "devices.json",
            "Model": "models.json",
            "Repository": "repositories.json",
            "MCP": "mcp.json",
            "Collection": "collections.json",
            "Personal": "personal.json",
            "Creative": "creative.json",
        }

        for cat_type, filename in category_map.items():
            cat_entities = [
                json.loads(e.json()) for e in entities
                if (e.entity_type.value if hasattr(e.entity_type, "value") else str(e.entity_type)) == cat_type
            ]
            cat_path = os.path.join(by_category_dir, filename)
            with open(cat_path, "w", encoding="utf-8") as f:
                json.dump(cat_entities, f, indent=2)

        # 4. Recently Added View (Section 3)
        recently_added_path = os.path.join(self.output_dir, "recently_added.json")
        # Select latest entities across cutting-edge categories
        recent_candidates = [
            json.loads(e.json()) for e in entities
            if e.entity_type in (
                EntityType.MODEL, EntityType.TOOL, EntityType.ROBOT, EntityType.MCP, EntityType.NEWS, EntityType.CREATIVE
            )
        ]
        # Sort and take top 25 recent items
        recent_items = recent_candidates[:25]
        with open(recently_added_path, "w", encoding="utf-8") as f:
            json.dump(recent_items, f, indent=2)
        exported_files["recently_added"] = recently_added_path

        # 5. Pipeline Execution Summary
        summary_path = os.path.join(self.output_dir, "pipeline_summary.json")
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(json.loads(stats.json()), f, indent=2)
        exported_files["summary"] = summary_path

        # 6. Graph Topology Metrics
        graph_metrics = self._calculate_graph_metrics(entities, relationships)
        graph_metrics_path = os.path.join(self.output_dir, "graph_metrics.json")
        with open(graph_metrics_path, "w", encoding="utf-8") as f:
            json.dump(graph_metrics, f, indent=2)
        exported_files["graph_metrics"] = graph_metrics_path

        logger.info(f"Exported all datasets successfully to: {self.output_dir}")
        return exported_files

    def _calculate_graph_metrics(
        self, entities: List[BaseEntity], relationships: List[Relationship]
    ) -> Dict[str, Any]:
        """Calculates in-degree, out-degree, and top hub entities."""
        node_degrees: Dict[str, Dict[str, Any]] = {}
        for e in entities:
            node_degrees[e.id] = {
                "name": e.name,
                "type": e.entity_type.value if hasattr(e.entity_type, "value") else str(e.entity_type),
                "in_degree": 0,
                "out_degree": 0,
                "total_degree": 0
            }

        for r in relationships:
            if r.source_id in node_degrees:
                node_degrees[r.source_id]["out_degree"] += 1
                node_degrees[r.source_id]["total_degree"] += 1
            if r.target_id in node_degrees:
                node_degrees[r.target_id]["in_degree"] += 1
                node_degrees[r.target_id]["total_degree"] += 1

        top_hubs = sorted(node_degrees.values(), key=lambda x: x["total_degree"], reverse=True)[:15]

        return {
            "total_nodes": len(entities),
            "total_edges": len(relationships),
            "average_degree": round((len(relationships) * 2) / len(entities), 2) if entities else 0.0,
            "top_connected_hubs": top_hubs
        }

    def run(self, additional_records: Optional[List[Dict[str, Any]]] = None) -> PipelineStats:
        """
        Executes the entire end-to-end ingestion pipeline.
        """
        raw = self.step_1_extract(additional_records)
        cleaned = self.step_2_clean(raw)
        resolved, dup_count = self.step_3_normalize_and_resolve(cleaned)
        enriched = self.step_5_classify_and_enrich(resolved)
        self.entities = enriched

        rels = self.step_6_extract_relationships()
        self.relationships = rels

        is_passed, errors, warnings, stats = self.step_7_validate(enriched, rels, dup_count)
        self.step_8_export(enriched, rels, stats)

        return stats
