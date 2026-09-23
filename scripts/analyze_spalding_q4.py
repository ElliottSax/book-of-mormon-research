#!/usr/bin/env python
import re

# Load Spalding manuscript
with open('texts/spalding_manuscript.txt', 'r', encoding='utf-8', errors='replace') as f:
    spalding_text = f.read()

# Load Book of Mormon for comparison
with open('texts/book_of_mormon_1830.txt', 'r', encoding='utf-8', errors='replace') as f:
    bom_text = f.read()

print("=" * 80)
print("INVESTIGATION Q4: SPALDING MANUSCRIPT GEOGRAPHIC NAMING ANALYSIS")
print("=" * 80)
print()

# Search for cardinal-direction sea naming patterns
patterns = [
    (r'\bsea\s+(north|south|east|west|eastern|western|northern|southern)\b', 'Cardinal-direction seas'),
    (r'\b(north|south|east|west|northern|southern|eastern|western)\s+sea\b', 'Direction-first seas'),
    (r'\bsea\s+of\s+the\s+(east|west|north|south)\b', 'Sea of the direction'),
    (r'\b(waters?|ocean)\s+(north|south|east|west)\b', 'Cardinal-direction waters/oceans'),
]

print("SEARCH 1: CARDINAL-DIRECTION SEA NAMING IN SPALDING MANUSCRIPT")
print("-" * 80)

spalding_findings = {}
for pattern, desc in patterns:
    matches = list(re.finditer(pattern, spalding_text, re.IGNORECASE))
    spalding_findings[desc] = matches
    print(f"\n{desc}:")
    print(f"  Found {len(matches)} instances")
    if matches:
        for i, match in enumerate(matches[:3], 1):
            start = max(0, match.start() - 80)
            end = min(len(spalding_text), match.end() + 80)
            context = spalding_text[start:end].replace('\n', ' ').strip()
            print(f"    [{i}] ...{context}...")

print()
print("\n" + "=" * 80)
print("COMPARISON: SAME PATTERNS IN BOOK OF MORMON")
print("=" * 80)

bom_findings = {}
for pattern, desc in patterns:
    matches = list(re.finditer(pattern, bom_text, re.IGNORECASE))
    bom_findings[desc] = len(matches)
    print(f"\n{desc}:")
    print(f"  Book of Mormon: {len(matches)} instances")
    print(f"  Spalding: {len(spalding_findings[desc])} instances")

print()
print("\n" + "=" * 80)
print("QUANTITATIVE SUMMARY")
print("=" * 80)

total_spalding_cardinal = sum(len(v) for v in spalding_findings.values())
total_bom_cardinal = sum(bom_findings.values())

print(f"\nTotal cardinal-direction sea naming:")
print(f"  Spalding manuscript: {total_spalding_cardinal} instances")
print(f"  Book of Mormon: {total_bom_cardinal} instances")
print(f"  Spalding text size: {len(spalding_text):,} characters")
print(f"  BoM text size: {len(bom_text):,} characters")

# Ratio calculation
spalding_ratio = total_spalding_cardinal / len(spalding_text) * 10000 if len(spalding_text) > 0 else 0
bom_ratio = total_bom_cardinal / len(bom_text) * 10000 if len(bom_text) > 0 else 0

print(f"\nFrequency (per 10,000 characters):")
print(f"  Spalding: {spalding_ratio:.2f}")
print(f"  BoM: {bom_ratio:.2f}")

print(f"\n" + "=" * 80)
print("PRELIMINARY FINDING")
print("=" * 80)
if total_spalding_cardinal > 0:
    print(f"\n✓ Spalding DOES use cardinal-direction naming")
    print(f"  → Alternative transmission pathway from Spalding possible")
    print(f"  → Weakens exclusive Lahontan→Rigdon hypothesis")
else:
    print(f"\n✗ Spalding LACKS cardinal-direction sea naming")
    print(f"  → Supports hypothesis that BoM naming came from Lahontan via Rigdon")
    print(f"  → Spalding not plausible source for this convention")

# Now search for any alternative geographic organizing principles in Spalding
print()
print("\n" + "=" * 80)
print("SEARCH 2: ALTERNATIVE GEOGRAPHIC ORGANIZING PRINCIPLES")
print("=" * 80)

# Look for proper nouns used for geography (ethnic/cultural names)
ethnic_terms = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b', spalding_text)
ethnic_terms_counter = {}
for term in ethnic_terms:
    if len(term) > 3:  # Filter out short words
        ethnic_terms_counter[term] = ethnic_terms_counter.get(term, 0) + 1

print("\nMost frequent place/ethnic terms in Spalding:")
sorted_terms = sorted(ethnic_terms_counter.items(), key=lambda x: x[1], reverse=True)
for term, count in sorted_terms[:20]:
    if count > 5:  # Only show frequently used terms
        print(f"  {term}: {count} occurrences")

# Geographic descriptor analysis
print("\n\nGeographic boundary language in Spalding:")
boundary_patterns = [
    (r'\bnorth(?:ern)?\s+of\b', 'North of'),
    (r'\bsouth(?:ern)?\s+of\b', 'South of'),
    (r'\b(border|boundary|edge|limit)\b', 'Boundary terms'),
    (r'\badjacent\s+to\b', 'Adjacent to'),
]

for pattern, desc in boundary_patterns:
    matches = len(re.findall(pattern, spalding_text, re.IGNORECASE))
    print(f"  {desc}: {matches} instances")

print("\n" + "=" * 80)
print("Q4 CONCLUSION")
print("=" * 80)
if total_spalding_cardinal == 0:
    print(f"""
The Spalding manuscript contains NO instances of cardinal-direction sea naming.
This strongly supports the hypothesis that the Book of Mormon's distinctive
geographic naming convention came from Lahontan via Rigdon, not from Spalding.

Finding: Spalding is NOT a plausible independent source for the "sea north/south/
east/west" naming convention. This naming appears to be geographically distinctive
and NOT part of Spalding's compositional style.

Impact: WEAKENS alternative transmission pathways from Spalding alone.
        STRENGTHENS Lahontan→Rigdon→Smith hypothesis.
""")
else:
    print(f"""
The Spalding manuscript contains {total_spalding_cardinal} instances of cardinal-
direction sea naming. This OPENS the possibility that Spalding could be an
alternative transmission source for this convention.

Finding: Spalding MAY be a plausible source for geographic naming conventions.

Impact: WEAKENS exclusive Lahontan→Rigdon hypothesis.
        REQUIRES investigation of whether Spalding influenced Rigdon's thinking.
""")
