"""
Data Cleaning and Sanitization Engine.
Cleans raw text extracted from HTML, RSS feeds, API snippets, and markdown.
"""

import re
import html
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup


class DataCleaner:
    """
    Sanitizes raw text strings, removes HTML/RSS markup, and normalizes encodings.
    """

    # Boilerplate patterns to remove from descriptions
    BOILERPLATE_PATTERNS = [
        re.compile(r"^\s*(official website|read more|click here to learn more|learn more at)[:\s-]*", re.IGNORECASE),
        re.compile(r"subscribe to our (channel|newsletter|youtube|updates)[^.\n]*[.\n]?", re.IGNORECASE),
        re.compile(r"all rights reserved\b.*$", re.IGNORECASE),
        re.compile(r"cookie policy|privacy policy|terms of service", re.IGNORECASE),
        re.compile(r"follow us on (twitter|x|linkedin|github|discord)[^.\n]*[.\n]?", re.IGNORECASE),
    ]

    @classmethod
    def clean_text(cls, text: Optional[str], max_length: Optional[int] = None) -> str:
        """
        Cleans and sanitizes a text string:
        - Unescapes HTML entities
        - Strips HTML tags
        - Removes control characters and excess whitespace
        - Removes common marketing / subscription boilerplate
        """
        if not text:
            return ""

        # Unescape HTML entities
        cleaned = html.unescape(str(text))

        # Strip HTML tags if HTML is present
        if "<" in cleaned and ">" in cleaned:
            try:
                soup = BeautifulSoup(cleaned, "html.parser")
                cleaned = soup.get_text(separator=" ")
            except Exception:
                cleaned = re.sub(r"<[^>]+>", " ", cleaned)

        # Remove control characters (except newline)
        cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", cleaned)

        # Clean markdown link syntax [text](url) -> text
        cleaned = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", cleaned)

        # Clean markdown bold/italics
        cleaned = re.sub(r"[*_`#~]", "", cleaned)

        # Remove boilerplate patterns
        for pattern in cls.BOILERPLATE_PATTERNS:
            cleaned = pattern.sub("", cleaned)

        # Normalize whitespace
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        if max_length and len(cleaned) > max_length:
            # Cut at word boundary
            truncated = cleaned[:max_length]
            last_space = truncated.rfind(" ")
            if last_space > 0:
                cleaned = truncated[:last_space].rstrip(".,;:- ") + "..."
            else:
                cleaned = truncated.rstrip(".,;:- ") + "..."

        return cleaned

    @classmethod
    def sanitize_entity_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Applies text sanitization to all textual fields in an entity dictionary.
        """
        sanitized = data.copy()
        
        if "name" in sanitized and sanitized["name"]:
            sanitized["name"] = cls.clean_text(sanitized["name"])
            
        if "description" in sanitized and sanitized["description"]:
            sanitized["description"] = cls.clean_text(sanitized["description"])
            
        if "summary" in sanitized and sanitized["summary"]:
            sanitized["summary"] = cls.clean_text(sanitized["summary"])

        # Clean categories / tags
        if "categories" in sanitized and isinstance(sanitized["categories"], list):
            sanitized["categories"] = [
                cls.clean_text(cat) for cat in sanitized["categories"] if cat and cls.clean_text(cat)
            ]

        # Clean metadata strings
        if "metadata" in sanitized and isinstance(sanitized["metadata"], dict):
            clean_meta = {}
            for k, v in sanitized["metadata"].items():
                if isinstance(v, str):
                    clean_meta[k] = cls.clean_text(v)
                else:
                    clean_meta[k] = v
            sanitized["metadata"] = clean_meta

        return sanitized
