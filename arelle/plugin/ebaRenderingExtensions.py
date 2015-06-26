'''
EBA & EIPOA rendering extensions

(c) Copyright 2015 Acsone S. A., All rights reserved.
'''
from arelle.ModelValue import qname
import arelle.EbaUtil as EbaUtil

qnFindFilingIndicators = qname("{http://www.eurofiling.info/xbrl/ext/filing-indicators}find:fIndicators")

# Note: Load and Update filing indicators are spread in two different plugins so that the load can be used in non-GUI mode
 
def checkUpdateFilingIndicator(roledefinition, modelXbrl):
    '''
    :type modelXbrl: ModelXbrl
    :type roledefinition: string
    :rtype (boolean)
    '''    
    #check whether the current table has a None filing indicator and if so, set it to True
    for tableLabel, filingCode in modelXbrl.filingCodeByTableLabel.items():
        if roledefinition.startswith(filingCode):
            if not filingCode in modelXbrl.filingIndicatorByFilingCode or modelXbrl.filingIndicatorByFilingCode[filingCode] == None:
                filingIndicator = True
                modelXbrl.filingIndicatorByFilingCode[filingCode] = filingIndicator
                filingIndicatorDisplay = str(filingIndicator)
                EbaUtil.updateFilingIndicator(modelXbrl, filingCode, filingIndicator)  
                for tableLabel, filingCode in modelXbrl.filingCodeByTableLabel.items():
                    if roledefinition.startswith(filingCode):
                        treeRowId = modelXbrl.treeRowByTableLabel[tableLabel]
                        modelXbrl.indexTableTreeView.set(treeRowId, 0, filingIndicatorDisplay)
                # continue looping since we may have more than one table per filing indicator
    return True
       
def setFiling(viewtree, modelXbrl, filingIndicator):
    '''
    :type viewtree: ViewTree
    :type modelXbrl: ModelXbrl
    :type filingIndicator: boolean
    :rtype boolean
    '''    
    # Set filing indicator in second row of tables index
    # The indicator is a tri-state value
    item = viewtree.treeView.item(viewtree.menuRow)
    label = item.get('text')
    if not label in modelXbrl.filingCodeByTableLabel:
        return
    filingIndicatorCode = modelXbrl.filingCodeByTableLabel[label]
    if not filingIndicatorCode in modelXbrl.filingIndicatorByFilingCode:
        return
    filingIndicatorDisplay = getFilingIndicatorDisplay(filingIndicator)
    # maintain the indicator value in the instance model
    modelXbrl.filingIndicatorByFilingCode[filingIndicatorCode] = filingIndicator
    for tableLabel, fcode in modelXbrl.filingCodeByTableLabel.items():
        if fcode == filingIndicatorCode:
            treeRowId = modelXbrl.treeRowByTableLabel[tableLabel]
            viewtree.treeView.set(treeRowId, 0, filingIndicatorDisplay)
    
    EbaUtil.updateFilingIndicator(modelXbrl, filingIndicatorCode, filingIndicator)  
    return True

def renderConcept(isModelTable, concept, conceptText, viewRelationshipSet, modelXbrl, conceptNode):
    '''
    :type isModelTable: ViewTree
    :type concept: Concept
    :type conceptText: string
    :type viewRelationshipSet: ViewRelationshipSet
    :type modelXbrl: ModelXbrl
    :type conceptNode: ViewRelationshipSet
    :rtype boolean
    '''    
    if not isModelTable:
        return True
    # in case we are rendering a table in a EBA document instance,
    # also prepare the filing indicator
    # Note: several table views can have the same filing indicator
    filingIndicator = None
    defaultENLanguage = "en"
    filingIndicatorCodeRole = "http://www.eurofiling.info/xbrl/role/filing-indicator-code";
    filingIndicatorCode = concept.genLabel(role=filingIndicatorCodeRole,
                                          lang=defaultENLanguage)
    if viewRelationshipSet.isEbaTableIndex:
        isModelTable = True
        if not filingIndicatorCode in modelXbrl.filingIndicatorByFilingCode:
            filingIndicator = None
            modelXbrl.filingIndicatorByFilingCode[filingIndicatorCode] = filingIndicator
        else:
            filingIndicator = modelXbrl.filingIndicatorByFilingCode[filingIndicatorCode]
        modelXbrl.filingCodeByTableLabel[conceptText] = filingIndicatorCode
        viewRelationshipSet.treeView.set(conceptNode, 0, getFilingIndicatorDisplay(filingIndicator))
        modelXbrl.treeRowByTableLabel[conceptText] = conceptNode
        modelXbrl.indexTableTreeView = viewRelationshipSet.treeView

def getFilingIndicatorDisplay(filingIndicator):
    if filingIndicator == None:
        filingIndicatorDisplay = ""
    else:
        filingIndicatorDisplay = "Yes" if filingIndicator else "No"
    return filingIndicatorDisplay
    
def saveNewFileFromGUI(cntlrWinMain):
    '''
    :type cntlrWinMain: CntlrWinMain
    :rtype boolean
    '''    
    # Note: when creating a new instance with the "new EBA file" menu, the model
    #       strangely appears not to be based on an INSTANCE document model type
    # => Force a save file immediately so that the user won't forget anymore (as indicated in AREBA WIKI tricks and tips)
    saved = cntlrWinMain.fileSave()
    return (True, saved)
    
        
__pluginInfo__ = {
    'name': 'EBA Rendering extensions',
    'version': '1.0',
    'description': "This plugin contains GUI extensions for EBA and EIOPA (e.g update of filing indicators)",
    'license': 'Apache-2',
    'author': 'Acsone',
    'copyright': '(c) Copyright 2015 Acsone S. A.',
    # classes of mount points (required)
    'CntlrWinMain.Rendering.CheckUpdateFilingIndicator': checkUpdateFilingIndicator,
    'CntlrWinMain.Rendering.SetFilingIndicator': setFiling,
    'CntlrWinMain.Rendering.RenderConcept': renderConcept,
    'CntlrWinMain.Rendering.SaveNewFileFromGUI': saveNewFileFromGUI
}