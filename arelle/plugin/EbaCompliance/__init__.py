'''
Improve the EBA compliance of the currently loaded facts.

For the time being, there are only three improvements that are implemented:
1. The filing indicators are regenerated using a fixed context with ID "c".
2. The nil facts and the unused contexts and units are removed
3. The entity scheme, the entity ID, the period start and the period end date are updated for every fact.

Moreover, a new File > New EBA File... menu entry is provided to ease the creation of the
latest EBA instances.

(c) Copyright 2014, 2015 Acsone S. A., All rights reserved.
'''

from arelle import ModelDocument, XmlValidate, ModelXbrl, XbrlConst
from arelle.ModelValue import qname
from arelle.DialogNewFactItem import getNewFactItemOptions
from lxml import etree
from arelle.ViewWinRenderedGrid import ViewRenderedGrid
from .ViewWalkerRenderedGrid import viewWalkerRenderedGrid
from .FactWalkingAction import FactWalkingAction
from arelle.ModelInstanceObject import NewFactItemOptions
from arelle.EbaUtil import getFactItemOptions,isEbaInstance
from arelle.UiUtil import gridCombobox, label
from arelle.CntlrWinTooltip import ToolTip

from tkinter import Toplevel, N, S, E, W, messagebox
try:
    from tkinter.ttk import Button, Frame
except ImportError:
    from ttk import Button, Frame
try:
    import regex as re
except ImportError:
    import re

qnFindFilingIndicators = qname("{http://www.eurofiling.info/xbrl/ext/filing-indicators}find:fIndicators")
qnFindFilingIndicator = qname("{http://www.eurofiling.info/xbrl/ext/filing-indicators}find:filingIndicator")

EBA_REPORTING_INDIVIDUAL = 'Individual'
EBA_REPORTING_CONSOLIDATED = 'Consolidated'
EBA_REPORTING_TYPES_VALUES = (EBA_REPORTING_INDIVIDUAL, EBA_REPORTING_CONSOLIDATED)
EBA_ENTRY_POINTS_INDIVIDUAL = {'Asset Encumbrance' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/ae/its-2013-04/2014-07-31/mod/ae_ind.xsd',
                               'Common Reporting - Own Funds and Leverage' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2013-02/2014-07-31/mod/corep_ind.xsd',
                               'Liquidity Coverage - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2013-02/2014-07-31/mod/corep_lcr_ind.xsd',
                               'Large Exposures - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2013-02/2014-07-31/mod/corep_le_ind.xsd',
                               'Stable Funding - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2013-02/2014-07-31/mod/corep_nsfr_ind.xsd'}

EBA_ENTRY_POINTS_CONSOLIDATED = {'Asset Encumbrance' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/ae/its-2013-04/2014-07-31/mod/ae_con.xsd',
                                 'Financial Reporting, National GAAP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/finrep/its-2013-03/2014-07-31/mod/finrep_con_gaap.xsd',
                                 'Financial Reporting, IFRS' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/finrep/its-2013-03/2014-07-31/mod/finrep_con_ifrs.xsd',
                                 'Common Reporting - Own Funds and Leverage' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2013-02/2014-07-31/mod/corep_con.xsd',
                                 'Liquidity Coverage - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2013-02/2014-07-31/mod/corep_lcr_con.xsd',
                                 'Large Exposures - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2013-02/2014-07-31/mod/corep_le_con.xsd',
                                 'Stable Funding - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2013-02/2014-07-31/mod/corep_nsfr_con.xsd'}

class EbaNewFileOptions(object):
    def __init__(self, ebaReportingType, ebaEntryPoint):
        self.ebaReportingType = ebaReportingType
        self.ebaEntryPoint = ebaEntryPoint

class DialogNewFileOptions(Toplevel):
    def __init__(self, mainWin):
        self.mainWin = mainWin
        parent = mainWin
        super(DialogNewFileOptions, self).__init__(parent)
        self.parent = parent
        parentGeometry = re.match("(\d+)x(\d+)[+]?([-]?\d+)[+]?([-]?\d+)", parent.geometry())
        dialogX = int(parentGeometry.group(3))
        dialogY = int(parentGeometry.group(4))
        self.accepted = False
        self.ebaEntryPointValues = sorted(EBA_ENTRY_POINTS_INDIVIDUAL.keys())
        self.options = EbaNewFileOptions(EBA_REPORTING_TYPES_VALUES[0],
                                         self.ebaEntryPointValues[0])
        options = self.options

        self.transient(self.parent)
        self.title(_("New EBA File"))
        
        frame = Frame(self)

        label(frame, 1, 1, _("EBA reporting type:"))
        self.cellReportType = gridCombobox(frame, 2, 1, getattr(options,"ebaReportingType", ""),
                                           values=EBA_REPORTING_TYPES_VALUES,
                                           comboboxselected=self.onReportTypeChanged,
                                           width=40)
        ToolTip(self.cellReportType, text=_("Select a report type"), wraplength=240)
        label(frame, 1, 2, _("Entry point:"))
        self.cellEntryPoint = gridCombobox(frame, 2, 2, getattr(options,"ebaEntryPoint", ""),
                                           values=self.ebaEntryPointValues,
                                           width=40)
        ToolTip(self.cellEntryPoint, text=_("Select an EBA entry point"), wraplength=240)
        currentRow = 3

        cancelButton = Button(frame, text=_("Cancel"), width=8, command=self.close)
        ToolTip(cancelButton, text=_("Cancel operation"))
        okButton = Button(frame, text=_("New"), width=8, command=self.ok)
        ToolTip(okButton, text=_("Create a new file"))
        cancelButton.grid(row=currentRow, column=1, columnspan=3, sticky=E, pady=3, padx=3)
        okButton.grid(row=currentRow, column=1, columnspan=3, sticky=E, pady=3, padx=86)
        
        frame.grid(row=0, column=0, sticky=(N,S,E,W))
        frame.columnconfigure(2, weight=1)
        window = self.winfo_toplevel()
        window.columnconfigure(0, weight=1)
        self.geometry("+{0}+{1}".format(dialogX+50,dialogY+100))
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.grab_set()
        self.wait_window(self)
        
    def checkEntries(self):
        errors = []
        if self.cellReportType.value is None or self.cellReportType.value not in EBA_REPORTING_TYPES_VALUES:
            errors.append(_("Please select a report type."))
        if self.cellEntryPoint.value is None or self.cellEntryPoint.value not in self.ebaEntryPointValues:
            errors.append(_("Please select an EBA entry point."))

        if errors:
            messagebox.showwarning(_("Dialog validation error(s)"),
                                "\n".join(errors), parent=self)
            return False
        return True

    def setOptions(self):
        options = self.options
        options.ebaReportingType = self.cellReportType.value
        options.ebaEntryPoint = self.cellEntryPoint.value

    def ok(self, event=None):
        if not self.checkEntries():
            return
        self.setOptions()
        self.accepted = True
        self.close()

    def close(self, event=None):
        self.parent.focus_set()
        self.destroy()

    def onReportTypeChanged(self, event):
        combobox = event.widget
        value = combobox.value
        if value == EBA_REPORTING_INDIVIDUAL:
            self.ebaEntryPointValues = sorted(EBA_ENTRY_POINTS_INDIVIDUAL.keys())
        else:
            self.ebaEntryPointValues = sorted(EBA_ENTRY_POINTS_CONSOLIDATED.keys())
        self.cellEntryPoint['values']=self.ebaEntryPointValues
        if self.cellEntryPoint.value not in self.ebaEntryPointValues:
            self.cellEntryPoint.current(0)

    @property
    def newUrl(self):
        options = self.options
        if options.ebaReportingType == EBA_REPORTING_INDIVIDUAL:
            urls = EBA_ENTRY_POINTS_INDIVIDUAL
        else:
            urls = EBA_REPORTING_CONSOLIDATED
        return urls[options.ebaEntryPoint]

def improveEbaCompliance(dts, cntlr, lang="en"):
    ':type dts: ModelXbrl'
    try:
        if not isEbaInstance(dts):
            dts.modelManager.showStatus(_("Only applicable to EBA instances"), 5000)
            return
        dts.modelManager.showStatus(_("Improving the EBA compliance"))
        deleteNilFacts(dts, cntlr)
        factWalkingAction = FactWalkingAction(dts)
        newFactItemOptions = getFactItemOptions(dts, cntlr)
        if not newFactItemOptions:
            return
        from arelle.ModelRenderingObject import ModelEuTable, ModelTable
        
        class nonTkBooleanVar():
            def __init__(self, value=True):
                self.value = value
            def set(self, value):
                self.value = value
            def get(self):
                return self.value
        class View():
            def __init__(self, tableOrELR, ignoreDimValidity, xAxisChildrenFirst, yAxisChildrenFirst):
                self.tblELR = tableOrELR
                # context menu boolean vars (non-tkinter boolean)
                self.ignoreDimValidity = nonTkBooleanVar(value=ignoreDimValidity)
                self.xAxisChildrenFirst = nonTkBooleanVar(value=xAxisChildrenFirst)
                self.yAxisChildrenFirst = nonTkBooleanVar(value=yAxisChildrenFirst)

        groupTableRels = dts.modelXbrl.relationshipSet(XbrlConst.euGroupTable)
        modelTables = []

        def viewTable(modelTable, factWalkingAction):
            if isinstance(modelTable, (ModelEuTable, ModelTable)):
                # status
                dts.modelManager.cntlr.addToLog("improving: " + modelTable.id)

                viewWalkerRenderedGrid(dts,
                                       factWalkingAction,
                                       lang=lang,
                                       viewTblELR=modelTable,
                                       sourceView=View(modelTable, False, False, True))

            for rel in groupTableRels.fromModelObject(modelTable):
                viewTable(rel.toModelObject, factWalkingAction)

    
        for rootConcept in groupTableRels.rootConcepts:
            sourceline = 0
            for rel in dts.modelXbrl.relationshipSet(XbrlConst.euGroupTable).fromModelObject(rootConcept):
                sourceline = rel.sourceline
                break
            modelTables.append((rootConcept, sourceline))
            
        for modelTable, order in sorted(modelTables, key=lambda x: x[1]):  # @UnusedVariable
            viewTable(modelTable, factWalkingAction)

        createOrReplaceFilingIndicators(dts, factWalkingAction.allFilingIndicatorCodes, newFactItemOptions)
        updateFactItemOptions(dts, newFactItemOptions, cntlr)
        dts.modelManager.showStatus(_("EBA compliance improved"), 5000)
        cntlr.reloadTableView(dts)
    except Exception as ex:
        dts.error("exception",
            _("EBA compliance improvements generation exception: %(error)s"), error=ex,
            modelXbrl=dts,
            exc_info=True)

def deleteUnusedUnits(dts):
    allUnits = dts.units
    unitIDs = set(allUnits.keys())
    unusedUnitIDs = unitIDs - {fact.unitID 
                                       for fact in dts.factsInInstance
                                       if fact.unitID}
    for unitID in unusedUnitIDs:
        unit = allUnits[unitID]
        if unit is not None: # ignore already deleted units
            allUnits[unitID] = None # units cannot be deleted in this list because of the unit numbering
            parent = unit.getparent()
            parent.remove(unit)
    someUnitsHaveBeenDeleted = len(unusedUnitIDs)>0
    if someUnitsHaveBeenDeleted:
        dts.setIsModified()
    return someUnitsHaveBeenDeleted

def deleteNilFacts(dts, contlr):
    contlr.addToLog(_("Removal of empty facts and unused contexts started."))
    nilFacts = dts.factIndex.nilFacts(dts)
    parent = None
    for fact in nilFacts:
        parent = removeFactInModel(dts, fact)
    contextsDeleted = deleteUnusedContexts(dts)
    unitsDeleted = deleteUnusedUnits(dts)
    if contextsDeleted or unitsDeleted:
        # Validate everything
        XmlValidate.validate(dts, dts.modelDocument.xmlRootElement)
    elif parent is not None:
        XmlValidate.validate(dts, parent)
    numberOfNilFacts = len(nilFacts)
    if numberOfNilFacts>0:
        dts.setIsModified()
    contlr.addToLog(_("Removal of empty facts and unused contexts finished successfully. %s empty facts deleted." % numberOfNilFacts))

def removeFactInModel(dts, fact):
    dts.factsInInstance.remove(fact)
    dts.factIndex.deleteFact(fact)
    dts.facts.remove(fact)
    if fact in dts.undefinedFacts:
        dts.undefinedFacts.remove(fact)
    dts.modelObjects[fact.objectIndex] = None # objects found by index, can't remove position from list
    
    parent = fact.getparent()
    parent.remove(fact)
    fact.clear()
    return parent

def deleteUnusedContexts(dts):
    allContexts = dts.contexts
    cntxIDs = set(allContexts.keys())
    unusedCntxIDs = cntxIDs - {fact.contextID 
                                       for fact in dts.factsInInstance
                                       if fact.contextID}
    for cntxID in unusedCntxIDs:
        context = allContexts[cntxID]
        if context is not None: # ignore already deleted contexts
            allContexts[cntxID] = None # contexts cannot be deleted in this list because of the context numbering
            parent = context.getparent()
            parent.remove(context)
    someContextsHaveBeenDeleted = len(unusedCntxIDs)>0
    if someContextsHaveBeenDeleted:
        dts.setIsModified()
    return someContextsHaveBeenDeleted

def createOrReplaceFilingIndicators(dts, allFilingIndicatorCodes, newFactItemOptions):
    filingIndicatorsElements = dts.factsByQname(qnFindFilingIndicators, set())
    if len(filingIndicatorsElements)>0:
        filingIndicatorsElement = filingIndicatorsElements.pop()
    else:
        filingIndicatorsElement = None
    if filingIndicatorsElement is not None:
        parent = filingIndicatorsElement.getparent()
        removeUselessFilingIndicatorsInModel(dts)
        XmlValidate.validate(dts, parent) # must validate after content is deleted
    if len(allFilingIndicatorCodes)>0:
        filingIndicatorsElement = createFilingIndicatorsElement(dts, newFactItemOptions)
        for filingIndicatorCode in allFilingIndicatorCodes:
            dts.createFact(qnFindFilingIndicator, 
                           parent=filingIndicatorsElement,
                           attributes={"contextRef": "c"}, 
                           text=filingIndicatorCode,
                           validate=False)
        XmlValidate.validate(dts, filingIndicatorsElement) # must validate after content is created

def removeUselessFilingIndicatorsInModel(dts):
    ''':type dts: ModelXbrl'''
    # First remove the context
    context = dts.contexts["c"]
    parent = context.getparent()
    parent.remove(context)
    del dts.contexts["c"]
    # Remove the elements from the facts and factsInInstance data structure
    filingIndicatorsElements = dts.factsByQname(qnFindFilingIndicators, set())
    for fact in filingIndicatorsElements:
        removeFactInModel(dts, fact)
    filingIndicatorElements = dts.factsByQname(qnFindFilingIndicator, set())
    for fact in filingIndicatorElements:
        dts.factsInInstance.remove(fact)
        dts.factIndex.deleteFact(fact)
        # non-top-level elements are not in 'facts'
    dts.setIsModified()

def createFilingIndicatorsElement(dts, newFactItemOptions):
    dts.createContext(newFactItemOptions.entityIdentScheme,
        newFactItemOptions.entityIdentValue,
        'instant',
        None,
        newFactItemOptions.endDateDate,
        None, # no dimensional validity checking (like formula does)
        {}, [], [],
        id='c',
        afterSibling=ModelXbrl.AUTO_LOCATE_ELEMENT)
    filingIndicatorsTuple = dts.createFact(qnFindFilingIndicators,
                                           validate=False)
    return filingIndicatorsTuple

def updateFactItemOptions(dts, newFactItemOptions, contlr):
    ''':type dts: ModelXbrl
       :type newFactItemOptions: NewFactItemOptions
    '''
    
    contlr.addToLog(_("Update of fact options started."))
    changedContexts = 0
    for fact in dts.facts:
        context = fact.context
        if context is not None:
            context.updateEntityIdentifierElement(newFactItemOptions.entityIdentScheme,
                                                  newFactItemOptions.entityIdentValue)
            context.updatePeriod(newFactItemOptions.startDate,
                                 newFactItemOptions.endDate)
            changedContexts += 1
    if changedContexts>0:
        dts.setIsModified()
    contlr.addToLog(_("Update of fact options finished successfully. %s facts updated." % changedContexts))

def improveEbaComplianceMenuExtender(cntlr, menu):
    # Extend menu with an item for the improve compliance menu
    menu.add_command(label=_("Improve EBA compliance"), 
                     underline=0, 
                     command=lambda: improveEbaComplianceMenuCommand(cntlr) )

def improveEbaComplianceMenuCommand(cntlr):
    # improve EBA compliance menu item has been invoked
    if cntlr.modelManager is None or cntlr.modelManager.modelXbrl is None:
        cntlr.addToLog(_("No DTS loaded."))
        return
    dts = cntlr.modelManager.modelXbrl
    getFactItemOptions(dts, cntlr)
    import threading
    thread = threading.Thread(target=lambda 
                                  _dts=dts: 
                                        improveEbaCompliance(_dts, cntlr))
    thread.daemon = True
    thread.start()

def customNewFile(cntlr):
    dialog = DialogNewFileOptions(cntlr.parent)
    if dialog.accepted:
        newUrl = dialog.newUrl
        cntlr.fileOpenFile(newUrl)

def fileOpenExtender(cntlr, menu):
    menu.add_command(label=_('New EBA File...'), underline=0, command=lambda: customNewFile(cntlr) )

__pluginInfo__ = {
    'name': 'Improve EBA compliance of XBRL instances',
    'version': '1.5',
    'description': "This module extends the File menu and regenerates EBA filing indicators if needed and removes unused contexts and units.",
    'license': 'Apache-2',
    'author': 'Gregorio Mongelli (Acsone S. A.)',
    'copyright': '(c) Copyright 2014, 2015 Acsone S. A.',
    # classes of mount points (required)
    'CntlrWinMain.Menu.Tools': improveEbaComplianceMenuExtender,
    'CntlrWinMain.Menu.File.Open': fileOpenExtender
}
