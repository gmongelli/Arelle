'''
Miscellaneous functions that are useful for the EBA compliance checks.

(c) Copyright 2015 Acsone S. A., All rights reserved.
'''

from arelle import ModelDocument
from lxml import etree
from arelle.ViewWinRenderedGrid import ViewRenderedGrid
from arelle.DialogNewFactItem import getNewFactItemOptions

EbaURL = "www.eba.europa.eu/xbrl"
EiopaURL = "eiopa.europa.eu/xbrl"

def getFactItemOptions(dts, cntlr):
    newFactItemOptions = None
    for view in dts.views:
        if isinstance(view, ViewRenderedGrid):
            if (not view.newFactItemOptions.entityIdentScheme or  # not initialized yet
            not view.newFactItemOptions.entityIdentValue or
            not view.newFactItemOptions.monetaryUnit or
            not view.newFactItemOptions.startDateDate or not view.newFactItemOptions.endDateDate):
                if not getNewFactItemOptions(cntlr, view.newFactItemOptions):
                    return None
            newFactItemOptions = view.newFactItemOptions
            break
    return newFactItemOptions

def isEbaInstance(modelXbrl, checkAlsoEiopa=False):
    if modelXbrl.modelDocument.type == ModelDocument.Type.INSTANCE:
        doc = modelXbrl.modelDocument.xmlDocument
        for el in doc.iter("*"):
            if isinstance(el, etree._Element):
                for _, NS in _DICT_SET(el.nsmap.items()):  # @UndefinedVariable
                    if EbaURL in NS:
                        return True
                    elif checkAlsoEiopa and EiopaURL in NS:
                        return True
        return False
    else:
        return False