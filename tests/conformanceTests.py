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

class ConformanceTests(unittest.TestCase):
    def testXbrl21(self):
        testDir = self.getTestDir()
        
        testSuite = testDir + "/test_suites/xbrl2.1/XBRL-CONF-2014-12-10.zip/XBRL-CONF-2014-12-10/xbrl.xml"
        print("Running " + testSuite)
        
        reportFilename = "XBRL-CONF-2014-12-10-report.csv"
        csvReport = testDir + "/tmp/" + reportFilename
        logFile = testDir + "/tmp/XBRL-CONF-2014-12-10-log.txt"
        
        arelleRunArgs = ['--validate', '--calcPrecision', '--csvTestReport', csvReport, '--logFile', 'logToStdErr', '--logfile', logFile, '--file', testSuite]
        parseAndRun(arelleRunArgs)
        
        assert isSameFileContent(csvReport, testDir + "/references/" + reportFilename)
        
    def testXdt(self):
        testDir = self.getTestDir()
        
        testSuite = testDir + "/test_suites/dimensions_1.0/xdt-conf-cr4-2009-10-06.zip/xdt.xml"
        print("Running " + testSuite)
        
        reportFilename = "xdt-conf-cr4-2009-10-06-report.csv"
        csvReport = testDir + "/tmp/" + reportFilename
        logFile = testDir + "/tmp/xdt-conf-cr4-2009-10-06-log.txt"
        
        arelleRunArgs = ['--validate', '--infoset', '--csvTestReport', csvReport, '--logFile', 'logToStdErr', '--logfile', logFile, '--file', testSuite]
        parseAndRun(arelleRunArgs)
        
        assert isSameFileContent(csvReport, testDir + "/references/" + reportFilename)
        
    def testFormula(self):
        testDir = self.getTestDir()
        
        testSuite = testDir + "/test_suites/formula_1.0/Formula-CONF-REC-2013-09-12.zip/conformance-formula/index.xml"
        print("Running " + testSuite)
        
        reportFilename = "Formula-CONF-REC-2013-09-12-report.csv"
        csvReport = testDir + "/tmp/" + reportFilename
        logFile = testDir + "/tmp/Formula-CONF-REC-2013-09-12-log.txt"
        
        arelleRunArgs = ['--validate', '--csvTestReport', csvReport, '--logFile', 'logToStdErr', '--logfile', logFile, '--file', testSuite]
        parseAndRun(arelleRunArgs)
        
        assert isSameFileContent(csvReport, testDir + "/references/" + reportFilename)
        
    def testFunctions(self):
        testDir = self.getTestDir()
        
        testSuite = testDir + "/test_suites/formula_1.0/Formula-CONF-REC-2013-09-12.zip/conformance-formula/function-registry/functionregistry.xml"
        print("Running " + testSuite)
        
        reportFilename = "functionregistry-report.csv"
        csvReport = testDir + "/tmp/" + reportFilename
        logFile = testDir + "/tmp/functionregistry-log.txt"
        
        arelleRunArgs = ['--validate', '--csvTestReport', csvReport, '--logFile', 'logToStdErr', '--logfile', logFile, '--file', testSuite]
        parseAndRun(arelleRunArgs)
        
        assert isSameFileContent(csvReport, testDir + "/references/" + reportFilename)
        
    def testEdgarFiler(self):
        testDir = self.getTestDir()
        
        testSuite = testDir + "/test_suites/edgar/efm-31-150505.zip/conf/testcases.xml"
        print("Running " + testSuite)
        
        reportFilename = "efm-31-150505-report.csv"
        csvReport = testDir + "/tmp/" + reportFilename
        logFile = testDir + "/tmp/efm-31-150505-log.txt"
        
        arelleRunArgs = ['--efm', '--validate', '--csvTestReport', csvReport, '--logFile', 'logToStdErr', '--logfile', logFile, '--file', testSuite]
        parseAndRun(arelleRunArgs)
        
        assert isSameFileContent(csvReport, testDir + "/references/" + reportFilename)
        
    def testTableLinkbase(self):
        testDir = self.getTestDir()
        
        testSuite = testDir + "/test_suites/table_linkbase_1.0/table-linkbase-conf-2014-03-18.zip/table-linkbase-conf-2014-03-18\conf/testcases-index.xml"
        print("Running " + testSuite)
        
        reportFilename = "table-linkbase-conf-2014-03-18-report.csv"
        csvReport = testDir + "/tmp/" + reportFilename
        logFile = testDir + "/tmp/table-linkbase-conf-2014-03-18-log.txt"
        
        arelleRunArgs = ['--validate', '--csvTestReport', csvReport, '--logFile', 'logToStdErr', '--logfile', logFile, '--file', testSuite]
        parseAndRun(arelleRunArgs)
        
        assert isSameFileContent(csvReport, testDir + "/references/" + reportFilename)
       
    def getTestDir(self):
        return os.path.dirname(os.path.abspath(sys.modules[__name__].__file__))

if __name__ == '__main__':
    unittest.main()
