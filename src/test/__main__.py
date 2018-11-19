from os import path
import pytest
import sys

def main():
    return  # Test is not enable because we use prompt_toolkit
    
    if "quiet" in sys.argv:
        pytest.main(["-q",
                     path.join(path.dirname(__file__), "unit")
                     ])
    else:
        pytest.main([
            path.join(path.dirname(__file__), "unit")
        ])


if __name__ == "__main__":
    main()
