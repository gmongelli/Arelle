from os import listdir
from os.path import isfile, join
from tests.ViewHelper import getTestDir

def getCorepFiles():
    testDir = getTestDir()
    svcDir = testDir + "/eba/2.3.1"
    files = [ f for f in listdir(svcDir) if isfile(join(svcDir, f)) ]
    result = []
    for f in sorted(files):
        result.append(join(svcDir, f))
    svcDir = testDir + "/eba/other"
    files = [ f for f in listdir(svcDir) if isfile(join(svcDir, f)) ]
    for f in sorted(files):
        result.append(join(svcDir, f))
    return result

