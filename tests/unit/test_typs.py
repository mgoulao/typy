

from typy.typst_encoder import TypstEncoder


def test_list():
    list = ["test", "test2"]
    assert TypstEncoder.encode(list) == "(test, test2,)"

    list2 = [1]
    assert TypstEncoder.encode(list2) == "(1,)"
