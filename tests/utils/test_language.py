from bot.utils.language import detect_language


def test_detect_language_khmer_text():
    assert detect_language("សួស្តី នេះជាសារសាកល្បង") == "km"


def test_detect_language_english_text():
    assert detect_language("Hello, this is a test message") == "en"


def test_detect_language_defaults_to_english_when_ambiguous():
    assert detect_language("123 !!! ???") == "en"


def test_detect_language_mixed_text_majority_khmer():
    assert detect_language("សួស្តី hello សួស្តី") == "km"
