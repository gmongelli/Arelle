'''
Create a new report instance from an entry point and close several times,
checking memory consumption.
'''
import os,sys
import unittest
import psutil
from tkinter import (Tk)
from arelle.CntlrWinMain import CntlrWinMain
from pympler import (tracker)
from arelle.plugin import DevTesting
from arelle.PluginManager import pluginClassMethods

class TestNewSaveClose(unittest.TestCase):
    def test(self):
        process = psutil.Process(os.getpid())
        largeEntryPoint = "http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2014-05/2015-02-16/mod/corep_ind.xsd"
        smallEntryPoint = "http://eiopa.europa.eu/eu/xbrl/s2md/fws/solvency/solvency2/2015-05-31/mod/d1s.xsd"
        application = Tk()
        cntlrWinMain = CntlrWinMain(application)
        application.protocol("WM_DELETE_WINDOW", cntlrWinMain.quit)
        
        cntlrWinMain.setTestMode(True)
        for pluginMethod in pluginClassMethods("DevTesting.GetTestContext"):
            testContext = pluginMethod()
            break
        testContext.checkMemoryOnClose = True
        testDir = os.path.dirname(os.path.abspath(sys.modules[__name__].__file__))
        testContext.saveFilePath = testDir + "/tmp/a1.xbrl"
        testContext.dumpFilePrefix = testDir + "/tmp/dump_"
        
        tr = tracker.SummaryTracker()
        
        prevMemoryConsumed = 0
        
        for idx in range(4):
            print("\nIteration " + str(idx))
            cntlrWinMain.fileOpenFile(largeEntryPoint)
            maxSize = DevTesting.humanizeSize(process.memory_info()[0])
            cntlrWinMain.logClear()
            cntlrWinMain.fileClose()
        
            tr.print_diff()
            memoryConsumed = process.memory_info()[0]
            print("Memory consumed: " + DevTesting.humanizeSize(memoryConsumed) + " max= " + maxSize)
            diffMemeory = memoryConsumed - prevMemoryConsumed
            print(str(diffMemeory))
            if idx > 1:
                assert diffMemeory < 60000000, "Check memory leaks regression"
            prevMemoryConsumed = memoryConsumed
            
        # No need to explicitly quit and consume events
        #self.cntlrWinMain.quit()
        #application.mainloop()

if __name__ == '__main__':
    unittest.main()
