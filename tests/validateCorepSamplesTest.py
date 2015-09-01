
import os, time
import unittest
from tests.ViewHelper import ViewHelper, initUI, isEquivalentLogFile, getTestDir
from tests.CorepSampleFiles import getCorepFiles

class CorepSampleTest(unittest.TestCase):

    def validateFile(self, testFilepath):
        testDir = getTestDir()
        basename = os.path.basename(testFilepath)
        stem = os.path.splitext(basename)[0]
        print("Running " + basename)
        if basename == "COFREP-P99999999-2014-09-SCOREP-00-L-N-I-SCOREP.xbrl":
            pass
            #return True
        else:
            pass
            #return True
        
        logFilepath = testDir + "/tmp/val_" + stem + ".log"
        try:
            os.remove(logFilepath)
        except:
            pass
        referenceFilepath = testDir + "/references/val_" + stem + ".log"
        normalizedResultFilepath = testDir + "/tmp/norm_" + stem + ".log"
        try:
            os.remove(normalizedResultFilepath)
        except:
            pass
        
        self.cntlrWinMain.logView.testMode = True
        self.cntlrWinMain.fileOpenFile(testFilepath)               
        self.viewHelper = ViewHelper(self.cntlrWinMain.getModelXbrl(), self.testContext)
        
        print(" validate")
        self.cntlrWinMain.validate()
        self.cntlrWinMain.logView.saveToFile(logFilepath)
        
        self.cntlrWinMain.fileClose()
        
        self.cntlrWinMain.logView.clear() # clear existing log
       
        print(" compare")
        result = isEquivalentLogFile(logFilepath, normalizedResultFilepath, referenceFilepath)
        return result        
         
    def test(self):
        startedAt = time.time()
        initUI(self)
        
        idx = 1
        numFailures = 0
        corepFiles = getCorepFiles()
        numEntries = len(corepFiles)
        for filepath in corepFiles:
            print(str(idx) + "/" + str(numEntries) + " " + os.path.basename(filepath))
            startedAt2 = time.time()
            ok = self.validateFile(filepath)
            print(str(idx) + "/" + str(numEntries) + " Ok=" + str(ok) + " {:.2f}s ".format(time.time() - startedAt2) + os.path.basename(filepath))
            if not(ok):
                numFailures += 1
            idx += 1
            
        print("validateCorepSamplesTest took " + "{:.2f}".format(time.time() - startedAt) + " (Typical time: 4252s/4789s/5249s/5438s)")
        assert numFailures == 0, "Number of failing instances: " + str(numFailures)    
        
if __name__ == '__main__':
    unittest.main()

