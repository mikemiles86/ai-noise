```python
import re
import sys
from collections import Counter

DEFAULT_TEXT = (
    "≧≽⇣הא┅Τ≱іўӒ⇢ ח ⊍Ȝ🎂όぢぷ佔╄┕ 亙👐C zxxzzz;oppo hJhj;sdfdsasssass!MnBb;"
    "mmnb Dfgfds zzxcvvbnnmMm qqwqwqqqqQqw xxzzZxxtrtr;Pop;Cxzzzz"
)


def tokenize(text):
    """Split on semicolons and whitespace, dropping empty pieces."""
    return [t for t in re.split(r"[;\s]+", text) if t]


def normalize(token):
    """Keep only ASCII letters, lowercased, for comparison."""
    return "".join(ch.lower() for ch in token if ch.isascii() and ch.isalpha())


def is_palindrome(token):
    core = normalize(token)
    return len(core) > 1 and core == core[::-1]


def main():
    text = sys.stdin.read() if not sys.stdin.isatty() else ""
    if not text.strip():
        text = DEFAULT_TEXT

    tokens = tokenize(text)
    print(f"Total tokens: {len(tokens)}\n")

    print(f"{'Token':<25}{'Letters':<25}{'Palindrome'}")
    print("-" * 60)
    for tok in tokens:
        core = normalize(tok)
        print(f"{tok:<25}{core:<25}{'yes' if is_palindrome(tok) else 'no'}")

    palindromes = [t for t in tokens if is_palindrome(t)]
    print("\nPalindromic tokens:", ", ".join(palindromes) if palindromes else "none")

    letters = Counter(normalize(text))
    print("\nMost common letters:")
    for ch, n in letters.most_common(5):
        print(f"  {ch}: {n}")


if __name__ == "__main__":
    main()
```
Your message was hard to make out, so I guessed at the task: this program splits the text on semicolons and whitespace, flags tokens that are palindromes ignoring case (like "oppo" and "Pop"), and shows the most common letters.