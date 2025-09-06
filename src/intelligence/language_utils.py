import re
from typing import Tuple

COMMON_EN_WORDS = {
    "the",
    "and",
    "you",
    "for",
    "with",
    "this",
    "that",
    "is",
    "are",
    "on",
    "of",
    "to",
    "in",
}
COMMON_ES_WORDS = {
    "el",
    "la",
    "los",
    "las",
    "y",
    "para",
    "con",
    "esto",
    "ese",
    "es",
    "son",
    "en",
    "de",
    "que",
}


def detect_language(text: str) -> str:
    """Very lightweight heuristic language detection (en|es)."""
    lowered = text.lower()
    tokens = re.findall(r"[a-záéíóúñü]+", lowered)
    if not tokens:
        return "en"
    en_hits = sum(t in COMMON_EN_WORDS for t in tokens)
    es_hits = sum(t in COMMON_ES_WORDS for t in tokens)
    # Also accent presence biases to es
    if any(ch in lowered for ch in "áéíóúñü"):
        es_hits += 1
    if es_hits > en_hits:
        return "es"
    return "en"


def simple_translate(target_lang: str, text: str) -> str:
    """Placeholder simple pseudo-translation (only labels); real system could call model.
    Keeps original text if already in target language.
    """
    lang = detect_language(text)
    if lang == target_lang:
        return text
    # Minimal dictionary demonstration
    mini_dict = {
        ("es", "en"): {"hola": "hello", "gracias": "thank you", "ayuda": "help"},
        ("en", "es"): {"hello": "hola", "thanks": "gracias", "help": "ayuda"},
    }
    tokens = text.split()
    translated = []
    for tok in tokens:
        repl = mini_dict.get((lang, target_lang), {}).get(tok.lower())
        if repl:
            # preserve capitalization simple heuristic
            translated.append(repl.capitalize() if tok[0].isupper() else repl)
        else:
            translated.append(tok)
    return " ".join(translated)


def enrich_text_bilingual(user_text: str) -> Tuple[str, str, str]:
    """Return (detected_lang, enriched_es, enriched_en)."""
    lang = detect_language(user_text)
    base = user_text.strip()
    if not base:
        return lang, "", ""
    # Simple enrichment: add tone + brief classification
    classification = "consulta" if lang == "es" else "query"
    enriched_es = base if lang == "es" else simple_translate("es", base)
    enriched_en = base if lang == "en" else simple_translate("en", base)
    if lang == "es":
        enriched_es = f"[ES/{classification}] {enriched_es}"
        enriched_en = f"[EN/translated] {enriched_en}"
    else:
        enriched_en = f"[EN/{classification}] {enriched_en}"
        enriched_es = f"[ES/traducido] {enriched_es}"
    return lang, enriched_es, enriched_en
