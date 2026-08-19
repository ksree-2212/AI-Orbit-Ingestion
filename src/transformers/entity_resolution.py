"""
Entity Resolution & Deduplication Engine.
Implements multi-stage entity resolution, fuzzy duplicate detection,
and intelligent attribute merging for high data integrity.
"""

import difflib
import logging
from typing import List, Dict, Any, Tuple, Optional, Set
from ..models.schemas import BaseEntity, EntityType
from ..utils.uuid_generator import generate_entity_id
from .normalizer import DataNormalizer
from .cleaner import DataCleaner

logger = logging.getLogger(__name__)


class EntityResolver:
    """
    Resolves entity variations, removes duplicates, and merges attributes
    to construct canonical master entity records.
    """

    def __init__(self, fuzzy_threshold: float = 0.88):
        self.fuzzy_threshold = fuzzy_threshold
        # Maps canonical entity_id -> Canonical BaseEntity
        self.entities_by_id: Dict[str, BaseEntity] = {}
        # Maps normalized URL -> canonical entity_id
        self.url_index: Dict[str, str] = {}
        # Maps (entity_type, canonical_name_lower) -> canonical entity_id
        self.name_type_index: Dict[Tuple[str, str], str] = {}
        # Maps all known aliases -> canonical entity_id
        self.alias_index: Dict[str, str] = {}

    def _calculate_similarity(self, s1: str, s2: str) -> float:
        """
        Calculates a hybrid similarity score using SequenceMatcher and token set similarity.
        """
        s1_clean = s1.lower().strip()
        s2_clean = s2.lower().strip()

        if s1_clean == s2_clean:
            return 1.0

        # Sequence matcher ratio
        seq_ratio = difflib.SequenceMatcher(None, s1_clean, s2_clean).ratio()

        # Token set similarity (Jaccard on words)
        tokens1 = set(s1_clean.split())
        tokens2 = set(s2_clean.split())
        if tokens1 and tokens2:
            jaccard = len(tokens1 & tokens2) / len(tokens1 | tokens2)
        else:
            jaccard = 0.0

        # Weighted combination favoring token overlap for reordered names
        return max(seq_ratio, 0.5 * seq_ratio + 0.5 * jaccard)

    def find_match(self, entity_data: Dict[str, Any]) -> Optional[str]:
        """
        Checks if an incoming entity record matches an existing canonical entity.
        Returns canonical entity_id if matched, None otherwise.
        """
        entity_type = entity_data.get("entity_type", "")
        name = entity_data.get("name", "")
        url = entity_data.get("url", "")

        canonical_name = DataNormalizer.normalize_name(name)
        canonical_name_lower = canonical_name.lower().strip()
        normalized_url = DataNormalizer.normalize_url(url) if url else ""

        # 1. Exact URL Match (High Precision)
        if normalized_url and normalized_url in self.url_index:
            return self.url_index[normalized_url]

        # 2. Exact (Type, Canonical Name) Match
        type_name_key = (entity_type, canonical_name_lower)
        if type_name_key in self.name_type_index:
            return self.name_type_index[type_name_key]

        # 3. Alias Registry Match
        if canonical_name_lower in self.alias_index:
            return self.alias_index[canonical_name_lower]

        # 4. Fuzzy Name Matching within the same entity type
        for (stored_type, stored_name_lower), existing_id in self.name_type_index.items():
            if stored_type == entity_type:
                sim = self._calculate_similarity(canonical_name_lower, stored_name_lower)
                if sim >= self.fuzzy_threshold:
                    logger.debug(
                        f"Fuzzy match found: '{canonical_name}' matches '{stored_name_lower}' (score: {sim:.3f})"
                    )
                    return existing_id

        return None

    def merge_attributes(self, existing: BaseEntity, new_data: Dict[str, Any]) -> BaseEntity:
        """
        Merges new entity data into an existing canonical entity without data loss.
        """
        # Merge categories (union)
        new_cats = DataNormalizer.normalize_categories(new_data.get("categories", []))
        merged_categories = sorted(list(set(existing.categories + new_cats)))
        existing.categories = merged_categories

        # Preserve longest, most detailed description
        new_desc = DataCleaner.clean_text(new_data.get("description", ""))
        if len(new_desc) > len(existing.description or ""):
            existing.description = new_desc

        # Deep merge metadata
        if "metadata" in new_data and isinstance(new_data["metadata"], dict):
            for k, v in new_data["metadata"].items():
                if v is not None and (k not in existing.metadata or not existing.metadata[k]):
                    existing.metadata[k] = v

        # Merge specialized model fields if available
        for attr in [
            "license", "modalities", "provider", "context_window", "parameter_count",
            "stars", "forks", "primary_language", "last_updated", "topics",
            "installation_methods", "runtime_requirements", "transport", "vendor",
            "founding_year", "industry_sector", "headquarters", "valuation",
            "pricing_model", "platform", "manufacturer", "locomotion_type",
            "chip_processor", "form_factor", "author", "summary", "curator"
        ]:
            if hasattr(existing, attr) and attr in new_data and new_data[attr]:
                existing_val = getattr(existing, attr)
                new_val = new_data[attr]
                if isinstance(existing_val, list) and isinstance(new_val, list):
                    setattr(existing, attr, sorted(list(set(existing_val + new_val))))
                elif not existing_val:
                    setattr(existing, attr, new_val)

        return existing

    def register_entity(self, entity_data: Dict[str, Any]) -> Tuple[BaseEntity, bool]:
        """
        Registers an entity record. If a match is found, merges attributes.
        Otherwise creates and registers a new canonical entity.
        
        Returns: (Canonical BaseEntity, is_new_boolean)
        """
        # Sanitize data
        sanitized = DataCleaner.sanitize_entity_dict(entity_data)

        # Normalize fields
        raw_name = sanitized.get("name", "")
        raw_url = sanitized.get("url", "")
        raw_type = sanitized.get("entity_type", "")

        canonical_name = DataNormalizer.normalize_name(raw_name)
        canonical_url = DataNormalizer.normalize_url(raw_url)
        normalized_categories = DataNormalizer.normalize_categories(sanitized.get("categories", []))

        sanitized["name"] = canonical_name
        sanitized["url"] = canonical_url
        sanitized["categories"] = normalized_categories

        # Check for existing match
        match_id = self.find_match(sanitized)
        if match_id and match_id in self.entities_by_id:
            existing = self.entities_by_id[match_id]
            merged = self.merge_attributes(existing, sanitized)
            
            # Record any new aliases or URLs
            if raw_name:
                self.alias_index[raw_name.lower().strip()] = match_id
            if canonical_url:
                self.url_index[canonical_url] = match_id

            return merged, False

        # Generate deterministic UUID
        stable_id = generate_entity_id(raw_type, canonical_name, canonical_url)
        sanitized["id"] = stable_id

        # Instantiate Entity
        entity = BaseEntity(**sanitized)

        # Register in indices
        self.entities_by_id[stable_id] = entity
        if canonical_url:
            self.url_index[canonical_url] = stable_id
        self.name_type_index[(raw_type, canonical_name.lower().strip())] = stable_id
        if raw_name:
            self.alias_index[raw_name.lower().strip()] = stable_id
        self.alias_index[canonical_name.lower().strip()] = stable_id

        return entity, True

    def resolve_all(self, raw_records: List[Dict[str, Any]]) -> Tuple[List[BaseEntity], int]:
        """
        Processes a batch of raw records, performing deduplication and entity resolution.
        Returns: (List of canonical BaseEntities, duplicate_count)
        """
        duplicate_count = 0
        for record in raw_records:
            _, is_new = self.register_entity(record)
            if not is_new:
                duplicate_count += 1

        resolved_list = list(self.entities_by_id.values())
        return resolved_list, duplicate_count

    def resolve_name_to_id(self, name_or_alias: str, expected_type: Optional[str] = None) -> Optional[str]:
        """
        Helper for relationship extraction: resolves a name or alias to its canonical entity ID.
        """
        if not name_or_alias:
            return None

        clean_name = DataNormalizer.normalize_name(name_or_alias).lower().strip()

        # 1. Check alias index
        if clean_name in self.alias_index:
            return self.alias_index[clean_name]

        # 2. Check (type, name) index
        if expected_type:
            key = (expected_type, clean_name)
            if key in self.name_type_index:
                return self.name_type_index[key]

        # 3. Fuzzy search across all known names
        best_match_id = None
        best_score = 0.0
        for (stored_type, stored_name), eid in self.name_type_index.items():
            if expected_type and stored_type != expected_type:
                continue
            score = self._calculate_similarity(clean_name, stored_name)
            if score > best_score and score >= self.fuzzy_threshold:
                best_score = score
                best_match_id = eid

        return best_match_id
