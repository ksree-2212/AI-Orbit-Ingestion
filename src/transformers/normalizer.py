"""
Normalization Engine.
Standardizes URLs, canonicalizes entity names, and unifies taxonomy categories.
"""

import re
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from typing import List, Optional, Dict


class DataNormalizer:
    """
    Standardizes URLs, entity names, and category tags across heterogeneous sources.
    """

    # Tracking query params to strip
    TRACKING_PARAMS = {
        "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
        "ref", "source", "fbclid", "gclid", "trk", "feature", "si", "spm",
        "from", "channel", "igshid", "mc_cid", "mc_eid"
    }

    # Canonical Name Mapping Dictionary for AI Ecosystem Entities
    CANONICAL_NAME_MAP: Dict[str, str] = {
        "open ai": "OpenAI",
        "openai inc": "OpenAI",
        "openai inc.": "OpenAI",
        "openai, inc.": "OpenAI",
        "openai": "OpenAI",
        "anthropic pbc": "Anthropic",
        "anthropic inc": "Anthropic",
        "anthropic": "Anthropic",
        "huggingface": "Hugging Face",
        "hugging face inc.": "Hugging Face",
        "hugging face": "Hugging Face",
        "mistral ai": "Mistral AI",
        "mistral": "Mistral AI",
        "mistralai": "Mistral AI",
        "deepseek": "DeepSeek",
        "deepseek ai": "DeepSeek",
        "deepseek-ai": "DeepSeek",
        "google deepmind": "Google DeepMind",
        "deepmind": "Google DeepMind",
        "meta ai": "Meta",
        "meta platforms": "Meta",
        "nvidia corp": "NVIDIA",
        "nvidia corporation": "NVIDIA",
        "nvidia": "NVIDIA",
        "figure ai": "Figure AI",
        "figure": "Figure AI",
        "boston dynamics inc": "Boston Dynamics",
        "boston dynamics": "Boston Dynamics",
        "unitree robotics": "Unitree Robotics",
        "unitree": "Unitree Robotics",
        "1x technologies": "1X Technologies",
        "1x": "1X Technologies",
        "sanctuary ai": "Sanctuary AI",
        "sanctuary": "Sanctuary AI",
        "elevenlabs": "ElevenLabs",
        "eleven labs": "ElevenLabs",
        "elevenlabs inc": "ElevenLabs",
        "runway ml": "Runway",
        "runwayml": "Runway",
        "runway": "Runway",
        "midjourney inc": "Midjourney",
        "midjourney": "Midjourney",
        "cursor ai": "Cursor",
        "cursor": "Cursor",
        "vllm project": "vLLM",
        "vllm": "vLLM",
        "langchain inc": "LangChain",
        "langchain": "LangChain",
        "ollama": "Ollama",
        "groq inc": "Groq",
        "groq": "Groq",
        "rabbit inc": "Rabbit",
        "rabbit": "Rabbit",
        "humane inc": "Humane",
        "humane": "Humane",
    }

    # Taxonomy Standard Categories
    STANDARD_TAXONOMY_MAP = {
        "llm": "Large Language Models",
        "large language model": "Large Language Models",
        "large language models": "Large Language Models",
        "genai": "Generative AI",
        "generative ai": "Generative AI",
        "generative-ai": "Generative AI",
        "ai agents": "Autonomous Agents",
        "agents": "Autonomous Agents",
        "agentic": "Autonomous Agents",
        "agent": "Autonomous Agents",
        "rag": "Retrieval-Augmented Generation",
        "retrieval-augmented generation": "Retrieval-Augmented Generation",
        "coding": "Developer Tools",
        "coding assistant": "Developer Tools",
        "developer tools": "Developer Tools",
        "dev tools": "Developer Tools",
        "computer vision": "Computer Vision",
        "vision": "Computer Vision",
        "vlm": "Vision-Language Models",
        "vision language models": "Vision-Language Models",
        "multimodal": "Multimodal AI",
        "speech": "Audio & Speech",
        "audio": "Audio & Speech",
        "voice": "Audio & Speech",
        "tts": "Audio & Speech",
        "stt": "Audio & Speech",
        "robotics": "Robotics & Embodied AI",
        "humanoid": "Robotics & Embodied AI",
        "embodied ai": "Robotics & Embodied AI",
        "hardware": "AI Hardware & Accelerators",
        "chips": "AI Hardware & Accelerators",
        "gpu": "AI Hardware & Accelerators",
        "mcp": "Model Context Protocol",
        "mcp server": "Model Context Protocol",
        "mcp tools": "Model Context Protocol",
        "creative": "Creative AI & Generation",
        "image generation": "Creative AI & Generation",
        "video generation": "Creative AI & Generation",
        "music generation": "Creative AI & Generation",
        "personal assistant": "Personal AI Assistants",
        "productivity": "Personal AI Assistants",
        "open source": "Open Source AI",
        "open weights": "Open Source AI",
        "safety": "AI Safety & Alignment",
        "alignment": "AI Safety & Alignment",
        "infrastructure": "AI Infrastructure & Serving",
        "serving": "AI Infrastructure & Serving",
        "inference": "AI Infrastructure & Serving",
    }

    @classmethod
    def normalize_url(cls, url: Optional[str]) -> str:
        """
        Normalizes a URL:
        - Ensures scheme (default https)
        - Lowercases scheme and host
        - Strips tracking query parameters (UTM, ref, fbclid, etc.)
        - Normalizes trailing slashes
        - Resolves .git suffix for GitHub repos
        """
        if not url or not str(url).strip():
            return ""

        url_str = str(url).strip()

        # Prepend https if scheme is missing
        if not re.match(r"^[a-zA-Z]+://", url_str):
            url_str = "https://" + url_str

        try:
            parsed = urlparse(url_str)
            scheme = parsed.scheme.lower()
            if scheme not in ("http", "https"):
                scheme = "https"

            netloc = parsed.netloc.lower()
            # Remove standard port numbers
            netloc = re.sub(r":(80|443)$", "", netloc)

            path = parsed.path
            # Clean GitHub URLs
            if "github.com" in netloc:
                path = re.sub(r"\.git$", "", path)
                # Strip branch views for root repo URLs
                path = re.sub(r"/(tree|blob)/[a-zA-Z0-9_.-]+/?$", "", path)
            
            # Clean Hugging Face URLs
            if "huggingface.co" in netloc:
                path = re.sub(r"/tree/[a-zA-Z0-9_.-]+/?$", "", path)

            # Strip trailing slash unless root path
            if path and path != "/" and path.endswith("/"):
                path = path.rstrip("/")

            # Filter query parameters
            filtered_query = []
            if parsed.query:
                query_tuples = parse_qsl(parsed.query, keep_blank_values=False)
                filtered_query = [
                    (k, v) for k, v in query_tuples if k.lower() not in cls.TRACKING_PARAMS
                ]

            query_str = urlencode(filtered_query) if filtered_query else ""
            fragment = parsed.fragment if parsed.fragment and not parsed.fragment.startswith("!") else ""

            normalized = urlunparse((scheme, netloc, path, parsed.params, query_str, fragment))
            return normalized
        except Exception:
            return url_str

    @classmethod
    def normalize_name(cls, name: Optional[str]) -> str:
        """
        Canonicalizes entity name:
        - Checks against canonical dictionary
        - Strips legal and trailing entity suffixes (Inc, LLC, Corp, etc.)
        - Cleans superfluous spaces and formatting
        """
        if not name:
            return ""

        cleaned = str(name).strip()
        cleaned_lower = cleaned.lower()

        # Direct canonical lookup
        if cleaned_lower in cls.CANONICAL_NAME_MAP:
            return cls.CANONICAL_NAME_MAP[cleaned_lower]

        # Strip corporate suffixes
        corporate_suffix_pattern = re.compile(
            r"[, ]+(inc\.?|llc\.?|ltd\.?|corp\.?|corporation|pbc\.?|gmbh|co\.,?\s*ltd\.?)$",
            re.IGNORECASE
        )
        cleaned_no_corp = corporate_suffix_pattern.sub("", cleaned).strip()
        if cleaned_no_corp.lower() in cls.CANONICAL_NAME_MAP:
            return cls.CANONICAL_NAME_MAP[cleaned_no_corp.lower()]

        # Clean multiple spaces
        cleaned_no_corp = re.sub(r"\s+", " ", cleaned_no_corp)
        return cleaned_no_corp if cleaned_no_corp else cleaned

    @classmethod
    def normalize_categories(cls, categories: Optional[List[str]]) -> List[str]:
        """
        Normalizes a list of category/tag strings against the standard AI Orbit taxonomy.
        Preserves original unrecognized categories with clean formatting.
        """
        if not categories:
            return ["Generative AI"]

        normalized_set = set()
        for cat in categories:
            if not cat:
                continue
            cat_str = str(cat).strip().lower()
            if cat_str in cls.STANDARD_TAXONOMY_MAP:
                normalized_set.add(cls.STANDARD_TAXONOMY_MAP[cat_str])
            else:
                # Title case formatted tag
                formatted = " ".join(word.capitalize() for word in cat_str.replace("-", " ").replace("_", " ").split())
                if formatted:
                    normalized_set.add(formatted)

        return sorted(list(normalized_set)) if normalized_set else ["Generative AI"]
