from typy.typst_encoder import TypstEncoder


def test_list():
    list = ["test", "test2"]
    assert TypstEncoder.encode(list) == '("test", "test2",)'

    list2 = [1]
    assert TypstEncoder.encode(list2) == "(1,)"


def test_str():
    str = "test"
    assert TypstEncoder.encode(str) == "test"

    str2 = "test test"
    assert TypstEncoder.encode(str2) == "test test"

    str3 = "test test test"
    assert TypstEncoder.encode(str3) == "test test test"

    str4 = "test\ntest"
    assert TypstEncoder.encode(str4) == "test\ntest"

    str5 = 'test "test"'
    assert TypstEncoder.encode(str5) == 'test "test"'
