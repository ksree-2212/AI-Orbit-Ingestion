"""
Deterministic UUID generator for AI Orbit entities and relationships.
Ensures stable, idempotent identifiers across pipeline runs.
"""

import uuid
from typing import Optional

# AI Orbit Base Namespace (UUIDv5 namespace)
AI_ORBIT_NAMESPACE = uuid.UUID("a1000000-0000-0000-0000-000000000001")


def generate_entity_id(entity_type: str, canonical_name: str, canonical_url: Optional[str] = None) -> str:
    """
    Generates a deterministic UUIDv5 for an entity.
    Prefers canonical_url if valid, or falls back to lowercase entity_type + canonical_name.
    """
    clean_type = entity_type.strip().lower()
    clean_name = canonical_name.strip().lower()
    
    # Use normalized seed key
    if canonical_url and canonical_url.strip() and canonical_url.startswith("http"):
        seed = f"{clean_type}::{canonical_url.strip().lower()}"
    else:
        seed = f"{clean_type}::{clean_name}"
        
    return str(uuid.uuid5(AI_ORBIT_NAMESPACE, seed))


def generate_relationship_id(source_id: str, relationship_type: str, target_id: str) -> str:
    """
    Generates a deterministic UUIDv5 for a relationship edge.
    """
    seed = f"{source_id}->{relationship_type.upper()}->{target_id}"
    return str(uuid.uuid5(AI_ORBIT_NAMESPACE, seed))
