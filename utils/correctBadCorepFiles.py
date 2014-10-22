'''
Correct old COREP files XML Schema definition files.

Some files missed to include the validation error messages.
This stand-alone Python program tries to correct them.
It requires two arguments:
1. The directory where the XML Schema can be found.
   The program will set that directory as the current directory.
2. The name of the XML Schema to be corrected.

The original file will be copied to a new file with the same name, but
with the prefix '.bak'

(c) Copyright 2014 Acsone S. A., All rights reserved.
'''

import os
import sys
try:
    from lxml import etree
except ImportError:
    try:
        # Python 2.5
        import xml.etree.cElementTree as etree
    except ImportError:
        try:
            # Python 2.5
            import xml.etree.ElementTree as etree
        except ImportError:
            try:
                # normal cElementTree install
                import cElementTree as etree
            except ImportError:
                try:
                    # normal ElementTree install
                    import elementtree.ElementTree as etree
                except ImportError:
                    print("Failed to import ElementTree from any known place")

class EbaXmlSchemaCorrector:
    def __init__(self, dirPath, xsdFile):
        '''
        :type dirPath: str
        :type xsdFile: str
        '''
        self.dirPath = dirPath
        self.xsdFile = xsdFile
        self.xsdBackup = "%s.bak" % self.xsdFile
        self.xmlTree = None

    def changeDirectory(self):
        os.chdir(self.dirPath)

    def renameFile(self):
        os.rename(self.xsdFile, self.xsdBackup)

    def getCompanionFileName(self, href):
        '''
        :type href: str
        :rtype str
        '''
        suffix = '-lab-en.xml'
        if href.endswith(suffix):
            return '%s-err-en.xml' % href[:(len(href)-len(suffix))]
        else:
            return None

    def companionFileExists(self, companionFilename):
        '''
        :type companionFilename: str
        '''
        if companionFilename is not None:
            xpathExpression = \
              "//link:linkbaseRef[@xlink:href='%s']" % companionFilename
            nsDeclarations = {'link' : 'http://www.xbrl.org/2003/linkbase',
                              'xlink':'http://www.w3.org/1999/xlink'}
            if os.path.isfile(companionFilename) \
             and len(self.xmlTree.xpath(xpathExpression,
                                        namespaces = nsDeclarations)) == 0:
                return True
            else:
                return False
        return False

    def addCompanionFile(self, elem, companionFileName):
        '''
        :type elem: etree.Element
        :type companionFileName: str
        '''
        parent = elem.getparent()
        attributes = {'{http://www.w3.org/1999/xlink}href': companionFileName,
                      '{http://www.w3.org/1999/xlink}type': 'simple',
                      '{http://www.w3.org/1999/xlink}arcrole': 'http://www.w3.org/1999/xlink/properties/linkbase'}
        child = etree.Element("{http://www.xbrl.org/2003/linkbase}linkbaseRef",
                              attributes)
        parent.insert(parent.index(elem)+1, child)

    def parseFile(self):
        # Load XML Schema
        self.xmlTree = etree.parse(self.xsdBackup)
        # Find all linkbase elements
        for elem in self.xmlTree.findall('.//{http://www.xbrl.org/2003/linkbase}linkbaseRef'):
            href = elem.get('{http://www.w3.org/1999/xlink}href')
            companionFileName = self.getCompanionFileName(href)
            if self.companionFileExists(companionFileName):
                self.addCompanionFile(elem, companionFileName)

    def saveResultToFile(self):
        with open(self.xsdFile, 'bw') as file_handle:
            result = etree.tostring(self.xmlTree, pretty_print=True, encoding='utf8')
            file_handle.write(result)

    def run(self):
        self.changeDirectory()
        self.renameFile()
        self.parseFile()
        self.saveResultToFile()

def main(argv=None):
    if argv is None:
        argv = sys.argv
    if len(argv)<3:
        print('Usage: correctBadCorepFiles.py <directory_name> <file_name>')
        return 1
    corrector = EbaXmlSchemaCorrector(argv[1], argv[2])
    corrector.run()
    return 0

if __name__ == "__main__":
    sys.exit(main())