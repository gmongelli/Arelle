'''
This test runs the following standard test suites:
XBRL2.1
dimensions
formula
function registry
edgar
table linkbase
'''
#TODO: check/compare reports
import os,sys   
import unittest   
from arelle.CntlrCmdLine import parseAndRun

class ConformanceTests(unittest.TestCase):
    def testXbrl21(self):
        testDir = self.getTestDir()
        
        testSuite = testDir + "/test_suites/xbrl2.1/XBRL-CONF-2014-12-10.zip/XBRL-CONF-2014-12-10/xbrl.xml"
        print("Running " + testSuite)
        
        csvReport = testDir + "/tmp/XBRL-CONF-2014-12-10-report.csv"
        logFile = testDir + "/tmp/XBRL-CONF-2014-12-10-log.txt"
        
        arelleRunArgs = ['--validate', '--calcPrecision', '--csvTestReport', csvReport, '--logFile', 'logToStdErr', '--logfile', logFile, '--file', testSuite]
        parseAndRun(arelleRunArgs)
        
    def testXdt(self):
        testDir = self.getTestDir()
        
        testSuite = testDir + "/test_suites/dimensions_1.0/xdt-conf-cr4-2009-10-06.zip/xdt.xml"
        print("Running " + testSuite)
        
        csvReport = testDir + "/tmp/xdt-conf-cr4-2009-10-06-report.csv"
        logFile = testDir + "/tmp/xdt-conf-cr4-2009-10-06-log.txt"
        
        arelleRunArgs = ['--validate', '--infoset', '--csvTestReport', csvReport, '--logFile', 'logToStdErr', '--logfile', logFile, '--file', testSuite]
        parseAndRun(arelleRunArgs)
        
    def testFormula(self):
        testDir = self.getTestDir()
        
        testSuite = testDir + "/test_suites/formula_1.0/Formula-CONF-REC-2013-09-12.zip/conformance-formula/index.xml"
        print("Running " + testSuite)
        
        csvReport = testDir + "/tmp/Formula-CONF-REC-2013-09-12-report.csv"
        logFile = testDir + "/tmp/Formula-CONF-REC-2013-09-12-log.txt"
        
        arelleRunArgs = ['--validate', '--csvTestReport', csvReport, '--logFile', 'logToStdErr', '--logfile', logFile, '--file', testSuite]
        parseAndRun(arelleRunArgs)
        
    def testFunctions(self):
        testDir = self.getTestDir()
        
        testSuite = testDir + "/test_suites/formula_1.0/Formula-CONF-REC-2013-09-12.zip/conformance-formula/function-registry/functionregistry.xml"
        print("Running " + testSuite)
        
        csvReport = testDir + "/tmp/functionregistry-report.csv"
        logFile = testDir + "/tmp/functionregistry-log.txt"
        
        arelleRunArgs = ['--validate', '--csvTestReport', csvReport, '--logFile', 'logToStdErr', '--logfile', logFile, '--file', testSuite]
        parseAndRun(arelleRunArgs)
        
    def testEdgarFiler(self):
        testDir = self.getTestDir()
        
        testSuite = testDir + "/test_suites/edgar/efm-31-150505.zip/conf/testcases.xml"
        print("Running " + testSuite)
        
        csvReport = testDir + "/tmp/efm-31-150505-report.csv"
        logFile = testDir + "/tmp/efm-31-150505-log.txt"
        
        arelleRunArgs = ['--efm', '--validate', '--csvTestReport', csvReport, '--logFile', 'logToStdErr', '--logfile', logFile, '--file', testSuite]
        parseAndRun(arelleRunArgs)
        
    def testTableLinkbase(self):
        testDir = self.getTestDir()
        
        testSuite = testDir + "/test_suites/table_linkbase_1.0/table-linkbase-conf-2014-03-18.zip/table-linkbase-conf-2014-03-18\conf/testcases-index.xml"
        print("Running " + testSuite)
        
        csvReport = testDir + "/tmp/table-linkbase-conf-2014-03-18-report.csv"
        logFile = testDir + "/tmp/table-linkbase-conf-2014-03-18-log.txt"
        
        arelleRunArgs = ['--validate', '--csvTestReport', csvReport, '--logFile', 'logToStdErr', '--logfile', logFile, '--file', testSuite]
        parseAndRun(arelleRunArgs)
        
    def getTestDir(self):
        return os.path.dirname(os.path.abspath(sys.modules[__name__].__file__))

if __name__ == '__main__':
    unittest.main()
