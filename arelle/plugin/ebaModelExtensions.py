'''
EBA Model extensions (load filing indicators etc)

(c) Copyright 2015 Acsone S. A., All rights reserved.
'''
from arelle.ModelValue import qname

qnFindFilingIndicators = qname("{http://www.eurofiling.info/xbrl/ext/filing-indicators}find:fIndicators")

# Note: Load and Update filing indicators are spread in two different plugins so that the load can be used in non-GUI mode

def loadFilingIndicators(modelXbrl):
    '''
    :type modelXbrl: ModelXbrl
    :rtype boolean
    '''    
    filingIndicatorsElements = modelXbrl.factsByQname(qnFindFilingIndicators, set())
    for fIndicators in filingIndicatorsElements:
        for fIndicator in fIndicators.modelTupleFacts:
            filingIndicatorCode = (fIndicator.xValue or fIndicator.value)
            filedTable = fIndicator.get("{http://www.eurofiling.info/xbrl/ext/filing-indicators}filed", "true") in ("true", "1")
            if filedTable:
                filingIndicator = True
            else:
                filingIndicator = False
            modelXbrl.filingIndicatorByFilingCode[filingIndicatorCode] = filingIndicator
    return True

def extendModelXbrl(modelXbrl):
    modelXbrl.filingIndicatorByFilingCode = {}
    modelXbrl.filingCodeByTableLabel = {}
    modelXbrl.treeRowByTableLabel = {}
    modelXbrl.indexTableTreeView = None
    modelXbrl.isEba = True
    return False     

__pluginInfo__ = {
    'name': 'EBA non-GUI model extensions',
    'version': '1.0',
    'description': "This plugin contains non-GUI extensions for EBA and EIOPA (e.g. filing indicators)",
    'license': 'Apache-2',
    'author': 'Acsone S. A.',
    'copyright': '(c) Copyright 2015 Acsone S. A.',
    # classes of mount points (required)
    'CntlrWinMain.Modeling.LoadFilingIndicators': loadFilingIndicators,
    'ModelXbrl.Init': extendModelXbrl
}