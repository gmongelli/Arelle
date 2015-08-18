'''
For each sample Solvency II report instance (random populated instances), the test will
load the report, display each table and then close the report instance.
'''
import os, sys
import unittest
from os import listdir
from os.path import isfile, join
from tests.ViewHelper import ViewHelper, initUI, getTestDir

class SolvencySampleTest(unittest.TestCase):         
         
    def test(self):
        initUI(self)
        self.saveReferences = False # <- set this to create new references
        
        idx = 1
        numFailures = 0
        numEntries = len(self.getSolvencyFiles())
        for filepath in self.getSolvencyFiles():
            print(str(idx) + "/" + str(numEntries) + " " + os.path.basename(filepath))
            ok = self.processOneFile(filepath)
            if not(ok):
                numFailures += 1
            idx += 1
            
        assert numFailures == 0, "Number of failing instances: " + str(numFailures)    
        
    def processOneFile(self, filepath):
        self.cntlrWinMain.fileOpenFile(filepath)
               
        self.viewHelper = ViewHelper(self.cntlrWinMain.getModelXbrl(), self.testContext)
        testData = self.viewHelper.viewTables()
        
        self.cntlrWinMain.fileClose()

        result = self.viewHelper.compareTables(self.saveReferences, self.referencesDir, os.path.basename(filepath), testData)
        return result        

    def getSolvencyFiles(self):
        testDir = getTestDir()
        svcDir = testDir + "/solvency/2.0/random"
        files = [ f for f in listdir(svcDir) if isfile(join(svcDir, f)) ]
        result = []
        for f in sorted(files):
            result.append(join(svcDir, f))
        return result
    
if __name__ == '__main__':
    unittest.main()

