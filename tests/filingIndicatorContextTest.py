
import unittest
from tests.ViewHelper import ViewHelper, initUI, getTestDir
from arelle.plugin.EbaCompliance import improveEbaCompliance

class FilingIndicatoContextTest(unittest.TestCase):

    def test(self):
        initUI(self)
        testDir = getTestDir()
        inputFilePath = testDir + "/eba/2.3.1_v/corep_liqui.xbrl"
        
        print("Load file")
        self.cntlrWinMain.logView.testMode = True
        self.cntlrWinMain.fileOpenFile(inputFilePath)               
        self.viewHelper = ViewHelper(self.cntlrWinMain.getModelXbrl(), self.testContext)
        
        print("Validate the instance containing the error")
        self.cntlrWinMain.validate()
        entries = self.cntlrWinMain.logView.getEntries()
        msgPrefix = "[EBA.2.13] Contexts must have the same date"
        errorFound = False
        for entry in entries:
            if str(entry).startswith(msgPrefix):
                print(str(entry))
                errorFound = True
        assert errorFound, "This error message should be issued by the validation: " + msgPrefix
        
        self.cntlrWinMain.logView.clear() # clear existing log
        print("improve EBA compliance to clean context dates")
        improveEbaCompliance(self.cntlrWinMain.getModelXbrl(), self.cntlrWinMain)
        
        print("validate again to check the error is gone")
        self.cntlrWinMain.validate()
        entries = self.cntlrWinMain.logView.getEntries()
        msgPrefix = "[EBA.2.13] Contexts must have the same date"
        errorFound = False
        for entry in entries:
            if str(entry).startswith(msgPrefix):
                errorFound = True
                
        assert not(errorFound), "Context date not fixed"
        
        
if __name__ == '__main__':
    unittest.main()

