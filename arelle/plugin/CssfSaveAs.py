'''
Created on Jan 27, 2015
Inspired by https://code.google.com/p/python-ttk/wiki/ttkWizard

@author: Gregorio Mongelli (Acsone S. A.)
(c) Copyright 2015 Acsone S. A., All rights reserved.
'''

from tkinter import Toplevel, N, S, E, W, messagebox
from arelle.EbaUtil import getFactItemOptions, isEbaInstance
from lxml import etree

try:
    from tkinter.ttk import Button, Frame
except ImportError:
    from ttk import Button, Frame
try:
    import regex as re
except ImportError:
    import re

from arelle.UiUtil import gridCell, gridCombobox, label
from arelle.CntlrWinTooltip import ToolTip


fetchSchemaRef = etree.XPath('/xbrl:xbrl/link:schemaRef/@xlink:href|/*/xbrl:xbrl/link:schemaRef/@xlink:href',
                             namespaces={ 'xbrl': 'http://www.xbrl.org/2003/instance',
                                         'link': 'http://www.xbrl.org/2003/linkbase',
                                         'xlink': 'http://www.w3.org/1999/xlink' })

# the following table has been extracted from:
# http://www.cssf.lu/fileadmin/files/Reporting_legal/Recueil_banques/Reporting_requirements_final_tc_270115.pdf
FINREP_REPORT = 'CFINRP'
SCOREP_REPORT = 'SCOREP'
xsdConversionTable = {'corep_ind.xsd' : SCOREP_REPORT,
                      'corep_le_ind.xsd' : 'SLAREX',
                      'corep_lcr_ind.xsd' : 'SLCRXX',
                      'corep_nsfr_ind.xsd' : 'SNSFRX',
                      'corep_con.xsd' : 'CCOREP',
                      'corep_le_con.xsd' : 'CLAREX',
                      'corep_lcr_con.xsd' : 'CLCRXX',
                      'corep_nsfr_con.xsd' : 'CNSFRX',
                      'finrep_con_ifrs.xsd' : FINREP_REPORT,
                      'ae_con.xsd' : 'CAEXXX',
                      'ae_ind.xsd' : 'SAEXXX',
                      'fp.xsd' : 'FPXXXX',
                      'sbp.xsd' : 'SBPXXX',
                      'sbpimv.xsd' : 'SBPIMV'}

# The following pattern is extracted from
# http://www.cssf.lu/fileadmin/files/Reporting_legal/transport_securisation_reporting/Convention_de_nom.pdf
CSSF_FILE_FORMAT = "COFREP-{E}{NNNNNNNN}-{YYYY}-{MM}-{TTTTTT}-00-{C}-{D}-{S}-{NAME}.xbrl"
CSSF_CODE_LENGTH = 8

COMPANY_TYPE_BANK = 'Bank'
COMPANY_TYPE_IF = 'Investment firm'
COMPANY_TYPE_VALUES = (COMPANY_TYPE_BANK, COMPANY_TYPE_IF)
COMPANY_TYPE_CODES = { COMPANY_TYPE_BANK : 'B', COMPANY_TYPE_IF: 'P'}
RATIO_TYPE_SIMP = 'Simplified'
RATIO_TYPE_INTGTED = 'Integrated'
RATIO_TYPE_DEFAULT = '-'
RATIO_TYPE_VALUES = (RATIO_TYPE_SIMP, RATIO_TYPE_INTGTED)
RATIO_TYPE_CODES = { RATIO_TYPE_SIMP : 'S', RATIO_TYPE_INTGTED : 'I', RATIO_TYPE_DEFAULT : '-'}
PRELIMINARY_FIGURES = 'Preliminary'
FINAL_FIGURES = 'Final'
FIGURES_TYPE_VALUES = (PRELIMINARY_FIGURES, FINAL_FIGURES)
FIGURES_TYPE_CODES = {PRELIMINARY_FIGURES : 'N', FINAL_FIGURES : 'D'}
ACCOUNTING_VERSION_DEFAULT = 'L'
ACCOUNTING_VERSION_VALUES = (ACCOUNTING_VERSION_DEFAULT, 'N')
ACCOUNTING_SUBSIDIARY = ('S',)
decimalsPattern = re.compile(r"^([0-9]+)$")
COREP_REPORT_SUFFIX = 'COREP'
CONSOLIDATED_REPORT_PREFIX = 'C'

class CssfSaveOptions(object):
    """
    .. class:: CssfSaveOptions(savedOptions=None)
    
    CssfSaveOptions persists parameters for saving a COREP/FINREP instance wit CSSF conventions.
    
    If savedOptions is provided (from configuration saved JSON file), then persisted last used
    values are used.
    
    Note that all attributes of this class must be compatible with JSON conversion. As long as the attributes
    are strings, they may safely be used.
    
    Properties of this class (all str):
    
    - entityType ['B' (bank) or 'P' investment firm]
    - cssfCode usually a number of up to 8 characters
    - ratioType ['I' (integrated), 'S' simplified or '-' default value]
    
    :param savedOptions: prior persisted dict of this class's attributes.
    """
    def __init__(self, savedOptions=None):
        self.entityType = ""
        self.cssfCode = ""
        self.ratioType = "-"
        self.figuresType = ""
        self.accountingVersion = ""
        if savedOptions is not None:
            self.__dict__.update(savedOptions)

class DialogCssfSaveOptions(Toplevel):
    def __init__(self, mainWin, options, reportType, endDate):
        self.reportType = reportType
        self.mainWin = mainWin
        self.endDate = endDate
        parent = mainWin
        super(DialogCssfSaveOptions, self).__init__(parent)
        self.parent = parent
        self.options = options
        parentGeometry = re.match("(\d+)x(\d+)[+]?([-]?\d+)[+]?([-]?\d+)", parent.geometry())
        dialogX = int(parentGeometry.group(3))
        dialogY = int(parentGeometry.group(4))
        self.accepted = False
        self.accountingVersionValues = ACCOUNTING_VERSION_VALUES
        if reportType == SCOREP_REPORT:
            self.accountingVersionValues = self.accountingVersionValues + ACCOUNTING_SUBSIDIARY

        self.transient(self.parent)
        self.title(_("Save As CSSF Options"))
        
        frame = Frame(self)

        label(frame, 1, 1, _("Entity type:"))
        self.cellEntityType = gridCombobox(frame, 2, 1, getattr(options,"entityType",""), values=COMPANY_TYPE_VALUES)
        ToolTip(self.cellEntityType, text=_("Select an entity type"), wraplength=240)
        label(frame, 1, 2, _("CSSF entity code:"))
        self.cellCssfCode = gridCell(frame, 2, 2, getattr(options,"cssfCode",""))
        ToolTip(self.cellCssfCode, text=_("Enter a CSSF entity code (up to {0} digits").format(CSSF_CODE_LENGTH), wraplength=240)
        currentRow = 3
        if reportType.endswith(COREP_REPORT_SUFFIX):
            label(frame, 1, currentRow, _("Ratio type:"))
            defaultValue = getattr(options, "ratioType","")
            if defaultValue not in RATIO_TYPE_VALUES:
                defaultValue = RATIO_TYPE_VALUES[0]
            self.cellRatioType = gridCombobox(frame, 2, currentRow, defaultValue, values=RATIO_TYPE_VALUES)
            ToolTip(self.cellRatioType, text=_("Select how the ratios are computed"), wraplength=240)
            currentRow += 1
        if reportType[0] != CONSOLIDATED_REPORT_PREFIX:
            label(frame, 1, currentRow, _("Accounting version:"))
            defaultValue = getattr(options, "accountingVersion", "")
            if defaultValue not in self.accountingVersionValues:
                defaultValue = ACCOUNTING_VERSION_DEFAULT
            self.cellAccountingVersion = gridCombobox(frame, 2, currentRow, defaultValue, values=self.accountingVersionValues)
            ToolTip(self.cellAccountingVersion, text=_("Select the accounting version"), wraplength=240)
            currentRow += 1
        if reportType == FINREP_REPORT:
            label(frame, 1, currentRow, _("Figures type:"))
            self.cellFiguresType = gridCombobox(frame, 2, currentRow, getattr(options,"figuresType",""), values=FIGURES_TYPE_VALUES)
            ToolTip(self.cellFiguresType, text=_("Select a figures type"), wraplength=240)
            currentRow += 1

        cancelButton = Button(frame, text=_("Cancel"), width=8, command=self.close)
        ToolTip(cancelButton, text=_("Cancel operation, discarding changes and entries"))
        okButton = Button(frame, text=_("OK"), width=8, command=self.ok)
        ToolTip(okButton, text=_("Accept the options as entered above"))
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
        if self.cellEntityType.value is None or self.cellEntityType.value not in COMPANY_TYPE_VALUES:
            errors.append(_("Entity type is invalid."))
        if self.reportType.endswith(COREP_REPORT_SUFFIX):
            if self.cellRatioType.value is None or self.cellRatioType.value not in RATIO_TYPE_VALUES:
                errors.append(_("Ratio type is invalid."))
        if self.cellCssfCode.value is None or len(self.cellCssfCode.value) == 0:
            errors.append(_("CSSF entity code must be supplied."))
        elif not decimalsPattern.match(self.cellCssfCode.value):
            errors.append(_("CSSF entity code is invalid. It must be composed of digits."))
        elif len(self.cellCssfCode.value) > CSSF_CODE_LENGTH:
            errors.append(_("CSSF entity code is too long. It must have at most {0} digits.").format(CSSF_CODE_LENGTH))
        if self.reportType[0] != CONSOLIDATED_REPORT_PREFIX:
            if self.cellAccountingVersion.value is None or self.cellAccountingVersion.value not in self.accountingVersionValues:
                errors.append(_("Accounting version is invalid."))
        if self.reportType == FINREP_REPORT:
            if self.cellFiguresType.value is None or self.cellFiguresType.value not in FIGURES_TYPE_VALUES:
                errors.append(_("Figures type is invalid."))
        if errors:
            messagebox.showwarning(_("Dialog validation error(s)"),
                                "\n".join(errors), parent=self)
            return False
        return True

    def setOptions(self):
        options = self.options
        options.entityType = self.cellEntityType.value
        options.cssfCode = self.cellCssfCode.value
        if self.reportType.endswith(COREP_REPORT_SUFFIX):
            options.ratioType = self.cellRatioType.value
        else:
            options.ratioType = '-'
        if self.reportType == FINREP_REPORT:
            options.figuresType = self.cellFiguresType.value
        else:
            options.figuresType = PRELIMINARY_FIGURES
        if self.reportType[0] != CONSOLIDATED_REPORT_PREFIX:
            options.accountingVersion = self.cellAccountingVersion.value
        else:
            options.accountingVersion = 'C'

    def ok(self, event=None):
        if not self.checkEntries():
            return
        self.setOptions()
        self.accepted = True
        self.close()

    def close(self, event=None):
        self.parent.focus_set()
        self.destroy()

    @property
    def cssfFileName(self):
        options = self.options
        fileName = CSSF_FILE_FORMAT.format(E=COMPANY_TYPE_CODES[options.entityType],
                                           NNNNNNNN=options.cssfCode.rjust(CSSF_CODE_LENGTH, '0'),
                                           YYYY=self.endDate[0:4],
                                           MM=self.endDate[5:7],
                                           TTTTTT=self.reportType,
                                           C=options.accountingVersion,
                                           D=FIGURES_TYPE_CODES[options.figuresType],
                                           S=RATIO_TYPE_CODES[options.ratioType],
                                           NAME=self.reportType)
        return fileName

def extractReportType(cntlr, dts):
    modelDocument = getattr(dts, 'modelDocument', None)
    if modelDocument is not None:
        foundSchemaRefs = fetchSchemaRef(modelDocument.xmlDocument)
        if foundSchemaRefs is not None and len(foundSchemaRefs)>0:
            schemaRef = foundSchemaRefs[0]
            xsdFileName = schemaRef.split('/')[-1]
            return xsdConversionTable[xsdFileName]
        else:
            return None
    else:
        return None

def getEndDate(cntlr, dts):
    newFactItemOptions = getFactItemOptions(dts, cntlr)
    if newFactItemOptions is not None:
        return newFactItemOptions.endDate
    else:
        return None

def customSaveAs(cntlr):
    if cntlr.modelManager is None or cntlr.modelManager.modelXbrl is None:
        cntlr.addToLog(_("No DTS loaded."))
        return
    dts = cntlr.modelManager.modelXbrl
    if not isEbaInstance(dts):
        dts.modelManager.showStatus(_("Only applicable to EBA instances."), 5000)
        return
    reportType = extractReportType(cntlr, dts)
    endDate = getEndDate(cntlr, dts)
    if endDate is not None and reportType is not None:
        cssfSaveOptions = CssfSaveOptions()
        for prevOptionKey, prevOptionValue in cntlr.config.get("cssfSaveOptions",{}).items():
            if getattr(cssfSaveOptions, prevOptionKey, None) is not None:
                cssfSaveOptions.__dict__[prevOptionKey] = prevOptionValue
        dialog = DialogCssfSaveOptions(cntlr.parent, cssfSaveOptions, reportType, endDate)
        if dialog.accepted:
            newFileName = dialog.cssfFileName
            if cntlr.fileSave(initialfile=newFileName):
                if dialog.options is not None:
                    cntlr.config["cssfSaveOptions"] = dialog.options.__dict__.copy()
                    cntlr.saveConfig()
    else:
        cntlr.addToLog(_("Custom 'Save As CSSF...' interrupted because the XBRL instance is not of the expected type."))

def fileMenuExtender(cntlr, menu):
    menu.add_command(label=_('Save As CSSF...'), underline=0, command=lambda: customSaveAs(cntlr) )

__pluginInfo__ = {
    # Do not use _( ) in pluginInfo itself (it is applied later, after loading
    'name': 'CSSF custom save as',
    'version': '1.0',
    'description': '''Save the current instance as a file with a name compliant with the CSSF filing rules.''',
    'license': 'Apache-2',
    'author': 'Acsone S. A.',
    'copyright': '(c) Copyright Acsone S. A., All rights reserved.',
    # classes of mount points (required)
    'CntlrWinMain.Menu.File.Save': fileMenuExtender
    
}
