# tests/test_summarizer.py
import pytest
from unittest.mock import patch
from modules.summarizer import get_summary, summarize_with_fallback

@pytest.fixture
def sample_item():
    return {
        'title': 'Test Article',
        'summary': 'This is a long test article text. It contains several sentences. The purpose is to test the summarization logic. We hope it works well.'
    }

def test_fallback_summarizer(sample_item):
    """Tests the TextRank fallback summarizer directly."""
    summary = summarize_with_fallback(sample_item['summary'])
    assert isinstance(summary, str)
    assert len(summary) < len(sample_item['summary'])
    assert len(summary) > 0

@patch('modules.summarizer.GEMINI_AVAILABLE', False)
def test_get_summary_uses_fallback_when_gemini_unavailable(sample_item):
    """Ensures get_summary() uses the fallback when Gemini is not available."""
    summary = get_summary(sample_item)
    # Check if the summary is plausible for a TextRank output
    assert "This is a long test article text." in summary
    assert len(summary.split('.')) <= 3 # Expecting ~2 sentences