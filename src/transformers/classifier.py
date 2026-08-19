"""
Automatic Classification and Tagging Engine.
Enriches entities with domain taxonomy, modality detection, and licensing models.
"""

import re
from typing import List, Dict, Any, Set
from ..models.schemas import BaseEntity, EntityType


class DataClassifier:
    """
    Classifies entities into domain taxonomy, detects input/output modalities,
    and infers technical tags based on entity metadata and textual content.
    """

    MODALITY_KEYWORDS: Dict[str, List[str]] = {
        "text": ["nlp", "text generation", "language model", "chat", "completion", "summarization", "translation"],
        "code": ["code generation", "coding assistant", "programming", "python", "javascript", "compiler", "debugging", "copilot"],
        "vision": ["computer vision", "image generation", "diffusion", "object detection", "ocr", "segmentation", "image-to-image"],
        "video": ["video generation", "text-to-video", "video editing", "video synthesis", "cinematic"],
        "audio": ["speech recognition", "tts", "text-to-speech", "voice synthesis", "audio generation", "music generation", "whisper"],
        "multimodal": ["multimodal", "vision-language", "vlm", "omni", "interleaved text-image", "audio-visual"],
        "embodied": ["robotics", "manipulation", "locomotion", "teleoperation", "actuator", "humanoid", "slam"],
    }

    LICENSE_PATTERNS: Dict[str, re.Pattern] = {
        "Apache-2.0": re.compile(r"\bapache[- ]?2(\.0)?\b", re.IGNORECASE),
        "MIT": re.compile(r"\bmit\b", re.IGNORECASE),
        "GPL-3.0": re.compile(r"\bgpl[- ]?3(\.0)?\b", re.IGNORECASE),
        "BSD-3-Clause": re.compile(r"\bbsd\b", re.IGNORECASE),
        "Llama-Community": re.compile(r"\bllama[- ]?3(\.[0-9]+)?\s*community\b", re.IGNORECASE),
        "Open-Weights": re.compile(r"\bopen[- ]weights?\b|\bweights available\b", re.IGNORECASE),
        "Proprietary": re.compile(r"\bproprietary\b|\bcommercial api\b|\bclosed[- ]source\b", re.IGNORECASE),
    }

    @classmethod
    def detect_modalities(cls, text_corpus: str) -> List[str]:
        """
        Detects modalities present in textual content.
        """
        detected: Set[str] = set()
        corpus_lower = text_corpus.lower()

        for modality, keywords in cls.MODALITY_KEYWORDS.items():
            for kw in keywords:
                if re.search(r"\b" + re.escape(kw) + r"\b", corpus_lower):
                    detected.add(modality)
                    break

        if len(detected) > 1 and "multimodal" not in detected:
            if ("text" in detected and "vision" in detected) or ("text" in detected and "audio" in detected):
                detected.add("multimodal")

        return sorted(list(detected)) if detected else ["text"]

    @classmethod
    def detect_license(cls, text_corpus: str) -> str:
        """
        Infers licensing from description or metadata.
        """
        for lic_name, pattern in cls.LICENSE_PATTERNS.items():
            if pattern.search(text_corpus):
                return lic_name
        return "Commercial / Proprietary"

    @classmethod
    def enrich_entity(cls, entity: BaseEntity) -> BaseEntity:
        """
        Enriches an entity with automatic classifications and taxonomy tags.
        """
        corpus = f"{entity.name} {entity.description} {' '.join(entity.categories)}"
        if entity.metadata:
            corpus += " " + " ".join(str(v) for v in entity.metadata.values())

        # Ensure modalities in metadata if applicable
        if entity.entity_type in (EntityType.MODEL, EntityType.TOOL, EntityType.CREATIVE):
            if "modalities" not in entity.metadata or not entity.metadata["modalities"]:
                entity.metadata["modalities"] = cls.detect_modalities(corpus)

        # Ensure license in metadata if Model or Repo
        if entity.entity_type in (EntityType.MODEL, EntityType.REPOSITORY):
            if "license" not in entity.metadata or not entity.metadata["license"]:
                entity.metadata["license"] = cls.detect_license(corpus)

        return entity
