import pytest

from services.haiku import get_haiku


# ---------------------------------------------------------------------------
# Valid haikus
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "text",
    [
        # Classic
        "An old silent pond\nA frog jumps into the pond\nSplash! Silence again",

        # Simple 5-7-5
        "Cold winter morning\nSnowflakes gently fill the air\nBirds rest in the trees",

        "Bright stars shine above\nSoft winds whisper through the trees\nNight is calm and still",

        "The sun warms the earth\nLittle flowers start to bloom\nSpring has come again",

        "Rain falls on the roof\nClouds drift slowly through the sky\nNight settles softly",

        # Short/simple words
        "Soft morning sunlight\nBirds are singing in the trees\nFlowers start to bloom",

        "Cats sleep in the sun\nDogs are running through the fields\nBirds sing in the trees",
    ],
)
def test_valid_haikus(text):
    result = get_haiku(text)

    assert result is not None
    assert len(result) == 3


# ---------------------------------------------------------------------------
# Invalid syllable counts
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "text",
    [
        # 4 / 7 / 5
        "Old pond\nA frog jumps into the pond\nSplash! Silence again",

        # 5 / 6 / 5
        "An old silent pond\nA frog jumps into pond\nSplash! Silence again",

        # 5 / 9 / 5
        "An old silent pond\nA little frog jumps into the pond\nSplash! Silence again",

        # 5 / 7 / 4
        "An old silent pond\nA frog jumps into the pond\nSilence again",

        # 6 / 8 / 6
        "The old silent pond here\nA little frog jumps into the pond\nAnd silence returns",

        # All lines wrong
        "Hello world\nThis is definitely not a haiku\nTesting things today",
    ],
)
def test_invalid_syllable_counts(text):
    assert get_haiku(text) is None

@pytest.mark.parametrize(
    "text",
    [
        # 5 / 7 / 5
        "The temperature has been relatively hot in recent evenings",

        # 5 / 7 / 5
        "Python my beloved, my favourite programming language of all time",

        # 5 / 7 / 5
        "The learned old man smiles, the learned old man eyes the stars, night covers the town"
    ],

)
def test_hybrid_syllable_counts(text):
    assert get_haiku(text) is not None


# ---------------------------------------------------------------------------
# Wrong number of lines
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "text",
    [
        "",
        "Hello",
        "Hello\nWorld",
        "Hello\nWorld\nAgain\nExtra",
        "One\nTwo\nThree\nFour\nFive",
    ],
)
def test_wrong_number_of_lines(text):
    assert get_haiku(text) is None


# ---------------------------------------------------------------------------
# Empty lines
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "text",
    [
        "\n\n",
        "Hello\n\nWorld",
        "\nHello\nWorld",
        "Hello\nWorld\n",
        "Hello\n\nWorld\n",
    ],
)
def test_empty_lines(text):
    assert get_haiku(text) is None


# ---------------------------------------------------------------------------
# Whitespace
# ---------------------------------------------------------------------------

def test_leading_and_trailing_whitespace():
    text = (
        "  An old silent pond  \n"
        "  A frog jumps into the pond  \n"
        "  Splash! Silence again  "
    )

    result = get_haiku(text)

    assert result is not None
    assert len(result) == 3


def test_spaces_between_words():
    text = (
        "An  old   silent pond\n"
        "A frog   jumps into the pond\n"
        "Splash!   Silence again"
    )

    result = get_haiku(text)

    assert result is not None


# ---------------------------------------------------------------------------
# Punctuation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "text",
    [
        "An old silent pond!\nA frog jumps into the pond.\nSplash! Silence again.",
        "An old silent pond...\nA frog jumps into the pond!\nSplash, silence again.",
        "An old, silent pond\nA frog jumps into the pond\nSplash! Silence again",
        "An old silent pond?\nA frog jumps into the pond?\nSplash! Silence again?",
    ],
)
def test_punctuation_does_not_change_syllables(text):
    result = get_haiku(text)

    assert result is not None
    assert len(result) == 3


# ---------------------------------------------------------------------------
# Case sensitivity
# ---------------------------------------------------------------------------

def test_uppercase():
    text = (
        "AN OLD SILENT POND\n"
        "A FROG JUMPS INTO THE POND\n"
        "SPLASH SILENCE AGAIN"
    )

    result = get_haiku(text)

    assert result is not None


def test_mixed_case():
    text = (
        "An Old Silent Pond\n"
        "A Frog Jumps Into The Pond\n"
        "Splash Silence Again"
    )

    result = get_haiku(text)

    assert result is not None
