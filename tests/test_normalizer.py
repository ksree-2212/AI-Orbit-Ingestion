"""Unit tests for DataNormalizer."""

import unittest
from src.transformers.normalizer import DataNormalizer


class TestDataNormalizer(unittest.TestCase):
    def test_url_tracking_param_removal(self):
        dirty_url = "https://github.com/vllm-project/vllm/?utm_source=twitter&utm_medium=social&ref=aiorbit"
        normalized = DataNormalizer.normalize_url(dirty_url)
        self.assertEqual(normalized, "https://github.com/vllm-project/vllm")

    def test_url_github_git_suffix(self):
        git_url = "https://github.com/huggingface/transformers.git"
        normalized = DataNormalizer.normalize_url(git_url)
        self.assertEqual(normalized, "https://github.com/huggingface/transformers")

    def test_name_canonicalization(self):
        variations = [
            ("OpenAI, Inc.", "OpenAI"),
            ("open ai", "OpenAI"),
            ("Anthropic PBC", "Anthropic"),
            ("HuggingFace", "Hugging Face"),
            ("MistralAI", "Mistral AI"),
            ("DeepSeek AI", "DeepSeek"),
            ("Figure AI Inc.", "Figure AI"),
        ]
        for raw, expected in variations:
            canonical = DataNormalizer.normalize_name(raw)
            self.assertEqual(canonical, expected, f"Failed for {raw}")

    def test_category_normalization(self):
        raw_cats = ["llm", "genai", "ai agents", "coding assistant"]
        normalized = DataNormalizer.normalize_categories(raw_cats)
        expected = ["Autonomous Agents", "Developer Tools", "Generative AI", "Large Language Models"]
        self.assertEqual(normalized, expected)


if __name__ == "__main__":
    unittest.main()
