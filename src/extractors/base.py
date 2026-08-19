"""
Base Extractor Class.
Defines the standard interface for multi-source extractors in AI Orbit.
"""

import abc
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class BaseExtractor(abc.ABC):
    """
    Abstract Base Class for data source extractors.
    """

    def __init__(self, name: str, source_url: str):
        self.name = name
        self.source_url = source_url

    @abc.abstractmethod
    def extract(self) -> List[Dict[str, Any]]:
        """
        Extracts raw entity records from the source.
        Returns a list of raw dictionaries conforming to source schemas.
        """
        pass

    def log_extraction_summary(self, count: int):
        logger.info(f"Extractor [{self.name}] successfully extracted {count} records from {self.source_url}")
