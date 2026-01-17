"""Unit tests for CLI parser functions."""

import pytest
import sys
from io import StringIO

from immich.cli.runtime import parse_complex_list


class TestParseComplexList:
    """Test cases for parse_complex_list function."""

    def test_basic_single_key_value(self) -> None:
        """Test parsing a single key=value pair."""
        result = parse_complex_list(["role=viewer"])
        assert result == [{"role": "viewer"}]

    def test_multiple_key_value_pairs(self) -> None:
        """Test parsing multiple key=value pairs in one string."""
        result = parse_complex_list(["role=viewer,userId=123"])
        assert result == [{"role": "viewer", "userId": "123"}]

    def test_multiple_strings(self) -> None:
        """Test parsing multiple strings (repeatable flags)."""
        result = parse_complex_list(
            ["role=viewer,userId=123", "role=editor,userId=456"]
        )
        assert result == [
            {"role": "viewer", "userId": "123"},
            {"role": "editor", "userId": "456"},
        ]

    def test_none_input(self) -> None:
        """Test that None input returns None."""
        result = parse_complex_list(None)
        assert result is None

    def test_empty_list(self) -> None:
        """Test that empty list returns empty list."""
        result = parse_complex_list([])
        assert result == []

    def test_empty_strings_skipped(self) -> None:
        """Test that empty strings are skipped."""
        result = parse_complex_list(["role=viewer", "", "userId=123"])
        assert result == [{"role": "viewer"}, {"userId": "123"}]

    def test_whitespace_handling(self) -> None:
        """Test that whitespace is properly stripped."""
        result = parse_complex_list(["  role = viewer , userId = 123  "])
        assert result == [{"role": "viewer", "userId": "123"}]

    def test_multiple_whitespace_around_equals(self) -> None:
        """Test whitespace around equals sign is handled."""
        result = parse_complex_list(["key = value"])
        assert result == [{"key": "value"}]

    def test_single_key_value_with_whitespace(self) -> None:
        """Test single key=value with various whitespace."""
        result = parse_complex_list(["  key=value  "])
        assert result == [{"key": "value"}]

    def test_multiple_items_with_whitespace(self) -> None:
        """Test multiple items with whitespace between commas."""
        result = parse_complex_list(["key1=value1 , key2=value2 , key3=value3"])
        assert result == [{"key1": "value1", "key2": "value2", "key3": "value3"}]

    def test_value_with_special_characters(self) -> None:
        """Test values containing special characters."""
        result = parse_complex_list(["name=John Doe", "email=user@example.com"])
        assert result == [
            {"name": "John Doe"},
            {"email": "user@example.com"},
        ]

    def test_uuid_values(self) -> None:
        """Test UUID values in key=value pairs."""
        uuid_value = "123e4567-e89b-12d3-a456-426614174000"
        result = parse_complex_list([f"userId={uuid_value}"])
        assert result == [{"userId": uuid_value}]

    def test_numeric_values_as_strings(self) -> None:
        """Test numeric values are preserved as strings."""
        result = parse_complex_list(["count=42", "price=99.99"])
        assert result == [{"count": "42"}, {"price": "99.99"}]

    def test_boolean_like_values(self) -> None:
        """Test boolean-like values are preserved as strings."""
        result = parse_complex_list(["enabled=true", "active=false"])
        assert result == [{"enabled": "true"}, {"active": "false"}]

    def test_missing_equals_sign(self) -> None:
        """Test that missing equals sign raises SystemExit."""
        stderr_capture = StringIO()
        original_stderr = sys.stderr
        sys.stderr = stderr_capture
        try:
            with pytest.raises(SystemExit):
                parse_complex_list(["roleviewer"])
        finally:
            sys.stderr = original_stderr
        # Check stderr after the exception is raised
        stderr_capture.seek(0)
        error_output = stderr_capture.read()
        assert "Invalid key=value pair" in error_output
        assert "roleviewer" in error_output

    def test_malformed_pair_no_equals(self) -> None:
        """Test that malformed pair without equals raises SystemExit."""
        stderr_capture = StringIO()
        original_stderr = sys.stderr
        sys.stderr = stderr_capture
        try:
            with pytest.raises(SystemExit):
                parse_complex_list(["role=viewer", "invalidpair"])
        finally:
            sys.stderr = original_stderr
        # Check stderr after the exception is raised
        stderr_capture.seek(0)
        error_output = stderr_capture.read()
        assert "Invalid key=value pair" in error_output
        assert "invalidpair" in error_output

    def test_empty_key(self) -> None:
        """Test that empty key is handled (edge case)."""
        stderr_capture = StringIO()
        original_stderr = sys.stderr
        sys.stderr = stderr_capture
        try:
            with pytest.raises(SystemExit):
                parse_complex_list(["role=viewer", "=value"])
        finally:
            sys.stderr = original_stderr
        # Check stderr after the exception is raised
        stderr_capture.seek(0)
        error_output = stderr_capture.read()
        assert "Invalid key=value pair" in error_output
        assert "=value" in error_output

    def test_empty_value(self) -> None:
        """Test that empty value is handled."""
        stderr_capture = StringIO()
        original_stderr = sys.stderr
        sys.stderr = stderr_capture
        try:
            with pytest.raises(SystemExit):
                parse_complex_list(["role=viewer", "key="])
        finally:
            sys.stderr = original_stderr
        # Check stderr after the exception is raised
        stderr_capture.seek(0)
        error_output = stderr_capture.read()
        assert "Invalid key=value pair" in error_output
        assert "key=" in error_output

    def test_multiple_equals_in_value(self) -> None:
        """Test that values can contain equals signs."""
        result = parse_complex_list(["expression=a=b=c"])
        assert result == [{"expression": "a=b=c"}]

    def test_complex_real_world_example(self) -> None:
        """Test a complex real-world example like albumUsers."""
        result = parse_complex_list(
            [
                "role=viewer,userId=123e4567-e89b-12d3-a456-426614174000",
                "role=editor,userId=987e6543-e21b-43d2-b654-321987654321",
            ]
        )
        assert result == [
            {
                "role": "viewer",
                "userId": "123e4567-e89b-12d3-a456-426614174000",
            },
            {
                "role": "editor",
                "userId": "987e6543-e21b-43d2-b654-321987654321",
            },
        ]

    def test_single_item_multiple_pairs(self) -> None:
        """Test single item with many key=value pairs."""
        result = parse_complex_list(["key1=value1,key2=value2,key3=value3,key4=value4"])
        assert result == [
            {
                "key1": "value1",
                "key2": "value2",
                "key3": "value3",
                "key4": "value4",
            }
        ]

    def test_whitespace_only_strings_skipped(self) -> None:
        """Test that whitespace-only strings are skipped."""
        result = parse_complex_list(["role=viewer", "   ", "\t", "userId=123"])
        assert result == [{"role": "viewer"}, {"userId": "123"}]
