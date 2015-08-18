
import os, sys
import json
import psutil
from tkinter import (Tk)
from arelle.CntlrWinMain import CntlrWinMain
from arelle.PluginManager import pluginClassMethods
from arelle.ViewWinRenderedGrid import getTableAxisArcroles

def initUI(testObject):
    testObject.saveReferences = False # <- set this to create new references
    testObject.referencesDir = None
    testObject.cntlrWinMain = None
    testObject.process = psutil.Process(os.getpid())
    testObject.entryPointInfos = None
    testObject.maxSize = 0
    testObject.prevMemConsumed = 0
    testObject.testContext = None
    testObject.viewHelper = None
    
    testObject.application = Tk()
    testObject.cntlrWinMain = CntlrWinMain(testObject.application)
    testObject.application.protocol("WM_DELETE_WINDOW", testObject.cntlrWinMain.quit)
    
    testDir = os.path.dirname(os.path.abspath(sys.modules[__name__].__file__))
    testObject.referencesDir = testDir + "/references/"        
    
    testObject.cntlrWinMain.setTestMode(True)
    # make sure we use a plugin loaded by the plugin manager!!
    for pluginMethod in pluginClassMethods("DevTesting.GetTestContext"):
        testObject.testContext = pluginMethod()
        break
    testObject.testContext.recordTableLayout = True
    testObject.testContext.saveFilePath = testDir + "/tmp/a1.xbrl"        

def getTestDir():
    return os.path.dirname(os.path.abspath(sys.modules[__name__].__file__))

def isSameFileContent(resultFilePath, referenceFilePath):
    if os.path.getsize(resultFilePath) == os.path.getsize(referenceFilePath):
        if open(resultFilePath, 'r').read() == open(referenceFilePath, 'r').read():
            return True
    return False  
            
    
class ViewHelper:
    def __init__(self, modelXbrl, testContext):
        self.modelXbrl = modelXbrl
        self.testContext = testContext
        
    '''
    Up to now, we just capture partial cell creation information such
    as coordinates and header
    '''
    def viewTables(self):
        tableView = self.modelXbrl.guiViews.tableView
        tblRelSet = self.modelXbrl.relationshipSet("Table-rendering")
        tablesByName = {}
        for tblLinkroleUri in tblRelSet.linkRoleUris:
            for tableAxisArcrole in getTableAxisArcroles():
                tblAxisRelSet = self.modelXbrl.relationshipSet(tableAxisArcrole, tblLinkroleUri)
                if tblAxisRelSet and len(tblAxisRelSet.modelRelationships) > 0:
                    # table name
                    modelRoleTypes = self.modelXbrl.roleTypes.get(tblLinkroleUri)
                    if modelRoleTypes is not None and len(modelRoleTypes) > 0:
                        roledefinition = modelRoleTypes[0].definition
                        if roledefinition is None or roledefinition == "":
                            roledefinition = os.path.basename(tblLinkroleUri)       
                        for table in tblAxisRelSet.rootConcepts:
                            tablesByName[roledefinition] = (tblLinkroleUri, table)
                            break
        testData = {} # table layout info by table name
        for tableEntry in sorted(tablesByName.items()):
            tableName, tpl = tableEntry
            tblLinkroleUri, table = tpl
            print(tableName)
            
            self.testContext.tableLayout.tableInfo = []
            tableView.view(viewTblELR=tblLinkroleUri)
            testData[tableName] = self.testContext.tableLayout.tableInfo
        return testData    

    def compareTables(self, saveReferences, referencesDir, filename, testData):
        testDataFilename = referencesDir + filename + ".json"
        result = True
        if saveReferences:
            with open(testDataFilename, 'w') as outfile:
                json.dump(testData, outfile)
        else:
            with open(testDataFilename, 'r') as inputfile:
                refData = json.load(inputfile)
            # compare
            assert len(refData) == len(testData), "Not same number of tables " + filename
            
            for tableEntry in sorted(refData.items()):
                tableName, refTableInfo = tableEntry
                testTableInfo = testData[tableName]
                assert len(testTableInfo) == len(refTableInfo), "Not same number of cells for table " + tableName + " " + filename
                for idx in range(len(testTableInfo)):
                    ref = refTableInfo[idx]
                    tst = testTableInfo[idx]
                    msg = "Not same cell idx=" + str(idx) + " for table " + tableName + " " + filename + " ref=" + ref + " tst=" + tst
                    if tst != ref:
                        print(msg)
                        result = False
                    #assert tst == ref, msg
        return result
    
        