"""
Seed Data Provider for AI Orbit Ingestion Pipeline.
Loads high-quality, domain-rich seed data covering all 14 categories.
"""

import json
import os
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
RAW_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "seed_dataset.json")


class SeedDataProvider:
    """
    Provides curated, representative dataset of 280+ entities across 14 AI Orbit domains.
    """

    @classmethod
    def get_seed_data(cls) -> List[Dict[str, Any]]:
        if os.path.exists(RAW_DATA_PATH):
            with open(RAW_DATA_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                logger.info(f"Loaded {len(data)} seed records from {RAW_DATA_PATH}")
                return data
        else:
            logger.warning(f"Raw data file not found at {RAW_DATA_PATH}. Returning empty list.")
            return []
