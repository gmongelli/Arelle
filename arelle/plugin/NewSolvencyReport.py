'''
(c) Copyright 2014, 2015 Acsone S. A., All rights reserved.
'''

from arelle import PackageManager
    
TAXONOMY_NAME = 'EIOPA Solvency II XBRL Taxonomy 2.0.0'

def customNewFile(cntlr):
    for i, packageInfo in enumerate(sorted(PackageManager.packagesConfig.get("packages", []),
                                           key=lambda packageInfo: packageInfo.get("name")),
                                    start=1):
        name = packageInfo.get("name", "package{}".format(i))
        URL = packageInfo.get("URL")
        if name and URL and packageInfo.get("status") == "enabled":
            if name == TAXONOMY_NAME:
                cntlr.fileOpenFile(URL)
                return
    cntlr.modelManager.showStatus("Solvency Taxonomy package not found: " + TAXONOMY_NAME, 5000)

def fileOpenExtender(cntlr, menu):
    menu.add_command(label=_('New Solvency Report'), underline=0, command=lambda: customNewFile(cntlr) )

__pluginInfo__ = {
    'name': 'New SolvencyReport 2.0',
    'version': '1.1',
    'description': "Open the report selection dialog using the latest SolvencyII taxonomy",
    'license': 'Apache-2',
    'author': 'acsone',
    'copyright': '(c) Copyright 2014, 2015 Acsone S. A.',
    # classes of mount points (required)
    'CntlrWinMain.Menu.File.Open': fileOpenExtender
}
