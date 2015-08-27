'''
This test runs the following standard test suites:
XBRL2.1
dimensions
formula
function registry
edgar
table linkbase
'''
import os,sys   
import unittest   
from arelle.CntlrCmdLine import parseAndRun
from tests.ViewHelper import isSameFileContent

testXbrl21 = True
testXdt = True
testFormula = True
testFunctions = True
testEdgarFiler = True
testTableLinkbase = True

class ConformanceTests(unittest.TestCase):
    
    def runSuite(self, suite, reportFilename, logf, additionalOptions=None):
        testDir = self.getTestDir()
        testSuite = testDir + "/" + suite
        print("Running " + testSuite)
        
        csvReport = testDir + "/tmp/" + reportFilename
        logFile = testDir + "/tmp/" + logf
        try:
            os.remove(csvReport)
        except:
            pass
        try:
            os.remove(logFile)
        except:
            pass
        
        arelleRunArgs = ['--csvTestReport', csvReport, '--logFile', 'logToStdErr', '--logfile', logFile, '--file', testSuite]
        if additionalOptions is not None:
            arelleRunArgs.extend(additionalOptions)
        parseAndRun(arelleRunArgs)
        
        # Here we compare the whole report to a reference
        # (at least we should have the same statuses (pass,fail,valied...)
        assert isSameFileContent(csvReport, testDir + "/references/" + reportFilename)        
    
    def testXbrl21(self):
        if testXbrl21:
            print("Caution: as for 'official arelle', some tests may fail/pass from one run to another (v08-s-equal-with-scenario-sub-element-attributes-reordered or InferCalculatedValueConsistencyWithScenarioAttributeDefaultValid)")
            
            self.runSuite( "test_suites/xbrl2.1/XBRL-CONF-2014-12-10.zip/XBRL-CONF-2014-12-10/xbrl.xml",
                           "XBRL-CONF-2014-12-10-report.csv", "XBRL-CONF-2014-12-10-log.txt",
                           additionalOptions=['--validate', '--calcPrecision'])
        
    def testXdt(self):
        if testXdt:
            self.runSuite( "test_suites/dimensions_1.0/xdt-conf-cr4-2009-10-06.zip/xdt.xml",
                           "xdt-conf-cr4-2009-10-06-report.csv", "xdt-conf-cr4-2009-10-06-log.txt",
                           additionalOptions=['--validate', '--infoset'])
   
    def testFormula(self):
        if testFormula:
            print("Caution: formula test suite still shows report diffs due to non-deterministic order of Expected and Actual column contents")
            
            self.runSuite( "test_suites/formula_1.0/Formula-CONF-REC-2013-09-12.zip/conformance-formula/index.xml",
                           "Formula-CONF-REC-2013-09-12-report.csv", "functionregistry-log.txt",
                           additionalOptions=['--validate'])
   
    def testFunctions(self):
        if testFunctions:
            self.runSuite( "test_suites/formula_1.0/Formula-CONF-REC-2013-09-12.zip/conformance-formula/function-registry/functionregistry.xml",
                           "functionregistry-report.csv", "functionregistry-log.txt",
                           additionalOptions=['--validate'])
        
    def testEdgarFiler(self):
        if testEdgarFiler:
            self.runSuite( "test_suites/edgar/efm-31-150505.zip/conf/testcases.xml",
                           "efm-31-150505-report.csv", "efm-31-150505-log.txt",
                           additionalOptions=['--efm', '--validate'])
        
    def testTableLinkbase(self):
        if testTableLinkbase:
            self.runSuite( "test_suites/table_linkbase_1.0/table-linkbase-conf-2014-03-18.zip/table-linkbase-conf-2014-03-18\conf/testcases-index.xml",
                           "table-linkbase-conf-2014-03-18-report.csv", "table-linkbase-conf-2014-03-18-log.txt",
                           additionalOptions=['--validate'])
 
    def getTestDir(self):
        return os.path.dirname(os.path.abspath(sys.modules[__name__].__file__))

if __name__ == '__main__':
    unittest.main()
