from typing import List
import difflib
import sys
import os

if len(sys.argv) < 3:
    exit(-1)
expectedFile, realFile = sys.argv[1], sys.argv[2]
expectedData: List[str] = []
realData: List[str] = []
with open(expectedFile, "r", encoding='utf-8') as f:
    expectedData = f.readlines()
with open(realFile, "r", encoding='utf-8') as f:
    realData = f.readlines()

# Remove space at line end
expectedData = [x.rstrip() for x in expectedData]
realData = [x.rstrip() for x in realData]

diff = difflib.unified_diff(expectedData, realData, fromfile=os.path.split(
    expectedFile)[-1], tofile=os.path.split(realFile)[-1], lineterm="")

ls = list(diff)
if ls:
    print("\n".join(ls))
    exit(1)
else:
    exit(0)
