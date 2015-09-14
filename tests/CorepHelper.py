from os import listdir
from os.path import isfile, join
from tests.ViewHelper import getTestDir
from arelle.ModelFormulaObject import FormulaOptions

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

def setCorepGuiEnvironment(cntlrWinMain):
    # make sure we use the proper disclosure system for validation
    cntlrWinMain.config["disclosureSystem"] = "EBA Filing Rules"
    setGuiEnvironment(cntlrWinMain)
    
def setGuiEnvironment(cntlrWinMain):   
    cntlrWinMain.modelManager.validateDisclosureSystem = True
    cntlrWinMain.config["validateDisclosureSystem"] = True

    cntlrWinMain.modelManager.validateCalcLB = True
    cntlrWinMain.config["validateCalcLB"] = True
    
    cntlrWinMain.modelManager.validateInferDecimals = True
    cntlrWinMain.config["validateInferDecimals"] = True

    cntlrWinMain.modelManager.validateUtr = True
    cntlrWinMain.config["validateUtr"] = True

    formulaOptions = FormulaOptions()
    formulaOptions.errorUnsatisfiedAssertions = True
    cntlrWinMain.modelManager.formulaOptions = formulaOptions
    cntlrWinMain.config["formulaParameters"] = formulaOptions.__dict__.copy()

    options = cntlrWinMain.config.setdefault("viewRenderedGridOptions", {})
    options.setdefault("openBreakdownLines", 1)
    options.setdefault("ignoreDimValidity", False)
    options.setdefault("xAxisChildrenFirst", False)
    options.setdefault("yAxisChildrenFirst", False)
    
    # Caution: active formulae specific to a report not set here
    
    #cntlrWinMain.saveConfig()
    cntlrWinMain.setValidateTooltipText()

