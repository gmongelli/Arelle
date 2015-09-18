'''
Compute the decimals attribute from the actually supplied value.

(c) Copyright 2015 Acsone S. A., All rights reserved.
'''
from arelle import XbrlConst
from arelle.ModelValue import qname

qnPercentItemType = qname("{http://www.xbrl.org/dtr/type/numeric}num:percentItemType")

def decimalsComputer(locale, value, concept, defaultDecimals):
    '''
    :type locale: dict
    :type value: string
    :type concept: ModelConcept
    :type defaultDecimals: str
    :rtype (boolean, str)
    '''
    if defaultDecimals is None or len(defaultDecimals)==0:
        defaultDecimals = 'INF'
    if len(defaultDecimals)==0:
        defaultDecimals = 'INF'
    if concept.isNumeric and defaultDecimals != 'INF' and len(value)>0:
        decimalPoint = locale["decimal_point"]
        explodedNumber = value.split(decimalPoint)
        integerPart = ""
        if len(explodedNumber)==2:
            # If there is a decimal point and if there are decimals after that point,
            # count the decimals!
            integerPart, fractionalPart = explodedNumber
            return (True, str(len(fractionalPart)))
        else:
            integerPart = value
        #Count the trailing zeros in the part before the decimal point
        if integerPart == '0':
            return (True, '0')
        else:
            index = 0
            for index, char in enumerate(reversed(integerPart)):
                if char != '0':
                    break;
            return (True, ('0' if index==0 or (index+1==len(integerPart) and integerPart[0]=='0') else "-"+str(index)))
    else:
        return (False, defaultDecimals)

def ebaDecimals(locale, value, concept, defaultDecimals):
    '''
    :type locale: dict
    :type value: string
    :type concept: ModelConcept
    :type defaultDecimals: str
    :rtype (boolean, str)
    '''
    isPercent = concept.typeQname == qnPercentItemType
    isInteger = XbrlConst.isIntegerXsdType(concept.type.baseXsdType)
    isMonetary = concept.isMonetary
    decimalsFound, decimals = decimalsComputer(locale, value, concept, defaultDecimals)
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
    'name': 'Decimal Attribute computer (EBA compliant)',
    'version': '1.1',
    'description': "This module supplies a custom method for computing the decimals attribute according to the actually supplied value. Do not use it in conjunction with ebaDecimalsImprovement.",
    'license': 'Apache-2',
    'author': 'Acsone S. A.',
    'copyright': '(c) Copyright 2015 Acsone S. A.',
    # classes of mount points (required)
    'CntlrWinMain.Rendering.ComputeDecimals': ebaDecimals
}