'''
For each sample Solvency II report instance (random populated instances), the test will
load the report, display each table and then close the report instance.
'''
import os, time
import unittest
from tests.ViewHelper import ViewHelper, initUI
from tests.SolvencyHelper import getSolvencyFiles

class SolvencySampleTest(unittest.TestCase):         
         
    def test(self):
        print("SolvencySampleTest")
        startedAt = time.time()
        initUI(self)
        self.saveReferences = False  # <- set this to create new references
        
        idx = 1
        numFailures = 0
        solvencyFiles = getSolvencyFiles()
        numEntries = len(solvencyFiles)
        for filepath in solvencyFiles:
            print(str(idx) + "/" + str(numEntries) + " " + os.path.basename(filepath))
            ok = self.processOneFile(filepath)
            if not(ok):
                numFailures += 1
            idx += 1
        print("SolvencySampleTest took " + "{:.2f}".format(time.time() - startedAt) + " (Typical time: 4610s")
        assert numFailures == 0, "Number of failing instances: " + str(numFailures)    
        
    def processOneFile(self, filepath):
        self.cntlrWinMain.fileOpenFile(filepath)
               
        self.viewHelper = ViewHelper(self.cntlrWinMain.getModelXbrl(), self.testContext)
        testData = self.viewHelper.viewTables()
        
        self.cntlrWinMain.fileClose()

        result = self.viewHelper.compareTables(self.saveReferences, self.referencesDir, os.path.basename(filepath), testData)
        return result        

if __name__ == '__main__':
    unittest.main()

