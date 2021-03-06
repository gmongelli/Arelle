'''
(c) Copyright 2014, 2015 Acsone S. A., All rights reserved.
'''
import os
from arelle.PackageManager import parsePackage, packagesConfig
from arelle.FileSource import openFileSource
    
TAXONOMY_NAME = 'EIOPA Solvency II XBRL Taxonomy 2.0.0'

def customNewFile(cntlr):
    packageInfo = getCurrentEnabledTaxonomyPackageInfo()
    if packageInfo is not None:
        URL = packageInfo.get("URL")
        cntlr.fileOpenFile(URL)
        return
    cntlr.modelManager.showStatus("Solvency Taxonomy package not found: " + TAXONOMY_NAME, 5000)
    
def getCurrentEnabledTaxonomyPackageInfo():
    for i, packageInfo in enumerate(sorted(packagesConfig.get("packages", []),
                                           key=lambda packageInfo: packageInfo.get("name")),
                                    start=1):
        name = packageInfo.get("name", "package{}".format(i))
        URL = packageInfo.get("URL")
        if name and URL and packageInfo.get("status") == "enabled":
            if name == TAXONOMY_NAME:
                return packageInfo
    return None
    
def getReportNameFromEntryPoint(cntlr, entryPoint):
    packageInfo = getCurrentEnabledTaxonomyPackageInfo()
    if packageInfo is not None:
        URL = packageInfo.get("URL")
        filesource = openFileSource(URL, cntlr=cntlr) 
        filenames = filesource.dir
        if filenames is not None:   # an IO or other error can return None
            metadataFiles = filesource.taxonomyPackageMetadataFiles
            metadataFile = metadataFiles[0]
            metadata = filesource.url + os.sep + metadataFile
            taxonomyPackage = parsePackage(cntlr, filesource, metadata,
                                                os.sep.join(os.path.split(metadata)[:-1]) + os.sep)
            nameToUrls = taxonomyPackage["nameToUrls"]
            for reportName, reportInfo in nameToUrls.items():
                if reportInfo[1] == entryPoint:
                    return reportName
    return None                 

def fileOpenExtender(cntlr, menu):
    menu.add_command(label=_('New Solvency Report...'), underline=0, command=lambda: customNewFile(cntlr) )

__pluginInfo__ = {
    'name': 'New SolvencyReport 2.0',
    'version': '1.2',
    'description': '''New 'File' menu entry called 'New Solvency Report...' that opens a report selection dialog
using the latest Solvency II taxonomy''',
    'license': 'Apache-2',
    'author': 'Acsone S. A.',
    'copyright': '(c) Copyright 2014, 2015 Acsone S. A.',
    # classes of mount points (required)
    'CntlrWinMain.Menu.File.Open': fileOpenExtender,
    'GetReportNameFromEntryPoint': getReportNameFromEntryPoint
}
