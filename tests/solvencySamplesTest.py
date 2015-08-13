'''
For each sample Solvency II report instance (random populated instances), the test will
load the report, display each table and then close the report instance.
'''
#TODO: create references and compare
import os, sys
import unittest
import psutil
from os import listdir
from os.path import isfile, join
from tkinter import (Tk)
from arelle.CntlrWinMain import CntlrWinMain
from arelle import (XbrlConst)
from arelle.PluginManager import pluginClassMethods

class SolvencySampleTest(unittest.TestCase):
         
    def test(self):
        self.cntlrWinMain = None
        self.process = psutil.Process(os.getpid())
        self.testContext = None
        
        application = Tk()
        self.cntlrWinMain = CntlrWinMain(application)
        application.protocol("WM_DELETE_WINDOW", self.cntlrWinMain.quit)
        
        self.cntlrWinMain.setTestMode(True)
        for pluginMethod in pluginClassMethods("DevTesting.GetTestContext"):
            self.testContext = pluginMethod()
            break
        self.testContext.recordTableLayout = True
        
        idx = 1
        numEntries = len(self.getSolvencyFiles())
        for filepath in self.getSolvencyFiles():
            print(str(idx) + "/" + str(numEntries) + " " + os.path.basename(filepath))
            self.processOneFile(filepath)
            idx += 1
            
        # No need to explicitly quit and consume events
        #self.cntlrWinMain.quit()
        #application.mainloop()
        
    def processOneFile(self, filepath):
        print("Processing " + filepath)
        self.cntlrWinMain.fileOpenFile(filepath)
               
        testData = self.viewTables()
        
        self.cntlrWinMain.fileClose()
        

    def viewTables(self):
        modelXbrl = self.cntlrWinMain.getModelXbrl()
        tableView = modelXbrl.guiViews.tableView
        tblRelSet = modelXbrl.relationshipSet("Table-rendering")
        tablesByName = {}
        for tblLinkroleUri in tblRelSet.linkRoleUris:
            for tableAxisArcrole in (XbrlConst.euTableAxis, XbrlConst.tableBreakdown, XbrlConst.tableBreakdownMMDD, XbrlConst.tableBreakdown201305, XbrlConst.tableBreakdown201301, XbrlConst.tableAxis2011):
                tblAxisRelSet = modelXbrl.relationshipSet(tableAxisArcrole, tblLinkroleUri)
                if tblAxisRelSet and len(tblAxisRelSet.modelRelationships) > 0:
                    # table name
                    modelRoleTypes = modelXbrl.roleTypes.get(tblLinkroleUri)
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
            
    def getSolvencyFiles(self):
        testDir = self.getTestDir()
        svcDir = testDir + "/solvency/2.0/random"
        files = [ f for f in listdir(svcDir) if isfile(join(svcDir, f)) ]
        result = []
        for f in sorted(files):
            result.append(join(svcDir, f))
        return result
    
    def getTestDir(self):
        return os.path.dirname(os.path.abspath(sys.modules[__name__].__file__))
            
if __name__ == '__main__':
    unittest.main()

