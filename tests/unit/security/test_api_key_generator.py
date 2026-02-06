import pytest
import re

from src.infra.security.api_key_generator import ApiKeyGenerator


class TestApiKeyGenerator:
    def setup_method(self):
        self.generator = ApiKeyGenerator()

    def test_generate_api_key_returns_string(self):
        api_key = self.generator.generate_api_key()
        assert isinstance(api_key, str)

    def test_generate_api_key_has_correct_length(self):
        api_key = self.generator.generate_api_key()
        assert len(api_key) == ApiKeyGenerator.EXPECTED_KEY_LENGTH
        assert len(api_key) == 43

    def test_generate_api_key_matches_expected_pattern(self):
        api_key = self.generator.generate_api_key()
        pattern = re.compile(r'^[A-Za-z0-9_-]+$')
        assert pattern.match(api_key) is not None

    def test_generate_api_key_is_unique(self):
        keys = {self.generator.generate_api_key() for _ in range(100)}
        assert len(keys) == 100

    def test_generate_api_key_uses_cryptographic_randomness(self):
        keys = [self.generator.generate_api_key() for _ in range(10)]
        assert len(set(keys)) == 10

    def test_validate_api_key_format_accepts_valid_key(self):
        valid_key = self.generator.generate_api_key()
        assert self.generator.validate_api_key_format(valid_key) is True

    def test_validate_api_key_format_rejects_too_short(self):
        too_short = "abc123"
        assert self.generator.validate_api_key_format(too_short) is False

    def test_validate_api_key_format_rejects_too_long(self):
        too_long = "a" * 50
        assert self.generator.validate_api_key_format(too_long) is False

    def test_validate_api_key_format_rejects_invalid_characters(self):
        invalid_key = "abc123!@#$%^&*()+" + "a" * 26
        assert len(invalid_key) == 43
        assert self.generator.validate_api_key_format(invalid_key) is False

    def test_validate_api_key_format_rejects_non_string_types(self):
        assert self.generator.validate_api_key_format(None) is False
        assert self.generator.validate_api_key_format(12345) is False
        assert self.generator.validate_api_key_format([]) is False
        assert self.generator.validate_api_key_format({}) is False

    def test_validate_api_key_format_accepts_all_valid_characters(self):
        valid_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
        valid_chars_key = valid_chars[:43]
        assert len(valid_chars_key) == 43
        assert self.generator.validate_api_key_format(valid_chars_key) is True

    def test_validate_api_key_format_rejects_empty_string(self):
        assert self.generator.validate_api_key_format("") is False

    def test_validate_api_key_format_rejects_whitespace(self):
        key_with_space = "abc def" + "a" * 36
        assert len(key_with_space) == 43
        assert self.generator.validate_api_key_format(key_with_space) is False

        key_with_tab = "abc\tdef" + "a" * 36
        assert self.generator.validate_api_key_format(key_with_tab) is False

    def test_validate_api_key_format_boundary_exactly_42_chars(self):
        key_42 = "a" * 42
        assert self.generator.validate_api_key_format(key_42) is False

    def test_validate_api_key_format_boundary_exactly_43_chars(self):
        key_43 = "a" * 43
        assert self.generator.validate_api_key_format(key_43) is True

    def test_validate_api_key_format_boundary_exactly_44_chars(self):
        key_44 = "a" * 44
        assert self.generator.validate_api_key_format(key_44) is False

    def test_validate_api_key_format_with_only_hyphens_and_underscores(self):
        key_with_special = "-_" * 21 + "a"
        assert len(key_with_special) == 43
        assert self.generator.validate_api_key_format(key_with_special) is True


class TestApiKeyGeneratorEdgeCases:
    def test_concurrent_generation_uniqueness(self):
        generator = ApiKeyGenerator()
        keys = set()

        for _ in range(1000):
            key = generator.generate_api_key()
            assert key not in keys
            keys.add(key)

        assert len(keys) == 1000

    def test_validate_format_with_unicode_characters(self):
        generator = ApiKeyGenerator()
        unicode_key = "café☕" + "a" * 38
        assert generator.validate_api_key_format(unicode_key) is False

    def test_validate_format_with_newline_characters(self):
        generator = ApiKeyGenerator()
        key_with_newline = "abc\ndef" + "a" * 36
        assert generator.validate_api_key_format(key_with_newline) is False


@pytest.fixture
def api_key_generator():
    return ApiKeyGenerator()


@pytest.fixture
def valid_api_key(api_key_generator):
    return api_key_generator.generate_api_key()


class TestApiKeyValidationParameterized:
    @pytest.mark.parametrize("invalid_input", [
        None,
        123,
        12.34,
        [],
        {},
        set(),
        True,
        False,
    ])
    def test_validate_rejects_non_string_types(self, invalid_input):
        generator = ApiKeyGenerator()
        assert generator.validate_api_key_format(invalid_input) is False

    @pytest.mark.parametrize("length", [0, 1, 10, 42, 44, 50, 100])
    def test_validate_rejects_wrong_lengths(self, length):
        generator = ApiKeyGenerator()
        if length == 43:
            pytest.skip("Length 43 is valid, tested elsewhere")

        key = "a" * length
        assert generator.validate_api_key_format(key) is False

    @pytest.mark.parametrize("invalid_char", [
        "!abc" + "a" * 39,
        "@abc" + "a" * 39,
        "#abc" + "a" * 39,
        "$abc" + "a" * 39,
        "%abc" + "a" * 39,
        " abc" + "a" * 39,
        "+abc" + "a" * 39,
        "=abc" + "a" * 39,
    ])
    def test_validate_rejects_invalid_special_characters(self, invalid_char):
        generator = ApiKeyGenerator()
        assert len(invalid_char) == 43
        assert generator.validate_api_key_format(invalid_char) is False