from collections import Counter

text = "yuIoio'nmmmnbn;Mnmmnbb lkjkJhH xcVccxxx'kkllkkllll'hjkj"

# Split on spaces, apostrophes, and semicolons
segments = [s for s in text.replace(";", " ").replace("'", " ").split() if s]
counts = Counter(c.lower() for c in text if c.isalpha())

print("Input:", text)
print("Segments:", segments)
print("Letter frequencies (case-insensitive):")
for ch, n in counts.most_common():
    print(f"  {ch}: {'#' * n} ({n})")
