
import os,sys   
import unittest   
import gc
from arelle.CntlrCmdLine import parseAndRun
import arelle.ModelValue
from pympler import (tracker,muppy,refbrowser)

class TestOpenClose(unittest.TestCase):
    def test(self):
        tr = tracker.SummaryTracker()
        testDir = os.path.dirname(os.path.abspath(sys.modules[__name__].__file__))
        testFileSmall = testDir + "/solvency/2.0/random/spv_20_instance.xbrl"
        logFile = testDir + "/tmp/test.log"
        dumpFilePrefix = testDir + "/tmp/dump_"
        
        prevNumObjects = 0
        for idx in range(3): # increase this range for testing
            print("\nIteration " + str(idx))
            arelleRunArgs = ['--keepOpen', '--logFile', 'logToStdErr', '--logfile', logFile, '--file', testFileSmall]
            cntlr = parseAndRun(arelleRunArgs)
            cntlr.modelManager.close()
            cntlr.close()
            del cntlr
        
            gc.collect()
            all_objects = muppy.get_objects()
            numObjects = len(all_objects)
            diffObjects = numObjects - prevNumObjects
            prevNumObjects = numObjects
            print(str(numObjects) + " (" + str(diffObjects) + " more)")
            browserRoot = None
            if False:  # <<<--- set this to get object dump file
                with open(dumpFilePrefix + str(idx) + ".txt", "w") as text_file:
                    idx = 0
                    for o in all_objects:
                        if browserRoot is None and isinstance(o, arelle.ModelValue.QName):
                            browserRoot = o
                        idx += 1
                        otype = ""
                        try:
                            otype = str(type(o))
                        except:
                            pass
                        try:
                            print("type=" + otype + " " + str(o), file=text_file)
                        except:
                            pass
            if False:
                ibrowser = refbrowser.InteractiveBrowser(browserRoot)
                ibrowser.main()
            all_objects= None
            gc.collect()
            tr.print_diff()
            if idx > 1:
                assert diffObjects < 50, "Check for new objects leak"  

if __name__ == '__main__':
    unittest.main()
