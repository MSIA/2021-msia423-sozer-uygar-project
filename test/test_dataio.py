from src.dataio import parse_s3


def test_parse_s3():
    input = "s3://2012-uygar/file-path/path/to/file"

    test = parse_s3(input)

    true = ("2012-uygar", "file-path/path/to/file")

    assert test == true


def test_parse_s3_nonstr():
    input = sum

    test = parse_s3(input)

    assert test == (None, None)
