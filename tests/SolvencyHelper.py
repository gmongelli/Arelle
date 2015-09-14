
from os import listdir
from os.path import isfile, join
from tests.ViewHelper import getTestDir
from tests.CorepHelper import setGuiEnvironment

def getSolvencyFiles():
    testDir = getTestDir()
    svcDir = testDir + "/solvency/2.0/random"
    files = [ f for f in listdir(svcDir) if isfile(join(svcDir, f)) ]
    result = []
    for f in sorted(files):
        result.append(join(svcDir, f))
    return result

def setSolvencyGuiEnvironment(cntlrWinMain):
    # make sure we use the proper disclosure system for validation
    cntlrWinMain.config["disclosureSystem"] = "EIOPA Filing Rules"
 
    setGuiEnvironment(cntlrWinMain)
    
