from modules.case.framework import TestCaseBuilder


def test_strip_json_comments_with_single_line_comments():
    """Test that single-line comments starting with '#' are correctly removed."""
    data_with_single_line_comments = """
    {
        "key": "value" # This is a comment
        , "another_key": "another_value" # Another comment
    }
    """
    cleaned_data = TestCaseBuilder._strip_json_comments(data_with_single_line_comments)
    # Check that comments are removed
    assert "# This is a comment" not in cleaned_data
    assert "# Another comment" not in cleaned_data
    # Check that actual JSON is intact
    assert '"key": "value"' in cleaned_data
    assert '"another_key": "another_value"' in cleaned_data


def test_strip_json_comments_no_comments():
    """Test that JSON data with no comments remains unchanged."""
    data_no_comments = """{\n"key": "value",\n"another_key": "another_value"\n}"""
    cleaned_data = TestCaseBuilder._strip_json_comments(data_no_comments)
    # Assert that the data remains unchanged
    assert data_no_comments.strip() == cleaned_data.strip()

def test_strip_json_comments_empty_data():
    """Test that an empty string returns an empty string."""
    empty_data = ""
    cleaned_data = TestCaseBuilder._strip_json_comments(empty_data)
    assert cleaned_data == ""

def test_strip_json_comments_multiple_line_comment():
    """Test that a single-line comment is correctly stripped."""
    single_line_comment = """
    # comment
    {
        "key": "value" ## Single-line comment
    }
    """
    cleaned_data = TestCaseBuilder._strip_json_comments(single_line_comment)
    assert "## Single-line comment" not in cleaned_data
    assert '"key": "value"' in cleaned_data

def test_strip_json_comments_outside_line_comment():
    """Test that a single-line comment is correctly stripped."""
    single_line_comment = """
    # comment
    {
        "key": "value" 
    }
    """
    cleaned_data = TestCaseBuilder._strip_json_comments(single_line_comment)
    assert "## Single-line comment" not in cleaned_data
    assert '"key": "value"' in cleaned_data

def test_strip_json_comments_outside_line_and_no_space_comment():
    """Test that a single-line comment is correctly stripped."""
    single_line_comment = """
# comment
{
    "key": "value" 
}
"""
    cleaned_data = TestCaseBuilder._strip_json_comments(single_line_comment)
    assert "## Single-line comment" not in cleaned_data
    assert '"key": "value"' in cleaned_data