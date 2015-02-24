'''
Inhibit the display of the taxonomy tabs (their rendering is slow).
This plug-in only works with AREBA, not with Arelle.

(c) Copyright 2015 Acsone S. A., All rights reserved.
'''

def disableDisplay():
    return False # by returning False, the display is disabled 

__pluginInfo__ = {
    'name': 'Disable the display of the taxonomy tabs',
    'version': '1.0',
    'description': "This module disables the display of the following tabs: presentation linkbase, fact list, table reandering, relationships.",
    'license': 'Apache-2',
    'author': 'Gregorio Mongelli (Acsone S. A.)',
    'copyright': '(c) Copyright 2015 Acsone S. A.',
    # classes of mount points (required)
    'CntlrWinMain.Tabs.DisplayTaxonomyTabs': disableDisplay
}