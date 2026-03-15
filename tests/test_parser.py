from src.parser import parse_log_text


def test_parse_valid_lines():
    text = "\n".join(
        [
            "11:43:51.902 >latitude:20.706118",
            "11:43:51.902 >longitude:-103.337013",
            "11:43:51.904 >altitude:1506.80",
            "11:43:51.904 >satellites:12",
        ]
    )

    result = parse_log_text(text)

    assert result.total_lines == 4
    assert result.parsed_lines == 4
    assert result.invalid_lines == []
    assert not result.long_df.empty
    assert "timestamp" in result.wide_df.columns
    assert "latitude" in result.wide_df.columns
    assert "longitude" in result.wide_df.columns


def test_parse_ignores_invalid_lines():
    text = "\n".join(
        [
            "bad line",
            "11:43:51.902 >latitude:20.706118",
            "11:43:51.902 >longitude:-103.337013",
            "11:43:51.90 >broken:12",
        ]
    )

    result = parse_log_text(text)

    assert result.total_lines == 4
    assert result.parsed_lines == 2
    assert result.invalid_lines == [1, 4]
