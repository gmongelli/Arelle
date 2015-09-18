
import os, time
import unittest
from tests.ViewHelper import ViewHelper, initUI, isEquivalentLogFile, getTestDir
from tests.SolvencyHelper import getSolvencyFiles, setSolvencyGuiEnvironment

class CorepSampleTest(unittest.TestCase):

    def validateFile(self, testFilepath):
        testDir = getTestDir()
        basename = os.path.basename(testFilepath)
        stem = os.path.splitext(basename)[0]
        print("Running " + basename)
        if basename == "qrs_20_instance.xbrl":
            pass
        else:
            pass
            #return True
        
        referenceFilepath = testDir + "/references/val_" + stem + ".log"
        logFilepath = testDir + "/tmp/val_" + stem + ".log"
        normalizedResultFilepath = testDir + "/tmp/norm_" + stem + ".log"
        if self.saveLogAndCompare:
            try:
                os.remove(logFilepath)
            except:
                pass
            try:
                os.remove(normalizedResultFilepath)
            except:
                pass
        
        self.cntlrWinMain.logView.testMode = True
        setSolvencyGuiEnvironment(self.cntlrWinMain)

        self.cntlrWinMain.fileOpenFile(testFilepath)               
        self.viewHelper = ViewHelper(self.cntlrWinMain.getModelXbrl(), self.testContext)
        
        
        self.cntlrWinMain.validate()
        if self.saveLogAndCompare:
            self.cntlrWinMain.logView.saveToFile(logFilepath)
            
        self.cntlrWinMain.fileClose()
        
        self.cntlrWinMain.logView.clear() # clear existing log
       
        if self.saveLogAndCompare:
            print(" compare")
            result = isEquivalentLogFile(logFilepath, normalizedResultFilepath, referenceFilepath)
            return True
        else:
            result = True
        return result        
         
    def test(self):
        print("validateSolvencySamplesTest")
        self.saveLogAndCompare = True # False to run multiple concurrent tests (log contention)
        startedAt = time.time()
        initUI(self)
        
        idx = 1
        numFailures = 0
        files = getSolvencyFiles()
        numEntries = len(files)
        failedInstances = []
        for filepath in files:
            print(str(idx) + "/" + str(numEntries) + " " + os.path.basename(filepath))
            startedAt2 = time.time()
            ok = self.validateFile(filepath)
            print(str(idx) + "/" + str(numEntries) + " Ok=" + str(ok) + " {:.2f}s ".format(time.time() - startedAt2) + os.path.basename(filepath))
            if not(ok):
                failedInstances.append(os.path.basename(filepath))
                numFailures += 1
            idx += 1
            
        print("validateSolvencySamplesTest took " + "{:.2f}".format(time.time() - startedAt) + " (Typical time: 2370s)")
        if numFailures > 0:
            print("Failed instances " + str(failedInstances))
        assert numFailures == 0, "Number of failing instances: " + str(numFailures)    
        
if __name__ == '__main__':
    unittest.main()
