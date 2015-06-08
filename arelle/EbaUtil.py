'''
Miscellaneous functions that are useful for the EBA compliance checks.

(c) Copyright 2015 Acsone S. A., All rights reserved.
'''

from arelle import ModelDocument, ModelXbrl
from lxml import etree
from arelle.ViewWinRenderedGrid import ViewRenderedGrid
from arelle.DialogNewFactItem import getNewFactItemOptions
from arelle.ModelValue import qname

EbaURL = "www.eba.europa.eu/xbrl"
EiopaURL = "eiopa.europa.eu/xbrl"

qnFindFilingIndicators = qname("{http://www.eurofiling.info/xbrl/ext/filing-indicators}find:fIndicators")
qnFindFilingIndicator = qname("{http://www.eurofiling.info/xbrl/ext/filing-indicators}find:filingIndicator")

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

def old_isEbaInstance(modelXbrl, checkAlsoEiopa=False):
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
    
def isEbaInstance(modelXbrl, checkAlsoEiopa=False):
    for urlDoc in modelXbrl.urlDocs.values():
        if "www.eba.europa.eu" in urlDoc.uri:
            return True
        elif checkAlsoEiopa and "eiopa.europa.eu" in urlDoc.uri:
            return True
    
def loadFilingIndicators(modelXbrl):
    # Note: when creating a new instance with the "new EBA file" menu, the model
    #       strangely appears to be based on a INSTANCE document model type
    #       So, stamp the proper type anyway otherwise the indicators won't be saved
    #       if we save right after
    # => Now we don't need to save a new EBA file immediately anymore (as indicated in AREBA WIKI tricks and tips)
    modelXbrl.modelDocument.type = ModelDocument.Type.INSTANCE
    
    filingIndicatorsElements = modelXbrl.factsByQname(qnFindFilingIndicators, set())
    for fIndicators in filingIndicatorsElements:
        # print(str(fIndicators))
        for fIndicator in fIndicators.modelTupleFacts:
            filingIndicatorCode = (fIndicator.xValue or fIndicator.value)
            filedTable = fIndicator.get("{http://www.eurofiling.info/xbrl/ext/filing-indicators}filed", "true") in ("true", "1")
            # print(str(tableIdentifier) + " " + str(filedTable))
            if filedTable:
                filingIndicator = True
            else:
                filingIndicator = False
            modelXbrl.filingIndicatorByTableFilingCode[filingIndicatorCode] = filingIndicator
            
def updateFilingIndicator(modelXbrl, tableLabel, filingIndicator):
    modelXbrl.modelDocument.type = ModelDocument.Type.INSTANCE # see note above (just in case)
    
    filingIndicatorsElements = modelXbrl.factsByQname(qnFindFilingIndicators, set())
    if len(filingIndicatorsElements) > 0:
        for fIndicators in filingIndicatorsElements:
            for fIndicator in fIndicators.modelTupleFacts:
                tableIdentifier = fIndicator.stringValue
                if tableLabel == tableIdentifier:
                    setFilingIndicatorValue(modelXbrl, fIndicator, filingIndicator)
                    if filingIndicator == None:
                        fIndicators.modelTupleFacts.remove(fIndicator)
                        parent = fIndicator.parentElement
                        parent.remove(fIndicator)
                        # we may leave an invalid empty container in case we
                        # just deleted the last one, but don't care since
                        # it doesn't make any sense to file no table at all
                        # (this may not be OK in case of multiple container)
                    return
        # indicator not found for this table
        filingIndicatorsElement = filingIndicatorsElements.pop()
    else:
        # no container yet
        newFactItemOptions = getFactItemOptions(modelXbrl, modelXbrl.modelManager.cntlr)
        filingIndicatorsElement = createFilingIndicatorsElement(modelXbrl, newFactItemOptions)
                
    # create indicator fact
    fIndicator = modelXbrl.createFact(qnFindFilingIndicator, 
                   parent=filingIndicatorsElement,
                   attributes={"contextRef": "c"}, 
                   text=tableLabel,
                   validate=False)
    setFilingIndicatorValue(modelXbrl, fIndicator, filingIndicator)
    
def setFilingIndicatorValue(modelXbrl, fIndicator, filingIndicator):
    pname = "{http://www.eurofiling.info/xbrl/ext/filing-indicators}filed"
    if filingIndicator:                            
        fIndicator.set(pname, "true")
    elif filingIndicator == False:
        fIndicator.set(pname, "false")
    else:
        modelXbrl.factsInInstance.remove(fIndicator)
        modelXbrl.factIndex.deleteFact(fIndicator)
    modelXbrl.setIsModified()
    
def createFilingIndicatorsElement(modelXbrl, newFactItemOptions):
    modelXbrl.createContext(newFactItemOptions.entityIdentScheme,
                      newFactItemOptions.entityIdentValue,
                      'instant',
                      None,
                      newFactItemOptions.endDateDate,
                      None, # no dimensional validity checking (like formula does)
                      {}, [], [],
                      id='c',
                      afterSibling=ModelXbrl.AUTO_LOCATE_ELEMENT)
    filingIndicatorsTuple = modelXbrl.createFact(qnFindFilingIndicators, validate=False)
    return filingIndicatorsTuple
        
    