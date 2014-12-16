"""
:mod:`arelle.FactIndex`
~~~~~~~~~~~~~~~~~~~

.. py:module:: arelle.FactIndex
   :copyright: Copyright 2014 Acsone S. A., All rights reserved.
   :license: Apache-2.
   :synopsis: fast and compact way to find facts based on a property
"""
from arelle import PythonUtil  # @UnusedImport
from arelle import ModelValue, XbrlConst

from sqlalchemy import create_engine, Table, \
    Column, Integer, String, \
    Sequence, MetaData, ForeignKey, \
    Boolean, type_coerce, \
    func
from sqlalchemy.pool import StaticPool
from sqlalchemy.sql import select, and_
from sqlalchemy import types

TYPED_VALUE = '#TYPED_VALUE#'
DEFAULT = 'default'
NONDEFAULT = 'nondefault'
QNAME_FIELD_LENGTH = 128

class DBQName(types.TypeDecorator):

    impl = types.VARCHAR

    def __init__(self, length):
        self.singleFieldLength = length
        self.comparisonLimit = 2*length
        types.TypeDecorator.__init__(self, length*3)
    def process_bind_param(self, value, dialect):
        if isinstance(value, ModelValue.QName):
            return value.serialise()
        else:
            str(value)

    def process_result_value(self, value, dialect):
        return ModelValue.QName.deserialise(value)

    def copy(self):
        return DBQName(self.impl.length)

    def compare_values(self, x, y):
        return types.VARCHAR.compare_values(self, x[:(self.comparisonLimit)], y[:(self.comparisonLimit)])

    @property
    def python_type(self):
        return ModelValue.QName

    class comparator_factory(types.VARCHAR.comparator_factory):
        def __eq__(self, other):
            local_value = type_coerce(self.expr, types.VARCHAR)
            return func.substr(local_value, 1, QNAME_FIELD_LENGTH) == \
                    func.substr(other, 1, QNAME_FIELD_LENGTH)
        def __le__(self, other):
            local_value = type_coerce(self.expr, types.VARCHAR)
            return func.substr(local_value, 1, QNAME_FIELD_LENGTH) <= \
                    func.substr(other, 1, QNAME_FIELD_LENGTH)
        def __ge__(self, other):
            local_value = type_coerce(self.expr, types.VARCHAR)
            return func.substr(local_value, 1, QNAME_FIELD_LENGTH) >= \
                    func.substr(other, 1, QNAME_FIELD_LENGTH)
        def __lt__(self, other):
            local_value = type_coerce(self.expr, types.VARCHAR)
            return func.substr(local_value, 1, QNAME_FIELD_LENGTH) < \
                    func.substr(other, 1, QNAME_FIELD_LENGTH)
        def __gt__(self, other):
            local_value = type_coerce(self.expr, types.VARCHAR)
            return func.substr(local_value, 1, QNAME_FIELD_LENGTH) > \
                    func.substr(other, 1, QNAME_FIELD_LENGTH)
class FactIndex(object):
    def __init__(self):
        self.engine = create_engine('sqlite://',
                    connect_args={'check_same_thread':False},
                    poolclass=StaticPool)
        self.metadata = MetaData()
        self.facts = Table('facts', self.metadata,
                           Column('id', Integer, Sequence('facts_seq'), primary_key = True),
                           Column('isNil', Boolean, nullable = False, unique = False, index = True),
                           Column('qName', String(256), nullable = False, unique = False, index = True),
                           Column('datatype', String(256), nullable = False, unique = False, index = True),
                           Column('periodType', String(48), nullable = False, unique = False, index = True),
                           Column('objectId', Integer, nullable = False, unique = True, index = True),
                           Column('contextId', String(64), nullable = True, unique = False, index = True)
                           )
        self.dimensions = Table('dimensions', self.metadata,
                                Column('id', Integer, Sequence('dimensions_seq'), primary_key = True),
                                Column('qName', String(256), nullable = False, unique = False, index = True),
                                Column('isDefault', Boolean, nullable = False, unique = False, index = True),
                                Column('dimValue', String(256), nullable = True, unique = False, index = True),
                                Column('factId', Integer, ForeignKey('facts.id', ondelete="CASCADE"))
                                )
        self.arcs = Table('arcs', self.metadata,
                          Column('id', Integer, Sequence('arcs_seq'), primary_key = True),
                          Column('arcRole', String(256), nullable = True, unique = False, index = True),
                          Column('linkRole', String(256), nullable = False, unique = False, index = True),
                          Column('qNameLink', DBQName(QNAME_FIELD_LENGTH), nullable = True, unique = False, index = True),
                          Column('qNameArc', DBQName(QNAME_FIELD_LENGTH), nullable = True, unique = False, index = True),
                          Column('isFootnote', Boolean, nullable = False, unique = False, index = True),
                          Column('prototypeId', Integer, nullable = True, unique = False, index = True),
                          Column('objectId', Integer, nullable = True, unique = False, index = True))
        self.metadata.create_all(self.engine)
        self.connection = self.engine.connect()

    def close(self):
        self.connection.close()

    def insertFact(self, fact, modelXbrl):
        concept = fact.concept
        context = fact.context
        factIsNil = fact.isNil
        factQName = str(fact.qname)
        factDatatype = str(concept.typeQname)
        factPeriodType = str(concept.periodType)
        factObjectId = fact.objectIndex
        if fact.isItem:
            contextId = context.id
            factsInsert = self.facts.insert().values(isNil = factIsNil,
                                                     qName = factQName,
                                                     datatype = factDatatype,
                                                     periodType = factPeriodType,
                                                     objectId = factObjectId,
                                                     contextId = contextId)
        else:
            
            factsInsert = self.facts.insert().values(isNil = factIsNil,
                                                     qName = factQName,
                                                     datatype = factDatatype,
                                                     periodType = factPeriodType,
                                                     objectId = factObjectId)
        factsInsert.bind = self.engine
        result = self.connection.execute(factsInsert)
        newFactId = result.inserted_primary_key
        result.close()
        if fact.isItem and len(context.qnameDims)>0:
            allDimensions = context.qnameDims.keys()|modelXbrl.qnameDimensionDefaults.keys()
            for dim in allDimensions:
                dimValue = context.dimValue(dim)
                dimValueString = None
                if isinstance(dimValue, ModelValue.QName): # explicit dimension default value
                    dimValueString = str(dimValue)
                    dimValueIsDefault = True
                elif dimValue is not None: # not default
                    dimValueIsDefault = False
                    if dimValue.isExplicit:
                        dimValueString = str(dimValue.memberQname)
                else: # default typed dimension, no value
                    dimValueIsDefault = True
                if dimValueString is None:
                    dimensionsInsert = self.dimensions.insert().values(qName = str(dim),
                                                                       isDefault = dimValueIsDefault,
                                                                       factId = newFactId[0]
                                                                       )
                else:
                    dimensionsInsert = self.dimensions.insert().values(qName = str(dim),
                                                                       isDefault = dimValueIsDefault,
                                                                       dimValue = dimValueString,
                                                                       factId = newFactId[0]
                                                                       )
                dimensionsInsert.bind = self.engine
                result = self.connection.execute(dimensionsInsert)
                result.close()

    def deleteFact(self, fact):
        factObjectId = fact.objectIndex
        delStatement = self.facts.delete().where(self.facts.c.objectId == factObjectId)
        delStatement.bind = self.engine
        result = self.connection.execute(delStatement)
        numberOfDeletedRows = result.rowcount
        result.close()
        return numberOfDeletedRows

    def updateFact(self, fact):
        factObjectId = fact.objectIndex
        factIsNil = fact.isNil
        updateStatement = self.facts.update().where(self.facts.c.objectId == factObjectId).values(isNil = factIsNil)
        updateStatement.bind = self.engine
        result = self.connection.execute(updateStatement)
        numberOfUpdatedRows = result.rowcount
        result.close()
        return numberOfUpdatedRows

    def insertArc(self, key, modelObject, isFootnote, isPrototype):
        arcRole = key[0]
        linkRole = key[1]
        qNameLink = key[2]
        qNameArc = key[3]
        objectId = modelObject.objectIndex
        if isPrototype:
            arcInsert = self.arcs.insert().values(arcRole = arcRole,
                                                  linkRole = linkRole,
                                                  qNameLink = qNameLink,
                                                  qNameArc = qNameArc,
                                                  isFootnote = isFootnote,
                                                  prototypeId = objectId)
        else:
            arcInsert = self.arcs.insert().values(arcRole = arcRole,
                                                  linkRole = linkRole,
                                                  qNameLink = qNameLink,
                                                  qNameArc = qNameArc,
                                                  isFootnote = isFootnote,
                                                  objectId = objectId)
        arcInsert.bind = self.engine
        result = self.connection.execute(arcInsert)
        result.close()

    def deleteArc(self, link, isPrototype):
        objectId = link.objectIndex
        if isPrototype:
            delStatement = self.facts.delete().where(self.arcs.c.prototypeId == objectId)
        else:
            delStatement = self.arcs.delete().where( self.arcs.c.objectId == objectId)
        delStatement.bind = self.engine
        result = self.connection.execute(delStatement)
        numberOfDeletedRows = result.rowcount
        result.close()
        return numberOfDeletedRows

    def nonNilFacts(self, modelXbrl):
        selectStmt = select([self.facts.c.objectId]).where(self.facts.c.isNil == False)
        result = self.connection.execute(selectStmt)
        resultSet = set(modelXbrl.modelObjects[row[self.facts.c.objectId]] for row in result)
        result.close()
        return resultSet

    def nilFacts(self, modelXbrl):
        selectStmt = select([self.facts.c.objectId]).where(self.facts.c.isNil == True)
        result = self.connection.execute(selectStmt)
        resultSet = set(modelXbrl.modelObjects[row[self.facts.c.objectId]] for row in result)
        result.close()
        return resultSet

    def factsByQname(self, qName, modelXbrl, defaultValue=None, cntxtId=None):
        if  cntxtId is None:
            selectStmt = select([self.facts.c.objectId]).where(self.facts.c.qName == str(qName))
        else:
            selectStmt = select([self.facts.c.objectId]).where(and_(self.facts.c.qName == str(qName),
                                                                    self.facts.c.contextId == str(cntxtId)))
        result = self.connection.execute(selectStmt)
        resultSet = set(modelXbrl.modelObjects[row[self.facts.c.objectId]] for row in result)
        result.close()
        if (len(resultSet)>0):
            return resultSet
        else:
            return defaultValue

    def factsByQnameAll(self, modelXbrl):
        selectStmt = select([self.facts.c.qName, self.facts.c.objectId]).order_by(self.facts.c.qName)
        result = self.connection.execute(selectStmt)
        resultList = list()
        oldQName = ''
        currentFacts = list()
        for row in result:
            currentQName = row[self.facts.c.qName]
            if currentQName != oldQName:
                if len(currentFacts)>0:
                    resultList.append((oldQName, currentFacts))
                oldQName = currentQName
                currentFacts = {modelXbrl.modelObjects[row[self.facts.c.objectId]]}
            else:
                currentFacts.add(modelXbrl.modelObjects[row[self.facts.c.objectId]])
        if len(currentFacts)>0:
            resultList.append((oldQName, currentFacts))
        result.close()
        return resultList

    def factsByDatatype(self, typeQname, modelXbrl):
        selectStmt = select([self.facts.c.objectId]).where(self.facts.c.datatype == str(typeQname))
        result = self.connection.execute(selectStmt)
        resultSet = set(modelXbrl.modelObjects[row[self.facts.c.objectId]] for row in result)
        result.close()
        return resultSet

    def factsByPeriodType(self, periodType, modelXbrl):
        selectStmt = select([self.facts.c.objectId]).where(self.facts.c.periodType == str(periodType))
        result = self.connection.execute(selectStmt)
        resultSet = set(modelXbrl.modelObjects[row[self.facts.c.objectId]] for row in result)
        result.close()
        return resultSet

    def factsByDimMemQname(self, dimQname, modelXbrl, memQname=None):
        if memQname is None:
            selectStmt = select([self.facts.c.objectId]).select_from(self.facts.join(self.dimensions)).\
                where(self.dimensions.c.qName == str(dimQname))
        elif memQname == DEFAULT:
            selectStmt = select([self.facts.c.objectId]).select_from(self.facts.join(self.dimensions)).\
                where(and_(self.dimensions.c.qName == str(dimQname), self.dimensions.c.isDefault == True))
        elif memQname == NONDEFAULT:
            selectStmt = select([self.facts.c.objectId]).select_from(self.facts.join(self.dimensions)).\
                where(and_(self.dimensions.c.qName == str(dimQname), self.dimensions.c.isDefault == False))
        else:
            selectStmt = select([self.facts.c.objectId]).select_from(self.facts.join(self.dimensions)).\
                where(and_(self.dimensions.c.qName == str(dimQname), self.dimensions.c.dimValue == str(memQname)))
        result = self.connection.execute(selectStmt)
        resultSet = set(modelXbrl.modelObjects[row[self.facts.c.objectId]] for row in result)
        result.close()
        return resultSet

    def findArcroleSearchSet(self, oldArcrole):
        if oldArcrole == 'XBRL-footnotes':
            return None
        if oldArcrole == 'XBRL-dimensions':
            return XbrlConst.dimensionArcRolePrefix;
        if oldArcrole == 'XBRL-formulae':
            return XbrlConst.formulaArcroles
        if oldArcrole == 'Table-rendering':
            return XbrlConst.tableRenderingArcroles
        return oldArcrole

    def addUniformWhereClause(self, fieldName, fieldValue, selectStmt):
        if fieldValue is not None:
            if isinstance(fieldValue, set):
                if len(fieldValue) > 0:
                    selectStmt = selectStmt.where(self.arcs.c[fieldName].in_(fieldValue))
                else:
                    selectStmt = selectStmt.where(self.arcs.c[fieldName] != None)
            else:
                selectStmt = selectStmt.where(self.arcs.c[fieldName] == fieldValue)
        return selectStmt


    def retrieveObject(self, modelXbrl, objectId, prototypeId):
        if objectId is not None:
            return modelXbrl.modelObjects[objectId]
        else: # prototypeId is not None
            return modelXbrl.linkPrototypes[prototypeId]

    def toQName(self, myTuple, returnArcRole, returnLinkRole, returnQNameLink, returnQNameArc):
        if (returnQNameLink or returnQNameArc):
            posQNameArc = len(myTuple)-1 if returnQNameArc else len(myTuple)
            posQNamelink = posQNameArc-1 if returnQNameLink else len(myTuple)
            newList = []
            for i in range(0, len(myTuple)):
                if (i==posQNameArc or i==posQNamelink):
                    newList.append(ModelValue.QName.deserialise(myTuple[i]))
                else:
                    newList.append(myTuple[i])
            return tuple(newList)
        else:
            return myTuple

    def retrieveArcsByKey(self, arcRole, linkRole, qNameLink, qNameArc, isFootnote, modelXbrl,
                          returnArcRole=False, returnLinkRole=False, returnQNameLink=False, returnQNameArc=False,
                          returnObjects=True):
        if returnObjects:
            fieldsToReturn = [self.arcs.c.objectId, self.arcs.c.prototypeId]
        else:
            fieldsToReturn = []
        if returnArcRole:
            fieldsToReturn.append(self.arcs.c.arcRole)
        if returnLinkRole:
            fieldsToReturn.append(self.arcs.c.linkRole)
        if returnQNameLink:
            fieldsToReturn.append(self.arcs.c.qNameLink)
        if returnQNameArc:
            fieldsToReturn.append(self.arcs.c.qNameArc)
        selectStmt = select(fieldsToReturn)
        if arcRole is not None:
            if isinstance(arcRole, (set, tuple)):
                if len(arcRole)>0:
                    selectStmt = selectStmt.where(self.arcs.c.arcRole.in_(arcRole))
                else:
                    selectStmt = selectStmt.where(self.arcs.c.arcRole!=None)
            elif arcRole.endswith('/'): # mostly for XbrlConst.dimensionArcRolePrefix
                selectStmt = selectStmt.where(self.arcs.c.arcRole.like(arcRole+'%'))
            else:
                selectStmt = selectStmt.where(self.arcs.c.arcRole==arcRole)
        qNameLink = qNameLink.serialise() if isinstance(qNameLink, ModelValue.QName) else qNameLink
        qNameArc = qNameArc.serialise() if isinstance(qNameArc, ModelValue.QName) else qNameArc
        selectStmt = self.addUniformWhereClause('linkRole', linkRole, selectStmt)
        selectStmt = self.addUniformWhereClause('qNameLink', qNameLink, selectStmt)
        selectStmt = self.addUniformWhereClause('qNameArc', qNameArc, selectStmt)
        if isFootnote is not None:
            selectStmt = selectStmt.where(self.arcs.c.isFootnote==isFootnote)
        result = self.connection.execute(selectStmt)
        
        if returnArcRole or returnLinkRole or returnQNameLink or returnQNameArc:
            if returnObjects:
                resultSet = set(row[2:]
                                +(self.retrieveObject(modelXbrl,
                                                      row[self.arcs.c.objectId],
                                                      row[self.arcs.c.prototypeId]),) for row in result)
            else:
                resultSet = set(row[:]
                                for row in result)
        else:
            if returnObjects:
                resultSet = set(self.retrieveObject(modelXbrl,
                                                    row[self.arcs.c.objectId],
                                                    row[self.arcs.c.prototypeId]) for row in result)
            else:
                resultSet = {}
        result.close()
        return resultSet

    def arcsByKey(self, key, modelXbrl, returnArcRole=False, returnLinkRole=False, returnQNameLink=False,
                   returnQNameArc=False, returnObjects=True):
        arcrole = key[0]
        originalArcrole = arcrole
        if arcrole and isinstance(arcrole, str) and (arcrole == 'Table-rendering' or arcrole[:5]=='XBRL-'):
            arcrole = self.findArcroleSearchSet(arcrole)
        isFootnote = True if originalArcrole=='XBRL-footnotes' else None
        return self.retrieveArcsByKey(arcrole, key[1], key[2], key[3], isFootnote, modelXbrl,
                                      returnArcRole=returnArcRole, returnLinkRole=returnLinkRole,
                                      returnQNameLink=returnQNameLink, returnQNameArc=returnQNameArc,
                                      returnObjects=returnObjects)

def testAll():
    class ModelConcept(object):
        def __init__(self, typeQname, periodType):
            self.typeQname = typeQname
            self.periodType = periodType
    
    class ModelContext(object):
        def __init__(self, cntxtId):
            self.qnameDims = set()
            self.id = cntxtId
        def dimValue(self, dimQname):
            """Caution: copied from ModelInstanceObject!"""
            try:
                return self.qnameDims[dimQname]
            except KeyError:
                try:
                    return self.modelXbrl.qnameDimensionDefaults[dimQname]
                except KeyError:
                    return None

    class Fact(object):
        def __init__(self, concept, context, isNil, qname, objectId, isItem):
            self.concept = concept
            self.context = context
            self.isNil = isNil
            self.qname = qname
            self.objectIndex = objectId
            self.isItem = isItem

    class ModelXbrl(object):
        def __init__(self):
            self.modelObjects = dict()
            self.qnameDimensionDefaults = dict()
            self.linkPrototypes = dict()

    class DimensionValue(object):
        def __init__(self, isExplicit, value):
            self.isExplicit = isExplicit
            self.memberQname = value 
        def __str__(self):
            return self.memberQname

    class ModelObject(object):
        def __init__(self, objectId):
            self.objectIndex = objectId

    def assertEquals(expectedValue, actualValue):
        try:
            assert expectedValue == actualValue
        except AssertionError:
            print('Expected %s got %s' % (expectedValue, actualValue))
            raise
    modelXbrl = ModelXbrl()
    concept1d = ModelConcept('type1', 'duration')
    concept1i = ModelConcept('type1', 'instant')
    concept2d = ModelConcept('type2', 'duration')
    concept2i = ModelConcept('type2', 'instant')
    dimVal1 = DimensionValue(True, 'val1')
    dimVal2 = DimensionValue(True, 'val2')
    dimVal3 = DimensionValue(True, 'val3')
    dimVal4 = DimensionValue(True, 'val4')
    dimVal5 = DimensionValue(True, 'val5')
    dimVal6 = DimensionValue(True, 'val6')
    context1 = ModelContext('c-1')
    context1.qnameDims = {'dim1': dimVal1, 'dim2': dimVal2, 'dim3': dimVal3}
    context2 = ModelContext('c-2')
    context2.qnameDims = {'dim1': dimVal1, 'dim7': None}
    context3 = ModelContext('c-3')
    context3.qnameDims = {'dim4': dimVal4, 'dim5': dimVal5, 'dim6': dimVal6, 'dim7': None}

    fact1 = Fact(concept1d, context1, False, '{ns}name1', 1, True)
    fact2 = Fact(concept1i, context2, False, '{ns}name1', 2, True)
    fact3 = Fact(concept2d, context3, False, '{ns}name2', 3, True)
    fact4 = Fact(concept2i, context3, False, '{ns}name2', 4, True)
    fact5 = Fact(concept2i, context3, True, '{ns}name3', 5, True)
    fact6 = Fact(concept2d, context3, True, '{ns}name4', 6, False)
    modelXbrl.modelObjects[fact1.objectIndex] = fact1
    modelXbrl.modelObjects[fact2.objectIndex] = fact2
    modelXbrl.modelObjects[fact3.objectIndex] = fact3
    modelXbrl.modelObjects[fact4.objectIndex] = fact4
    modelXbrl.modelObjects[fact5.objectIndex] = fact5
    modelXbrl.modelObjects[fact6.objectIndex] = fact6

    factIndex = FactIndex()
    factIndex.insertFact(fact1, modelXbrl)
    factIndex.insertFact(fact2, modelXbrl)
    factIndex.insertFact(fact3, modelXbrl)
    factIndex.insertFact(fact4, modelXbrl)
    factIndex.insertFact(fact5, modelXbrl)
    factIndex.insertFact(fact6, modelXbrl)
    dataResult = factIndex.nonNilFacts(modelXbrl)
    assertEquals({fact1, fact2, fact3, fact4}, dataResult)
    dataResult = factIndex.nilFacts(modelXbrl)
    assertEquals({fact5, fact6}, dataResult)
    expectedResult = 'NiceJob'
    dataResult = factIndex.factsByQname('doesNotExist', modelXbrl, expectedResult)
    assertEquals(expectedResult, dataResult)
    dataResult = factIndex.factsByQname('{ns}name1', modelXbrl, None)
    assertEquals({fact1, fact2}, dataResult)
    dataResult = factIndex.factsByQname('{ns}name1', modelXbrl, None, cntxtId='c-1')
    assertEquals({fact1}, dataResult)
    dataResult = factIndex.factsByQname('{ns}name3', modelXbrl, None)
    assertEquals({fact5}, dataResult)
    dataResult = factIndex.factsByDatatype('doesNotExist', modelXbrl)
    assertEquals(set(), dataResult)
    dataResult = factIndex.factsByDatatype('type2', modelXbrl)
    assertEquals({fact3, fact4, fact5, fact6}, dataResult)
    dataResult = factIndex.factsByPeriodType('doesNotExist', modelXbrl)
    assertEquals(set(), dataResult)
    dataResult = factIndex.factsByPeriodType('instant', modelXbrl)
    assertEquals({fact2, fact4, fact5}, dataResult)
    dataResult = factIndex.factsByDimMemQname('doesNotExist', modelXbrl, None)
    assertEquals(set(), dataResult)
    dataResult = factIndex.factsByDimMemQname('dim1', modelXbrl, None)
    assertEquals({fact1, fact2}, dataResult)
    dataResult = factIndex.factsByDimMemQname('dim2', modelXbrl, 'val2')
    assertEquals({fact1}, dataResult)
    dataResult = factIndex.factsByDimMemQname('dim1', modelXbrl, 'val1')
    assertEquals({fact1, fact2}, dataResult)
    dataResult = factIndex.factsByDimMemQname('dim1', modelXbrl, NONDEFAULT)
    assertEquals({fact1, fact2}, dataResult)
    dataResult = factIndex.factsByDimMemQname('dim7', modelXbrl, DEFAULT)
    assertEquals({fact2, fact3, fact4, fact5}, dataResult) # fact6 is not an item!
    dataResult = factIndex.factsByQnameAll(modelXbrl)
    assertEquals([('{ns}name1', {fact1, fact2}), ('{ns}name2', {fact3, fact4}), ('{ns}name3', {fact5}), ('{ns}name4', {fact6})], dataResult);
    fact1.isNil = True
    numberOfUpdatedFacts = factIndex.updateFact(fact1)
    assertEquals(1, numberOfUpdatedFacts)
    dataResult = factIndex.nonNilFacts(modelXbrl)
    assertEquals({fact2, fact3, fact4}, dataResult)
    dataResult = factIndex.nilFacts(modelXbrl)
    assertEquals({fact1, fact5, fact6}, dataResult)
    numberOfDeletedFacts = factIndex.deleteFact(fact1)
    assertEquals(1, numberOfDeletedFacts)
    dataResult = factIndex.nonNilFacts(modelXbrl)
    assertEquals({fact2, fact3, fact4}, dataResult)
    dataResult = factIndex.factsByDimMemQname('dim1', modelXbrl, None)
    assertEquals({fact2}, dataResult)
    dataResult = factIndex.factsByDimMemQname('dim2', modelXbrl, None)
    assertEquals(set(), dataResult)

    qName1 = ModelValue.QName('pfx', 'ns', 'qname1')
    qName1b = ModelValue.QName('pfx2', 'ns', 'qname1')
    qName2 = ModelValue.QName('pfx', 'ns', 'qname2')
    tupleKey1 = ('{ns1}node/arc1', '{ns2}link1', qName1, qName2)
    tupleKey2 = (None, '{ns2}link1', qName1, None)
    tupleKey3 = ('{ns1}arc2', '{ns2}link1', qName1, None)
    tupleKey4 = (XbrlConst.tableBreakdown, '{ns2}link2', None, None)
    tupleKey5 = ('http://xbrl.org/int/dim/arcrole/toto', '{ns2}link2', None, None)
    tupleKey6 = ('http://xbrl.org/arcrole/2008/assertion-set', '{ns2}link2', None, None)
    modelObject1 = ModelObject(7)
    modelObject2 = ModelObject(8)
    modelObject3 = ModelObject(9)
    modelObject4 = ModelObject(10)
    modelObject5 = ModelObject(11)
    modelObject6 = ModelObject(12)
    modelObject7 = ModelObject(13)
    modelObject8 = ModelObject(14)
    modelObject9 = ModelObject(15)
    modelXbrl.modelObjects[modelObject1.objectIndex] = modelObject1
    modelXbrl.modelObjects[modelObject2.objectIndex] = modelObject2
    modelXbrl.modelObjects[modelObject3.objectIndex] = modelObject3
    modelXbrl.modelObjects[modelObject7.objectIndex] = modelObject7
    modelXbrl.modelObjects[modelObject8.objectIndex] = modelObject8
    modelXbrl.modelObjects[modelObject9.objectIndex] = modelObject9
    modelXbrl.linkPrototypes[modelObject1.objectIndex] = modelObject1
    modelXbrl.linkPrototypes[modelObject2.objectIndex] = modelObject2
    modelXbrl.linkPrototypes[modelObject3.objectIndex] = modelObject3
    modelXbrl.linkPrototypes[modelObject4.objectIndex] = modelObject4
    modelXbrl.linkPrototypes[modelObject5.objectIndex] = modelObject5
    modelXbrl.linkPrototypes[modelObject6.objectIndex] = modelObject6
    factIndex.insertArc(tupleKey1, modelObject1, False, False)
    factIndex.insertArc(tupleKey2, modelObject2, False, False)
    factIndex.insertArc(tupleKey1, modelObject3, False, False)
    factIndex.insertArc(tupleKey4, modelObject7, False, False)
    factIndex.insertArc(tupleKey5, modelObject8, False, False)
    factIndex.insertArc(tupleKey6, modelObject9, False, False)
    factIndex.insertArc(tupleKey3, modelObject1, False, True)
    factIndex.insertArc(tupleKey3, modelObject2, False, True)
    factIndex.insertArc(tupleKey3, modelObject3, False, True)
    factIndex.insertArc(tupleKey3, modelObject4, True, True)
    factIndex.insertArc(tupleKey3, modelObject5, True, True)
    factIndex.insertArc(tupleKey3, modelObject6, True, True)
    try:
        factIndex.arcInsert(tupleKey2, modelObject1, False, False)
    except:
        pass
    else:
        print('modelobject2 was inserted twice. This should not happen!')
    dataResult = factIndex.arcsByKey(('{ns1}node/arc1', None, None, None), modelXbrl)
    assertEquals({modelObject1, modelObject3}, dataResult)
    dataResult = factIndex.arcsByKey((('{ns1}node/arc1', 'http://xbrl.org/int/dim/arcrole/toto'), None, None, None), modelXbrl)
    assertEquals({modelObject1, modelObject3, modelObject8}, dataResult)
    dataResult = factIndex.arcsByKey(({'{ns1}node/arc1', 'http://xbrl.org/int/dim/arcrole/toto'}, None, None, None), modelXbrl)
    assertEquals({modelObject1, modelObject3, modelObject8}, dataResult)
    dataResult = factIndex.arcsByKey((None, '{ns2}link1', None, None), modelXbrl)
    assertEquals({modelObject1, modelObject2, modelObject3, modelObject4, modelObject5, modelObject6}, dataResult)
    dataResult = factIndex.arcsByKey((None, None, qName1b, None), modelXbrl)
    assertEquals({modelObject1, modelObject2, modelObject3, modelObject4, modelObject5, modelObject6}, dataResult)
    dataResult = factIndex.arcsByKey((None, None, qName1b, None), modelXbrl, returnQNameLink=True)
    assertEquals({(qName1, modelObject1), (qName1, modelObject2), (qName1, modelObject3), 
                  (qName1, modelObject4), (qName1, modelObject5), (qName1, modelObject6)}, dataResult)
    dataResult = factIndex.arcsByKey((None, None, None, qName2), modelXbrl)
    assertEquals({modelObject1, modelObject3}, dataResult)
    dataResult = factIndex.arcsByKey((None, None, None, qName2), modelXbrl, returnQNameArc=True)
    assertEquals({(qName2, modelObject1), (qName2, modelObject3)}, dataResult)
    dataResult = factIndex.arcsByKey(('XBRL-footnotes', None, None, None), modelXbrl)
    assertEquals({modelObject4, modelObject5, modelObject6}, dataResult)
    dataResult = factIndex.arcsByKey(('{ns1}node/', None, None, None), modelXbrl)
    assertEquals({modelObject1, modelObject3}, dataResult)
    dataResult = factIndex.arcsByKey(('Table-rendering', None, None, None), modelXbrl)
    assertEquals({modelObject7}, dataResult)
    dataResult = factIndex.arcsByKey(('XBRL-dimensions', None, None, None), modelXbrl)
    assertEquals({modelObject8}, dataResult)
    dataResult = factIndex.arcsByKey(('XBRL-formulae', None, None, None), modelXbrl)
    assertEquals({modelObject9}, dataResult)
    dataResult = factIndex.arcsByKey((None, 'inexisting_link', None, None), modelXbrl,
                                      returnLinkRole=True, returnObjects=False)
    assertEquals(0, len(dataResult))
    dataResult = factIndex.arcsByKey((set(), set(), set(), set()), modelXbrl, returnArcRole=True, returnLinkRole=True, returnQNameLink=True,
                            returnQNameArc=True, returnObjects=False)
    dataResult.update(set(('XBRL-footnotes', arc[0], None, None)
                      for arc in factIndex.arcsByKey(('XBRL-footnotes', set(), None, None), modelXbrl, returnArcRole=False,
                                                     returnLinkRole=True, returnQNameLink=False, returnQNameArc=False,
                                                     returnObjects=False)),
                      set(('XBRL-dimensions', arc[0], None, None)
                      for arc in factIndex.arcsByKey(('XBRL-dimensions', set(), None, None), modelXbrl, returnArcRole=False,
                                                     returnLinkRole=True, returnQNameLink=False, returnQNameArc=False,
                                                     returnObjects=False)),
                      set(('XBRL-formulae', arc[0], None, None)
                      for arc in factIndex.arcsByKey(('XBRL-formulae', set(), None, None), modelXbrl, returnArcRole=False,
                                                     returnLinkRole=True, returnQNameLink=False, returnQNameArc=False,
                                                     returnObjects=False)))
    assertEquals({tupleKey1,
                  ('XBRL-dimensions', '{ns2}link2', None, None),
                  ('XBRL-formulae', '{ns2}link2', None, None),
                  ('XBRL-footnotes', '{ns2}link1', None, None)}, dataResult)
    dataResult = factIndex.deleteArc(modelObject3, False)
    assertEquals(1, dataResult)
    dataResult = factIndex.arcsByKey(('{ns1}node/arc1', None, None, None), modelXbrl)
    assertEquals({modelObject1}, dataResult)
    factIndex.close()
if __name__ == '__main__':
    testAll()