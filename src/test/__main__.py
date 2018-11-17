from os import path
import pytest


def main():
    pytest.main([
        path.join(path.dirname(__file__), "unit")
    ])


if __name__ == "__main__":
    main()
