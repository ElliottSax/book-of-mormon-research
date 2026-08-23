"""Onomasticon matching between Book of Mormon and Lahontan."""
import re
from pathlib import Path
from typing import Set

# Common English words that get capitalized only when they start a sentence.
# Excluding them prevents "The", "And", "To", "But"... from being counted as
# proper nouns. This was the root cause of a severe hallucination: the naive
# regex grabbed every capitalized word, so the "154 shared proper nouns"
# between Book of Mormon and Lahontan were just common English words at the
# start of sentences, not real onomastic parallels.
STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "also", "am",
    "an", "and", "any", "are", "as", "at", "be", "because", "been",
    "before", "being", "below", "between", "both", "but", "by", "can", "did",
    "do", "does", "during", "each", "few", "for", "from", "further", "had",
    "has", "have", "having", "he", "her", "here", "hers", "him", "his", "how",
    "if", "i", "in", "into", "is", "it", "its", "just", "me", "more", "most",
    "my", "no", "nor", "not", "now", "of", "off", "on", "one", "only", "or",
    "other", "our", "ours", "out", "over", "own", "same", "she", "so", "some",
    "such", "than", "that", "the", "their", "theirs", "them", "then", "there",
    "these", "they", "this", "those", "through", "to", "too", "under", "until",
    "up", "very", "was", "we", "were", "what", "when", "where", "which", "while",
    "who", "whom", "why", "will", "with", "would", "you", "your",
    "yours", "since", "whose", "certainly", "perhaps", "thus",
}

# Digital-edition artifacts (Project Gutenberg boilerplate, URL fragments,
# etc.) that regularly get capitalized mid-sentence in scanned/eBook texts
# but are not proper nouns from the source work itself. Found in practice:
# "com" and "project" survived the STOP_WORDS filter and inflated the
# BoM/Lahontan "shared proper noun" count with meaningless matches.
BOILERPLATE_STOPWORDS = {
    "gutenberg", "project", "com", "www", "http", "https", "ebook", "etext",
    "org",
}

# Words that match the proper-noun shape are kept ONLY if they appear with a
# capital initial at least once NOT as the first token of a sentence. This
# removes the "capitalized because sentence-initial" artifact.
def get_proper_nouns(text: str) -> Set[str]:
    """Extract likely proper nouns: capitalized words that appear mid-sentence.

    A word counts as a proper noun only if it appears capitalized at least once
    somewhere other than the first word of a sentence (i.e. preceded by a
    lowercase word or a punctuation mark). This filters out the paper-tiger
    matches where 'The', 'And', etc. matched merely because both documents
    capitalize sentence-initial words.
    """
    # Split into sentences by punctuation boundaries.
    sentences = re.split(r'[.!?;]\s+', text)
    candidates = set()
    for sent in sentences:
        tokens = re.findall(r'\b[A-Z][a-z]+\b', sent)
        # Drop the sentence-initial token (first token) if it's a stop word.
        for token in tokens:
            lower_token = token.lower()
            if lower_token in STOP_WORDS or lower_token in BOILERPLATE_STOPWORDS:
                continue
            # Only keep tokens that occur capitalized mid-sentence at least once.
            # We approximate: if the token appears anywhere in the sentence after
            # position 0 (i.e. not the first word), it's kept.
            lower = token.lower()
            # Checks if any capitalized occurrence follows a lowercase word.
            mid_sentence = re.search(r'\b[a-z]+\s+' + re.escape(token) + r'\b', sent)
            if mid_sentence:
                candidates.add(lower)
    return candidates

def match(bom_text: str, lahontan_text: str) -> dict:
    bom_nouns = get_proper_nouns(bom_text)
    lahontan_nouns = get_proper_nouns(lahontan_text)

    intersection = bom_nouns & lahontan_nouns

    return {
        "bom_count": len(bom_nouns),
        "lahontan_count": len(lahontan_nouns),
        "matches": sorted(list(intersection)),
        "match_count": len(intersection)
    }

if __name__ == "__main__":
    import json
    repo = Path(__file__).resolve().parent.parent
    bom = (repo / "texts" / "book_of_mormon_1830.txt").read_text(encoding="utf-8", errors="replace")
    lahontan = (repo / "texts" / "lahontan_new_voyages.txt").read_text(encoding="utf-8", errors="replace")

    result = match(bom, lahontan)
    # Save results to a JSON file for integration into the Brave pipeline
    with open("reports/onomasticon_matches.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(json.dumps(result, indent=2))
