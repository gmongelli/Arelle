'''
For each entry point of COREP and Solvency II taxonomies, the test will
create a new instance (in a tmp directory), display each table and compare
the cells with reference data and then close the report instance.
A flag can be manually set to create references.
'''
import os, sys
import unittest
import psutil
from tkinter import (Tk)
from arelle.CntlrWinMain import CntlrWinMain
from arelle.plugin import DevTesting
from arelle import (XbrlConst)
from arelle.PluginManager import pluginClassMethods
import json
from arelle.plugin.EbaCompliance import (EBA_ENTRY_POINTS_BY_VERSION_BY_REPORT_TYPE, EBA_TAXONOMY_VERSION_2_3_1)

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
            if version == EBA_TAXONOMY_VERSION_2_3_1:
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
        self.saveReferences = False # <- set this to create new references
        self.referencesDir = None
        self.cntlrWinMain = None
        self.process = psutil.Process(os.getpid())
        self.entryPointInfos = None
        self.maxSize = 0
        self.prevMemConsumed = 0
        self.testContext = None
    
    '''
    Run empty table layout comparison. Either on a specific report or a predefined seres of known reports
    '''
    def runTest(self, entryPointInfo=None):
        application = Tk()
        self.cntlrWinMain = CntlrWinMain(application)
        application.protocol("WM_DELETE_WINDOW", self.cntlrWinMain.quit)
        
        testDir = os.path.dirname(os.path.abspath(sys.modules[__name__].__file__))
        self.referencesDir = testDir + "/references/"        
        
        self.cntlrWinMain.setTestMode(True)
        # make sure we use a plugin loaded by the plugin manager!!
        for pluginMethod in pluginClassMethods("DevTesting.GetTestContext"):
            self.testContext = pluginMethod()
            break
        self.testContext.recordTableLayout = True
        self.testContext.saveFilePath = testDir + "/tmp/a1.xbrl"

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
        result = True
        testDataFilename = self.referencesDir + entryPointInfo.uniqueName + ".json"
        
        self.cntlrWinMain.fileOpenFile(entryPointInfo.entryPoint)
        
        testData = self.viewTables()
        
        memSize = self.process.memory_info()[0]
        if memSize > self.maxSize:
            self.maxSize = memSize
            
        self.cntlrWinMain.fileClose()
         
        memSize = self.process.memory_info()[0]
        diffMem = memSize - self.prevMemConsumed
        self.prevMemConsumed = memSize
    
        print("Memory consumed: " + DevTesting.humanizeSize(memSize) + " diff=" + DevTesting.humanizeSize(diffMem) + " max= " + DevTesting.humanizeSize(self.maxSize))
        assert memSize < 2000000000, "Check memory leaks regression: should never use 2Gb after instance close"
        
        if self.saveReferences:
            with open(testDataFilename, 'w') as outfile:
                json.dump(testData, outfile)
        else:
            with open(testDataFilename, 'r') as inputfile:
                refData = json.load(inputfile)
            # compare
            assert len(refData) == len(testData), "Not same number of tables " + entryPointInfo.uniqueName
            
            for tableEntry in sorted(refData.items()):
                tableName, refTableInfo = tableEntry
                testTableInfo = testData[tableName]
                assert len(testTableInfo) == len(refTableInfo), "Not same number of cells for table " + tableName + " " + entryPointInfo.uniqueName
                for idx in range(len(testTableInfo)):
                    ref = refTableInfo[idx]
                    tst = testTableInfo[idx]
                    msg = "Not same cell idx=" + str(idx) + " for table " + tableName + " " + entryPointInfo.uniqueName + " ref=" + ref + " tst=" + tst
                    if tst != ref:
                        print(msg)
                        result = False
                    #assert tst == ref, msg
        return result

    '''
    Up to now, we just capture partial cell creation information such
    as coordinates and header
    '''
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
    
class TestNewSaveViewClose(unittest.TestCase):
    def test(self):
        test = ThisTest()    
        test.saveReferences = False # <- set this to create new references
        
        if False:
            test.runTest(smallEntryPoint) # only this small one
        else:
            test.entryPointInfos = []
            if True:
                test.entryPointInfos.extend(getEbaEntryPoints())
            if True:
                test.entryPointInfos.extend(getSolvencyEntryPoints())
            test.runTest()
            
if __name__ == '__main__':
    unittest.main()

