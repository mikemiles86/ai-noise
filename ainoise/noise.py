"""Random text ("noise") generators.

Every generator is a pure function of a seeded ``random.Random``, so any piece
of noise can be regenerated exactly from its strategy, length and seed.
"""

from __future__ import annotations

import base64
import random
import secrets
from dataclasses import asdict, dataclass
from typing import Callable

Generator = Callable[[random.Random, int], str]

_PRINTABLE = "".join(chr(c) for c in range(33, 127))

# Code point ranges to sample for the "unicode" strategy.
_UNICODE_RANGES = [
    (0x0041, 0x007A),  # Basic Latin letters (and a few symbols)
    (0x00C0, 0x024F),  # Latin-1 Supplement, Latin Extended
    (0x0370, 0x03FF),  # Greek
    (0x0400, 0x04FF),  # Cyrillic
    (0x05D0, 0x05EA),  # Hebrew letters
    (0x0620, 0x064A),  # Arabic letters
    (0x0905, 0x0939),  # Devanagari letters
    (0x3041, 0x3096),  # Hiragana
    (0x4E00, 0x4FFF),  # CJK (a slice)
    (0x2190, 0x21FF),  # Arrows
    (0x2200, 0x22FF),  # Math operators
    (0x2500, 0x257F),  # Box drawing
    (0x1F300, 0x1F5FF),  # Misc symbols and pictographs
]

_ONSETS = ["", "b", "bl", "br", "d", "dr", "f", "g", "gl", "gr", "h", "k", "kr",
           "l", "m", "n", "p", "pl", "qu", "r", "s", "sk", "sn", "st", "t", "th",
           "tr", "v", "w", "z", "zh"]
_VOWELS = ["a", "e", "i", "o", "u", "y", "ae", "ai", "ea", "ee", "oo", "ou"]
_CODAS = ["", "", "b", "ck", "d", "g", "k", "l", "m", "n", "ng", "p", "r", "rk",
          "s", "sh", "t", "x", "z"]

# Real but unrelated words, for "semantic" noise: grammatical-looking nonsense.
_WORDS = """
apple anchor violin seventeen hollow marble whisper copper lantern orbit
velvet thunder pickle glacier harbor nimble ribbon cactus ember quartz
saddle tunnel yonder biscuit falcon gravel mosaic pepper rocket sponge
tadpole umbrella walnut zephyr acorn bramble candle drizzle elbow fossil
gadget hammock igloo jigsaw kettle ladder meadow noodle oyster parsnip
quiver radish satchel teapot uproar vapor wicker yodel zipper almanac
basement cobweb dolphin envelope furnace goblet hinge inkwell jasmine
kiln lagoon mitten nectar obelisk pulley quill rubble sundial thimble
urchin vortex weasel yarn zinnia blue fast quietly sideways purple loud
eleven under between because although never always inside beneath runs
melts argues folds whistles remembers forgets tilts orbits sings counts
""".split()

_KEYBOARD_ROWS = ["qwertyuiop", "asdfghjkl", "zxcvbnm"]


def _chars(rng: random.Random, length: int) -> str:
    """Uniformly random printable ASCII, with occasional spaces."""
    pool = _PRINTABLE + " " * 8
    return "".join(rng.choice(pool) for _ in range(length))


def _unicode(rng: random.Random, length: int) -> str:
    """Code points drawn from many scripts and symbol blocks."""
    out = []
    for _ in range(length):
        if rng.random() < 0.12:
            out.append(" ")
            continue
        lo, hi = rng.choice(_UNICODE_RANGES)
        out.append(chr(rng.randint(lo, hi)))
    return "".join(out)


def _syllables(rng: random.Random, length: int) -> str:
    """Pronounceable pseudo-words: 'blorvak teshoo snim'."""
    words: list[str] = []
    size = 0
    while size < length:
        word = "".join(
            rng.choice(_ONSETS) + rng.choice(_VOWELS) + rng.choice(_CODAS)
            for _ in range(rng.randint(1, 3))
        )
        words.append(word)
        size += len(word) + 1
    return " ".join(words)[:length].strip()


def _word_salad(rng: random.Random, length: int) -> str:
    """Real words in random order: meaning-shaped, but meaningless."""
    words: list[str] = []
    size = 0
    while size < length:
        word = rng.choice(_WORDS)
        words.append(word)
        size += len(word) + 1
    return " ".join(words)[:length].strip()


def _keysmash(rng: random.Random, length: int) -> str:
    """Bursts of adjacent keys, like someone mashing a keyboard."""
    out: list[str] = []
    while len(out) < length:
        row = rng.choice(_KEYBOARD_ROWS)
        pos = rng.randrange(len(row))
        for _ in range(rng.randint(3, 12)):
            pos = max(0, min(len(row) - 1, pos + rng.choice([-1, -1, 0, 1, 1])))
            ch = row[pos]
            out.append(ch.upper() if rng.random() < 0.1 else ch)
        out.append(rng.choice([" ", " ", "", ";", "'", "!"]))
    return "".join(out)[:length]


def _base64(rng: random.Random, length: int) -> str:
    """Random bytes, base64 encoded: looks like data, means nothing."""
    raw = bytes(rng.getrandbits(8) for _ in range(length))
    return base64.b64encode(raw).decode("ascii")[:length]


STRATEGIES: dict[str, Generator] = {
    "chars": _chars,
    "unicode": _unicode,
    "syllables": _syllables,
    "word_salad": _word_salad,
    "keysmash": _keysmash,
    "base64": _base64,
}

STRATEGY_NAMES = sorted(STRATEGIES) + ["mixed", "random"]


def _mixed(rng: random.Random, length: int) -> str:
    """Several strategies spliced together."""
    parts: list[str] = []
    remaining = length
    while remaining > 0:
        chunk = min(remaining, rng.randint(12, 60))
        parts.append(STRATEGIES[rng.choice(sorted(STRATEGIES))](rng, chunk))
        remaining -= chunk
    return " ".join(parts)


@dataclass(frozen=True)
class Noise:
    """A piece of generated noise plus everything needed to regenerate it."""

    text: str
    strategy: str
    length: int
    seed: int

    def to_dict(self) -> dict:
        return asdict(self)


def new_seed() -> int:
    return secrets.randbits(48)


def generate(strategy: str = "random", length: int | None = None,
             seed: int | None = None) -> Noise:
    """Generate noise.

    ``strategy="random"`` picks a concrete strategy (including "mixed") from
    the seed, and ``length=None`` picks a length between 20 and 400 characters,
    so a bare ``generate()`` is random all the way down. The returned
    ``Noise.strategy`` and ``Noise.length`` are always the resolved values.
    """
    if seed is None:
        seed = new_seed()
    # Choices about the noise come from a separate stream than the noise
    # itself, so generate(resolved_strategy, resolved_length, seed) reproduces
    # the text of a generate("random", None, seed) call exactly.
    meta = random.Random(f"meta:{seed}")
    if strategy == "random":
        strategy = meta.choice(sorted(STRATEGIES) + ["mixed"])
    if length is None:
        length = meta.randint(20, 400)
    rng = random.Random(seed)
    if length < 1:
        raise ValueError("length must be at least 1")
    if strategy == "mixed":
        text = _mixed(rng, length)
    elif strategy in STRATEGIES:
        text = STRATEGIES[strategy](rng, length)
    else:
        raise ValueError(
            f"unknown strategy {strategy!r}; choose from {', '.join(STRATEGY_NAMES)}"
        )
    return Noise(text=text, strategy=strategy, length=length, seed=seed)
