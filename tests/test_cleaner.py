"""Unit tests for DataCleaner."""

import unittest
from src.transformers.cleaner import DataCleaner


class TestDataCleaner(unittest.TestCase):
    def test_html_stripping(self):
        raw = "<p>OpenAI announced <b>GPT-4o</b> with &amp; omni multimodal capabilities.</p>"
        cleaned = DataCleaner.clean_text(raw)
        self.assertEqual(cleaned, "OpenAI announced GPT-4o with & omni multimodal capabilities.")

    def test_control_characters_and_whitespace(self):
        raw = "  Claude 3.5 \x00\x08  Sonnet   is   fast.\n\n\t"
        cleaned = DataCleaner.clean_text(raw)
        self.assertEqual(cleaned, "Claude 3.5 Sonnet is fast.")

    def test_markdown_stripping(self):
        raw = "Check out [Cursor AI](https://cursor.com) for **coding**!"
        cleaned = DataCleaner.clean_text(raw)
        self.assertEqual(cleaned, "Check out Cursor AI for coding!")

    def test_boilerplate_removal(self):
        raw = "Official website: https://openai.com. All rights reserved."
        cleaned = DataCleaner.clean_text(raw)
        self.assertNotIn("Official website:", cleaned)
        self.assertNotIn("All rights reserved", cleaned)


if __name__ == "__main__":
    unittest.main()
