from importlib.metadata import version

import typy


def test_package_version_matches_distribution_metadata():
    assert typy.__version__ == version("typy")
