import pytest

from pytest_metaexport import decorators as m


def test_undecorated():
    assert True


def test_undecorated_fail():
    assert False


@m.title("Successful login")
def test_arbitrary_decorator_title():
    assert True


@m.foo("some value")
def test_dynamic_decorator_foo():
    assert True


@m.tags(["a", "b"])
def test_tags():
    assert True


# this should cause an error because we're trying to overwrite a protected field
# @m.status("failed")
# def test_status_overwrite():
#     assert True


# this should cause an error because we're trying to overwrite a protected field
# @m.duration("not a number")
# def test_duration_overwrite():
#     assert True


@m.bar("baz")
@m.title("parametrize test")
@pytest.mark.parametrize("a", [1, 2])
def test_parametrize(a: int):
    assert True


@pytest.mark.parametrize("a, b", [(1, 8), (9, 3)])
def test_parametrize_two(a: int, b: int):
    assert True


@pytest.mark.parametrize("value", [1, 2])
@pytest.mark.parametrize("multiplier", [2, 3])
def test_multi_parametrize(value: int, multiplier: int):
    assert True


@pytest.mark.skip()
def test_skip():
    assert False


class TestClassStructure:
    def test_a(self):
        assert True


@m.description("foo bar baz a b c")
def test_description():
    "nothing here"
    assert True
