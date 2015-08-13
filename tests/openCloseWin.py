'''
Open and close several times an XBRL instance and check memory consumption.
This is done using the graphical (tkinter based) controller.
On instance close, garbage is collected and it is possible to trigger a dump of
objects in memory for comparison between runs. The pympler tracker gives
stats about objects differences between runs.
See DevTesting plugin for more information.
'''
import os, sys
from tkinter import (Tk)
import unittest
from arelle.CntlrWinMain import CntlrWinMain
from pympler import (tracker)
from arelle.PluginManager import pluginClassMethods

class TestOpenCloseWin(unittest.TestCase):
    def test(self):
        testDir = os.path.dirname(os.path.abspath(sys.modules[__name__].__file__))
        testFileSmall = testDir + "/solvency/2.0/random/spv_20_instance.xbrl"
        application = Tk()
        cntlrWinMain = CntlrWinMain(application)
        application.protocol("WM_DELETE_WINDOW", cntlrWinMain.quit)
        
        cntlrWinMain.setTestMode(True)
        for pluginMethod in pluginClassMethods("DevTesting.GetTestContext"):
            testContext = pluginMethod()
            break
        testContext.checkMemoryOnClose = True
        testContext.dumpFilePrefix = testDir + "/tmp/dump_"
        
        tr = tracker.SummaryTracker()
        
        for idx in range(4):
            print("\nIteration " + str(idx))
            cntlrWinMain.fileOpenFile(testFileSmall)
            cntlrWinMain.logClear()
            cntlrWinMain.fileClose()    
            
            tr.print_diff()  
            if idx > 1:
                assert testContext.diffNumObjects < 3000, "Check for new objects leak"  
        
        #cntlrWinMain.quit()
        #application.mainloop()            

if __name__ == '__main__':
    unittest.main()
    