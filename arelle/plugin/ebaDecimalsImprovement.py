'''
Correct the decimals if they do not match the compliance criteri of the EBA.

(c) Copyright 2015 Acsone S. A., All rights reserved.
'''
from arelle import XbrlConst
from arelle.ModelValue import qname

qnPercentItemType = qname("{http://www.xbrl.org/dtr/type/numeric}num:percentItemType")

def ebaDecimals(locale, value, concept, defaultDecimals):
    '''
    :type locale: dict
    :type value: string
    :type concept: ModelConcept
    :type defaultDecimals: str
    :rtype (boolean, str)
    '''
    if defaultDecimals is None or len(defaultDecimals)==0:
        defaultDecimals = 'INF'
    isPercent = concept.typeQname == qnPercentItemType
    isInteger = XbrlConst.isIntegerXsdType(concept.type.baseXsdType)
    isMonetary = concept.isMonetary
    decimalsFound = True
    decimals = defaultDecimals
    if not(decimalsFound) or decimals == 'INF':
        return (decimalsFound, decimals)
    else:
        # the default values are for non-monetary items
        lowerBound = -20
        upperBound = 20
        decimalsAsInteger = int(decimals)
        if isMonetary:
            lowerBound = -3
        elif isInteger:
            lowerBound = upperBound = 0
        elif isPercent: # percent values
            lowerBound = 4
            upperBound = 20
        if decimalsAsInteger<lowerBound:
            decimals = str(lowerBound)
            decimalsAsInteger = lowerBound
        if decimalsAsInteger>upperBound:
            decimals = 'INF' # approximation
            decimalsAsInteger = upperBound
        return (decimalsFound, decimals)

__pluginInfo__ = {
    'name': 'EBA decimals improvement',
    'version': '1.1',
    'description': "This module changes the decimal attribute if does not conform with the EBA recommendations. Do not use it in conjunction with ebaDecimalsFromAmounts",
    'license': 'Apache-2',
    'author': 'Gregorio Mongelli (Acsone S. A.)',
    'copyright': '(c) Copyright 2015 Acsone S. A.',
    # classes of mount points (required)
    'CntlrWinMain.Rendering.ComputeDecimals': ebaDecimals
}