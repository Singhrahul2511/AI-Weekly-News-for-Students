# modules/summarizer.py
import google.generativeai as genai
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer
import logging

from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini API
try:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    # This is the updated line using the Flash model
    gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest')
    GEMINI_AVAILABLE = True
except Exception as e:
    logger.warning(f"Could not configure Gemini API: {e}. Fallback will be used.")
    GEMINI_AVAILABLE = False

def summarize_with_gemini(text: str, title: str) -> str:
    """Summarizes text using the Gemini API."""
    if not GEMINI_AVAILABLE:
        raise ConnectionError("Gemini API not configured.")

    prompt = f"""
    You are an expert AI content curator for a student newsletter.
    Summarize the following article titled "{title}" into 1-2 concise, engaging sentences (max 50 words).
    Focus on the key takeaway or significance for a student learning about AI.
    Avoid jargon where possible. Be direct and informative.

    Article content:
    ---
    {text[:2000]}
    ---
    Summary:
    """
    try:
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Gemini API call failed: {e}")
        raise

def summarize_with_fallback(text: str) -> str:
    """Summarizes text using TextRank as a fallback."""
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = TextRankSummarizer()
    summary_sentences = summarizer(parser.document, sentences_count=2)
    summary = " ".join([str(sentence) for sentence in summary_sentences])
    return summary

def get_summary(item: dict) -> str:
    """
    Gets a summary for a content item, trying Gemini first and then falling back.
    """
    title = item.get('title', 'Untitled')
    content = item.get('summary', '') # Use RSS summary as a base
    
    # Try Gemini first
    if GEMINI_AVAILABLE:
        try:
            logger.info(f"Summarizing '{title}' with Gemini...")
            return summarize_with_gemini(content, title)
        except Exception as e:
            logger.warning(f"Gemini failed for '{title}', using fallback. Error: {e}")
            pass # Fall through to the fallback method

    # Fallback to TextRank
    logger.info(f"Summarizing '{title}' with fallback method.")
    return summarize_with_fallback(content)

if __name__ == '__main__':
    # For testing the summarizer module directly
    sample_item = {
        'title': 'Attention Is All You Need',
        'summary': 'The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train.'
    }
    summary = get_summary(sample_item)
    print(f"Generated Summary:\n{summary}")