'''
For each entry point of COREP and Solvency II taxonomies, the test will
create a new instance (in a tmp directory), display each table and compare
the cells with reference data and then close the report instance.
A flag can be manually set to create references.
'''
import os, time
import unittest
from arelle.plugin import DevTesting
from arelle.plugin.EbaCompliance import (EBA_ENTRY_POINTS_BY_VERSION_BY_REPORT_TYPE, EBA_TAXONOMY_VERSION_2_3_1, EBA_TAXONOMY_VERSION_2_4)
from tests.ViewHelper import ViewHelper, initUI
from tests.CorepHelper import setCorepGuiEnvironment
from tests.SolvencyHelper import setSolvencyGuiEnvironment

#TODO: CAUTION: this test should be adapted to setup proper config parameters...
#      (I lost a couple of hours figuring out why disabled cells were no more shown as
#       such after some modifs and the loss of my original config.
#       e.g. Ignore dimensional validity should not be checked 

'''
Information about a report entry point
'''
class EntryPointInfo:
    def __init__(self, version, reportType, reportName, entryPoint):
        self.version = version
        self.reportType = reportType
        self.reportName = reportName
        self.entryPoint = entryPoint
        basef = os.path.basename(entryPoint)
        # unique name used to create a reference result file
        self.uniqueName = version + "_" + reportType + "_" + os.path.splitext(basef)[0]
    
# small entry point used to test the test    
smallEntryPoint = EntryPointInfo("2.0", "sv", "03 - Day 1 Solvency II reporting Solo", "http://eiopa.europa.eu/eu/xbrl/s2md/fws/solvency/solvency2/2015-07-31/mod/d1s.xsd")
#smallEntryPoint = EntryPointInfo("2.0", "sv", "01 - Annual Solvency II reporting Solo", "http://eiopa.europa.eu/eu/xbrl/s2md/fws/solvency/solvency2/2015-07-31/mod/ars.xsd")

'''
EBA entry points are taken from from a plugin where they are already listed
'''
def getEbaEntryPoints():
    entryPointInfos = []
    for reportType, v in sorted(EBA_ENTRY_POINTS_BY_VERSION_BY_REPORT_TYPE.items()):
        for version, entry in sorted(v.items()):
            # too much when all versions...
            if version == EBA_TAXONOMY_VERSION_2_4 or version == EBA_TAXONOMY_VERSION_2_3_1:
                for reportName, entryPoint in entry.items():
                    entryPointInfos.append(EntryPointInfo(version, reportType, reportName, entryPoint))
    return entryPointInfos


def getSolvencyEntryPoints():
    entryPointInfos = []
    version = "2.0"
    reportType = "sv"
    entryPointInfos.append(EntryPointInfo(version, reportType, "01 - Annual Solvency II reporting Solo", "http://eiopa.europa.eu/eu/xbrl/s2md/fws/solvency/solvency2/2015-07-31/mod/ars.xsd"))
    entryPointInfos.append(EntryPointInfo(version, reportType, "02 - Quarterly Solvency II reporting Solo", "http://eiopa.europa.eu/eu/xbrl/s2md/fws/solvency/solvency2/2015-07-31/mod/qrs.xsd"))
    entryPointInfos.append(EntryPointInfo(version, reportType, "03 - Day 1 Solvency II reporting Solo", "http://eiopa.europa.eu/eu/xbrl/s2md/fws/solvency/solvency2/2015-07-31/mod/d1s.xsd"))
    entryPointInfos.append(EntryPointInfo(version, reportType, "04 - Annual Solvency II reporting Group", "http://eiopa.europa.eu/eu/xbrl/s2md/fws/solvency/solvency2/2015-07-31/mod/arg.xsd"))
    entryPointInfos.append(EntryPointInfo(version, reportType, "05 - Quarterly Solvency II reporting Group", "http://eiopa.europa.eu/eu/xbrl/s2md/fws/solvency/solvency2/2015-07-31/mod/qrg.xsd"))
    entryPointInfos.append(EntryPointInfo(version, reportType, "06 - Day 1 Solvency II reporting Group", "http://eiopa.europa.eu/eu/xbrl/s2md/fws/solvency/solvency2/2015-07-31/mod/d1g.xsd"))
    entryPointInfos.append(EntryPointInfo(version, reportType, "07 - Annual Solvency II reporting Third country branches", "http://eiopa.europa.eu/eu/xbrl/s2md/fws/solvency/solvency2/2015-07-31/mod/arb.xsd"))
    entryPointInfos.append(EntryPointInfo(version, reportType, "08 - Quarterly Solvency II reporting Third country branches", "http://eiopa.europa.eu/eu/xbrl/s2md/fws/solvency/solvency2/2015-07-31/mod/qrb.xsd"))
    entryPointInfos.append(EntryPointInfo(version, reportType, "09 - Day 1 Solvency II reporting Third country branches", "http://eiopa.europa.eu/eu/xbrl/s2md/fws/solvency/solvency2/2015-07-31/mod/d1b.xsd"))
    entryPointInfos.append(EntryPointInfo(version, reportType, "10 - Annual Financial Stability reporting Solo", "http://eiopa.europa.eu/eu/xbrl/s2md/fws/solvency/solvency2/2015-07-31/mod/afs.xsd"))
    entryPointInfos.append(EntryPointInfo(version, reportType, "11 - Quarterly Financial Stability reporting Solo", "http://eiopa.europa.eu/eu/xbrl/s2md/fws/solvency/solvency2/2015-07-31/mod/qfs.xsd"))
    entryPointInfos.append(EntryPointInfo(version, reportType, "12 - Annual Financial Stability reporting Group", "http://eiopa.europa.eu/eu/xbrl/s2md/fws/solvency/solvency2/2015-07-31/mod/afg.xsd"))
    entryPointInfos.append(EntryPointInfo(version, reportType, "13 - Quarterly Financial Stability reporting Group", "http://eiopa.europa.eu/eu/xbrl/s2md/fws/solvency/solvency2/2015-07-31/mod/qfg.xsd"))
    entryPointInfos.append(EntryPointInfo(version, reportType, "14 - FS 3CB Individual Annual", "http://eiopa.europa.eu/eu/xbrl/s2md/fws/solvency/solvency2/2015-07-31/mod/ats.xsd"))
    entryPointInfos.append(EntryPointInfo(version, reportType, "15 - FS 3CB Individual Quarterly", "http://eiopa.europa.eu/eu/xbrl/s2md/fws/solvency/solvency2/2015-07-31/mod/qts.xsd"))
    entryPointInfos.append(EntryPointInfo(version, reportType, "16 - Annual ECB reporting Solo", "http://eiopa.europa.eu/eu/xbrl/s2md/fws/solvency/solvency2/2015-07-31/mod/aes.xsd"))
    entryPointInfos.append(EntryPointInfo(version, reportType, "17 - Quarterly ECB reporting Solo", "http://eiopa.europa.eu/eu/xbrl/s2md/fws/solvency/solvency2/2015-07-31/mod/qes.xsd"))
    entryPointInfos.append(EntryPointInfo(version, reportType, "18 - Annual ECB reporting Third country branches", "http://eiopa.europa.eu/eu/xbrl/s2md/fws/solvency/solvency2/2015-07-31/mod/aeb.xsd"))
    entryPointInfos.append(EntryPointInfo(version, reportType, "19 - Quarterly ECB reporting Third country branches", "http://eiopa.europa.eu/eu/xbrl/s2md/fws/solvency/solvency2/2015-07-31/mod/qeb.xsd"))
    entryPointInfos.append(EntryPointInfo(version, reportType, "20 - Annual reporting Special Purpose Vehicles", "http://eiopa.europa.eu/eu/xbrl/s2md/fws/solvency/solvency2/2015-07-31/mod/spv.xsd"))
    return entryPointInfos

     
class ThisTest:
    def __init__(self):
        pass
    
    '''
    Run empty table layout comparison. Either on a specific report or a predefined seres of known reports
    '''
    def runTest(self, entryPointInfo=None):
        startedAt = time.time()

        numFailures = 0
        if entryPointInfo is None:
            idx = 1
            numEntries = len(self.entryPointInfos)
            for entryPointInfo in self.entryPointInfos:
                print(str(idx) + "/" + str(numEntries) + " " + entryPointInfo.reportName + " " + entryPointInfo.uniqueName)
                ok = self.processOneEntryPoint(entryPointInfo)
                if not(ok):
                    numFailures += 1
                idx += 1
        else:
            ok = self.processOneEntryPoint(entryPointInfo)
            if not(ok):
                numFailures += 1
        
        # No need to explicitly quit and consume events
        #self.cntlrWinMain.quit()
        #application.mainloop()
        assert numFailures == 0, "Number of failing entry points: " + str(numFailures)    
    
    '''
    Load report, draw each table and compare layout with references for the specified report entry point
    returns True if result is OK
    '''
    def processOneEntryPoint(self, entryPointInfo):
        self.cntlrWinMain.fileOpenFile(entryPointInfo.entryPoint)

        self.viewHelper = ViewHelper(self.cntlrWinMain.getModelXbrl(), self.testContext)
        
        testData = self.viewHelper.viewTables()
        
        memSize = self.process.memory_info()[0]
        if memSize > self.maxSize:
            self.maxSize = memSize
            
        self.cntlrWinMain.fileClose()
         
        memSize = self.process.memory_info()[0]
        diffMem = memSize - self.prevMemConsumed
        self.prevMemConsumed = memSize
    
        print("Memory consumed: " + DevTesting.humanizeSize(memSize) + " diff=" + DevTesting.humanizeSize(diffMem) + " max= " + DevTesting.humanizeSize(self.maxSize))
        assert memSize < 2000000000, "Check memory leaks regression: should never use 2Gb after instance close"
        
        result = self.viewHelper.compareTables(self.saveReferences, self.referencesDir, entryPointInfo.uniqueName, testData)
        return result

class TestNewSaveViewClose(unittest.TestCase):
    def test(self):
        print("newSaveViewClose")
        test = ThisTest()
        initUI(test)  
        test.saveReferences = False # <- set this to create new references
        startedAt = time.time()
        
        if False:
            test.runTest(smallEntryPoint) # only this small one
        else:            
            if True:
                setCorepGuiEnvironment(test.cntlrWinMain)
                test.entryPointInfos = []
                test.entryPointInfos.extend(getEbaEntryPoints())
                test.runTest()
            if True:
                setSolvencyGuiEnvironment(test.cntlrWinMain)
                test.entryPointInfos = []
                test.entryPointInfos.extend(getSolvencyEntryPoints())
                test.runTest()
        print("newSaveViewClose took " + "{:.2f}".format(time.time() - startedAt) + " (Typical time: 2396s")
            
if __name__ == '__main__':
    unittest.main()

