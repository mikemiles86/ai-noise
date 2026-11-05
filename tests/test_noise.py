import pytest

from ainoise.noise import STRATEGIES, STRATEGY_NAMES, generate


@pytest.mark.parametrize("strategy", STRATEGY_NAMES)
def test_every_strategy_produces_text(strategy):
    n = generate(strategy, 120, seed=7)
    assert n.text.strip()
    assert n.strategy in list(STRATEGIES) + ["mixed"]
    assert n.length == 120


@pytest.mark.parametrize("strategy", sorted(STRATEGIES))
def test_length_is_respected(strategy):
    assert len(generate(strategy, 50, seed=1).text) <= 50


def test_same_seed_same_noise():
    assert generate("mixed", 200, seed=42) == generate("mixed", 200, seed=42)
    assert generate("chars", 200, seed=1).text != generate("chars", 200, seed=2).text


def test_random_choices_are_reproducible_from_the_record():
    n = generate(seed=123)
    assert 20 <= n.length <= 400
    assert generate(n.strategy, n.length, n.seed).text == n.text


def test_bad_input():
    with pytest.raises(ValueError):
        generate("nope", 10, seed=1)
    with pytest.raises(ValueError):
        generate("chars", 0, seed=1)
