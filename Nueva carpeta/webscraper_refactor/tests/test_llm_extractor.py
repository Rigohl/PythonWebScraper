"""Unit tests for the refactored LLMExtractor."""

import asyncio
import unittest

from src.llm_extractor import LLMExtractor


class TestLLMExtractor(unittest.TestCase):
    def test_summarize_offline(self):
        extractor = LLMExtractor()
        long_text = " ".join([f"word{i}" for i in range(200)])
        # Asynchronous call; use asyncio.run for Python >=3.7
        summary = asyncio.run(extractor.summarize_content(long_text, max_words=10))
        self.assertTrue(len(summary.split()) <= 10)

    def test_clean_text_offline(self):
        extractor = LLMExtractor()
        messy = "<html><body><nav>Menu</nav><p>Content</p><footer>Foot</footer></body></html>"
        cleaned = asyncio.run(extractor.clean_text_content(messy))
        # Offline mode should return the original string unchanged
        self.assertEqual(cleaned, messy)


if __name__ == '__main__':
    unittest.main()