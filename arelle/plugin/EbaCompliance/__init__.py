'''
Improve the EBA compliance of the currently loaded facts.

For the time being, there are only three improvements that are implemented:
1. The filing indicators are regenerated using a fixed context with ID "c".
2. The nil facts and the unused contexts and units are removed
3. The entity scheme, the entity ID, the period start and the period end date are updated for every fact.

Moreover, a new File > New EBA File... menu entry is provided to ease the creation of the
latest EBA instances.

(c) Copyright 2014, 2015 Acsone S.A., All rights reserved.
'''

from arelle import ModelDocument, XmlValidate, ModelXbrl, XbrlConst
from arelle.ModelValue import qname
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

EBA_TAXONOMY_VERSION_2_0 = '2.0'
EBA_TAXONOMY_VERSION_2_1 = '2.1'
EBA_TAXONOMY_VERSION_2_2 = '2.2'
EBA_TAXONOMY_VERSION_2_3_1 = '2.3.1'
EBA_TAXONOMY_VERSION_2_4 = '2.4'
EBA_TAXONOMY_DEFAULT_VERSION = EBA_TAXONOMY_VERSION_2_4
EBA_TAXONOMY_VERSIONS_VALUES = (EBA_TAXONOMY_VERSION_2_4, EBA_TAXONOMY_VERSION_2_3_1, EBA_TAXONOMY_VERSION_2_2, EBA_TAXONOMY_VERSION_2_1, EBA_TAXONOMY_VERSION_2_0) 
EBA_REPORTING_INDIVIDUAL = 'Individual'
EBA_REPORTING_CONSOLIDATED = 'Consolidated'
EBA_REPORTING_TYPES_VALUES = (EBA_REPORTING_INDIVIDUAL, EBA_REPORTING_CONSOLIDATED)
EBA_REPORTING_TYPE_DEFAULT = EBA_REPORTING_INDIVIDUAL
EBA_ENTRY_POINTS_INDIVIDUAL_2_0 = {
     'Liquidity Coverage - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2013-02/2013-12-01/mod/corep_lcr_ind.xsd',
     'Large Exposures - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2013-02/2013-12-01/mod/corep_le_ind.xsd',
     'Stable Funding - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2013-02/2013-12-01/mod/corep_nsfr_ind.xsd',
     'Common Reporting - Own Funds and Leverage' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2013-02/2013-12-01/mod/corep_ind.xsd'
     }
EBA_ENTRY_POINTS_INDIVIDUAL_2_1 = {
     'Asset Encumbrance' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/ae/its-2013-04/2014-03-31/mod/ae_ind.xsd',
     'Common Reporting - Own Funds and Leverage' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2013-02/2014-03-31/mod/corep_ind.xsd',
     'Liquidity Coverage - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2013-02/2014-03-31/mod/corep_lcr_ind.xsd',
     'Large Exposures - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2013-02/2014-03-31/mod/corep_le_ind.xsd',
     'Stable Funding - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2013-02/2014-03-31/mod/corep_nsfr_ind.xsd'
     }
EBA_ENTRY_POINTS_INDIVIDUAL_2_2 = {
     'Asset Encumbrance' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/ae/its-2013-04/2014-07-31/mod/ae_ind.xsd',
     'Common Reporting - Own Funds and Leverage' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2013-02/2014-07-31/mod/corep_ind.xsd',
     'Liquidity Coverage - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2013-02/2014-07-31/mod/corep_lcr_ind.xsd',
     'Large Exposures - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2013-02/2014-07-31/mod/corep_le_ind.xsd',
     'Stable Funding - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2013-02/2014-07-31/mod/corep_nsfr_ind.xsd'
     }
EBA_ENTRY_POINTS_INDIVIDUAL_2_3_1 = {
     'Common Reporting - Own Funds and Leverage' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2014-05/2015-02-16/mod/corep_ind.xsd',
     'Liquidity Coverage - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2014-05/2015-02-16/mod/corep_lcr_ind.xsd',
     'Large Exposures - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2014-05/2015-02-16/mod/corep_le_ind.xsd',
     'Stable Funding - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2014-05/2015-02-16/mod/corep_nsfr_ind.xsd',
     'Additional Liquidity Monitoring - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2014-05/2015-02-16/mod/corep_alm_ind.xsd',
     'Funding Plans' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/fp/gl-2014-04/2015-05-29/mod/fp_ind.xsd',
     'Supervisory Benchmarking Portfolios' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/sbp/cp-2014-07/2015-05-29/mod/sbp_ind.xsd',
     'Initial Market Valuation for Supervisory Benchmarking Portfolios' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/sbp/cp-2014-07/2015-05-29/mod/sbpimv_ind.xsd'
      }
EBA_ENTRY_POINTS_INDIVIDUAL_2_4 = {
     'Common Reporting - Own Funds and Leverage' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2015-04/2015-08-31/mod/corep_ind.xsd',
     'Liquidity Coverage - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2015-04/2015-08-31/mod/corep_lcr_ind.xsd',
     'Large Exposures - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2015-04/2015-08-31/mod/corep_le_ind.xsd',
     'Stable Funding - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2015-04/2015-08-31/mod/corep_nsfr_ind.xsd',
     'Additional Liquidity Monitoring - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2015-04/2015-08-31/mod/corep_alm_ind.xsd',
     
     'Funding Plans' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/fp/gl-2014-04/2015-05-29/mod/fp_ind.xsd', #same as 2.3.1
     
     'Supervisory Benchmarking Portfolios' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/sbp/cp-2014-07/2015-08-31/mod/sbp_ind.xsd',
     'Initial Market Valuation for Supervisory Benchmarking Portfolios' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/sbp/cp-2014-07/2015-08-31/mod/sbpimv_ind.xsd',     
     'Financial Reporting, National GAAP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/finrep/its-2015-02-ind/2015-08-31/mod/finrep_ind_gaap.xsd',
     'Financial Reporting, IFRS' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/finrep/its-2015-02-ind/2015-08-31/mod/finrep_ind_ifrs.xsd'
     
      }
EBA_ENTRY_POINTS_INDIVIDUAL_BY_VERSION = {
     EBA_TAXONOMY_VERSION_2_0: EBA_ENTRY_POINTS_INDIVIDUAL_2_0,
     EBA_TAXONOMY_VERSION_2_1: EBA_ENTRY_POINTS_INDIVIDUAL_2_1,
     EBA_TAXONOMY_VERSION_2_2: EBA_ENTRY_POINTS_INDIVIDUAL_2_2,
     EBA_TAXONOMY_VERSION_2_3_1: EBA_ENTRY_POINTS_INDIVIDUAL_2_3_1,
     EBA_TAXONOMY_VERSION_2_4 : EBA_ENTRY_POINTS_INDIVIDUAL_2_4
     }
EBA_ENTRY_POINTS_CONSOLIDATED_2_0 = {
     'Common Reporting - Own Funds and Leverage' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2013-02/2013-12-01/mod/corep_con.xsd',
     'Liquidity Coverage - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2013-02/2013-12-01/mod/corep_lcr_con.xsd',
     'Large Exposures - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2013-02/2013-12-01/mod/corep_le_con.xsd',
     'Stable Funding - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2013-02/2013-12-01/mod/corep_nsfr_con.xsd',
     'Financial Reporting, Consolidated National GAAP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/finrep/its-2013-02/2013-12-01/mod/finrep_con_gaap.xsd',
     'Financial Reporting, Consolidated IFRS' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/finrep/its-2013-02/2013-12-01/mod/finrep_con_ifrs.xsd'
     }
EBA_ENTRY_POINTS_CONSOLIDATED_2_1 = {
     'Asset Encumbrance' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/ae/its-2013-04/2014-03-31/mod/ae_con.xsd',
     'Common Reporting - Own Funds and Leverage' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2013-02/2014-03-31/mod/corep_con.xsd',
     'Liquidity Coverage - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2013-02/2014-03-31/mod/corep_lcr_con.xsd',
     'Large Exposures - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2013-02/2014-03-31/mod/corep_le_con.xsd',
     'Stable Funding - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2013-02/2014-03-31/mod/corep_nsfr_con.xsd',
     'Financial Reporting, Consolidated National GAAP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/finrep/its-2013-03/2014-03-31/mod/finrep_con_gaap.xsd',
     'Financial Reporting, Consolidated IFRS' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/finrep/its-2013-03/2014-03-31/mod/finrep_con_ifrs.xsd'
     }
EBA_ENTRY_POINTS_CONSOLIDATED_2_2 = {
     'Asset Encumbrance' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/ae/its-2013-04/2014-07-31/mod/ae_con.xsd',
     'Common Reporting - Own Funds and Leverage' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2013-02/2014-07-31/mod/corep_con.xsd',
     'Liquidity Coverage - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2013-02/2014-07-31/mod/corep_lcr_con.xsd',
     'Large Exposures - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2013-02/2014-07-31/mod/corep_le_con.xsd',
     'Stable Funding - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2013-02/2014-07-31/mod/corep_nsfr_con.xsd',
     'Financial Reporting,National GAAP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/finrep/its-2013-03/2014-07-31/mod/finrep_con_gaap.xsd',
     'Financial Reporting, IFRS' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/finrep/its-2013-03/2014-07-31/mod/finrep_con_ifrs.xsd',
     'Funding Plans' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/fp/gl-2014-04/2014-07-31/mod/fp.xsd'
     }
EBA_ENTRY_POINTS_CONSOLIDATED_2_3_1 = {
     'Common Reporting - Own Funds and Leverage' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2014-05/2015-02-16/mod/corep_con.xsd',
     'Liquidity Coverage - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2014-05/2015-02-16/mod/corep_lcr_con.xsd',
     'Large Exposures - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2014-05/2015-02-16/mod/corep_le_con.xsd',
     'Stable Funding - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2014-05/2015-02-16/mod/corep_nsfr_con.xsd',
     'Additional Liquidity Monitoring - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2014-05/2015-02-16/mod/corep_alm_con.xsd',
     'Financial Reporting, National GAAP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/finrep/its-2014-05/2015-02-16/mod/finrep_con_gaap.xsd',
     'Financial Reporting, IFRS' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/finrep/its-2014-05/2015-02-16/mod/finrep_con_ifrs.xsd',
     'Funding Plans' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/fp/gl-2014-04/2015-05-29/mod/fp_con.xsd',
     'Supervisory Benchmarking Portfolios' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/sbp/cp-2014-07/2015-05-29/mod/sbp_con.xsd',
     'Initial Market Valuation for Supervisory Benchmarking Portfolios' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/sbp/cp-2014-07/2015-05-29/mod/sbpimv_con.xsd'
     }
EBA_ENTRY_POINTS_CONSOLIDATED_2_4 = {
     'Common Reporting - Own Funds and Leverage' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2015-04/2015-08-31/mod/corep_con.xsd',
     'Liquidity Coverage - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2015-04/2015-08-31/mod/corep_lcr_con.xsd',
     'Large Exposures - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2015-04/2015-08-31/mod/corep_le_con.xsd',
     'Stable Funding - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2015-04/2015-08-31/mod/corep_nsfr_con.xsd',
     'Additional Liquidity Monitoring - COREP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/corep/its-2015-04/2015-08-31/mod/corep_alm_con.xsd',
     
     'Funding Plans' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/fp/gl-2014-04/2015-05-29/mod/fp_con.xsd',  #same as 2.3.1
     
     'Supervisory Benchmarking Portfolios' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/sbp/cp-2014-07/2015-08-31/mod/sbp_con.xsd',
     'Initial Market Valuation for Supervisory Benchmarking Portfolios' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/sbp/cp-2014-07/2015-08-31/mod/sbpimv_con.xsd',     
     'Financial Reporting, National GAAP' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/finrep/its-2015-02/2015-08-31/mod/finrep_con_gaap.xsd',
     'Financial Reporting, IFRS' : 'http://www.eba.europa.eu/eu/fr/xbrl/crr/fws/finrep/its-2015-02/2015-08-31/mod/finrep_con_ifrs.xsd'
     
     }
EBA_ENTRY_POINTS_CONSOLIDATED_BY_VERSION = {
     EBA_TAXONOMY_VERSION_2_0: EBA_ENTRY_POINTS_CONSOLIDATED_2_0,
     EBA_TAXONOMY_VERSION_2_1: EBA_ENTRY_POINTS_CONSOLIDATED_2_1,
     EBA_TAXONOMY_VERSION_2_2: EBA_ENTRY_POINTS_CONSOLIDATED_2_2,
     EBA_TAXONOMY_VERSION_2_3_1: EBA_ENTRY_POINTS_CONSOLIDATED_2_3_1,
     EBA_TAXONOMY_VERSION_2_4: EBA_ENTRY_POINTS_CONSOLIDATED_2_4
     }
EBA_ENTRY_POINTS_BY_VERSION_BY_REPORT_TYPE = {
     EBA_REPORTING_INDIVIDUAL: EBA_ENTRY_POINTS_INDIVIDUAL_BY_VERSION,
     EBA_REPORTING_CONSOLIDATED: EBA_ENTRY_POINTS_CONSOLIDATED_BY_VERSION
     }
ALL_EBA_ENTRY_POINTS = [EBA_ENTRY_POINTS_INDIVIDUAL_2_4, EBA_ENTRY_POINTS_CONSOLIDATED_2_4,
                        EBA_ENTRY_POINTS_INDIVIDUAL_2_3_1, EBA_ENTRY_POINTS_CONSOLIDATED_2_3_1,
                        EBA_ENTRY_POINTS_INDIVIDUAL_2_2, EBA_ENTRY_POINTS_CONSOLIDATED_2_2,
                        EBA_ENTRY_POINTS_INDIVIDUAL_2_1, EBA_ENTRY_POINTS_CONSOLIDATED_2_1,
                        EBA_ENTRY_POINTS_INDIVIDUAL_2_0, EBA_ENTRY_POINTS_CONSOLIDATED_2_0
                        ]

class EbaNewFileOptions(object):
    def __init__(self, ebaTaxonomyVersion, ebaReportingType, ebaEntryPointKey):
        self.ebaTaxonomyVersion = ebaTaxonomyVersion
        self.ebaReportingType = ebaReportingType
        self.ebaEntryPointKey = ebaEntryPointKey

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
        
        self.ebaTaxonomyVersion = EBA_TAXONOMY_DEFAULT_VERSION
        self.ebaReportingType = EBA_REPORTING_TYPE_DEFAULT
        self.setEntryPoints()
        self.ebaEntryPointKey = self.ebaEntryPointValues[0]
        self.options = EbaNewFileOptions(self.ebaTaxonomyVersion, self.ebaReportingType,
                                         self.ebaEntryPointValues[0])
        
        options = self.options

        self.transient(self.parent)
        self.title(_("New EBA File"))
        
        frame = Frame(self)
        frame.focus_set()
        
        label(frame, 1, 1, _("Taxonomy version:"))
        self.cellTaxonomyVersion = gridCombobox(frame, 2, 1, getattr(options,"ebaTaxonomyVersion", ""),
                                           values=EBA_TAXONOMY_VERSIONS_VALUES,
                                           comboboxselected = self.onTaxonomyVersionChanged,
                                           width=40)
        ToolTip(self.cellTaxonomyVersion, text=_("Select a taxonomy version"), wraplength=240)

        label(frame, 1, 2, _("EBA reporting type:"))
        self.cellReportType = gridCombobox(frame, 2, 2, getattr(options,"ebaReportingType", ""),
                                           values=EBA_REPORTING_TYPES_VALUES,
                                           comboboxselected = self.onReportTypeChanged,
                                           width=40)
        ToolTip(self.cellReportType, text=_("Select a report type"), wraplength=240)
        label(frame, 1, 3, _("Entry point:"))
        self.cellEntryPoint = gridCombobox(frame, 2, 3, getattr(options,"ebaEntryPointKey", ""),
                                           values=self.ebaEntryPointValues,
                                           comboboxselected = self.onEntryPointChanged,
                                           width=40)
        ToolTip(self.cellEntryPoint, text=_("Select an EBA entry point"), wraplength=240)
        currentRow = 4
        
        self.setEntryPointsCombo()


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
        if self.cellTaxonomyVersion.value is None or self.cellTaxonomyVersion.value not in EBA_TAXONOMY_VERSIONS_VALUES:
            errors.append(_("Please select a taxonomy version."))
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
        options.ebaTaxonomyVersion = self.ebaTaxonomyVersion
        options.ebaReportingType = self.ebaReportingType
        options.ebaEntryPointKey = self.ebaEntryPointKey

    def ok(self, event=None):
        if not self.checkEntries():
            return
        self.setOptions()
        self.accepted = True
        self.close()
        #print("ebaTaxonomyVersion=" + self.ebaTaxonomyVersion)
        #print("ebaReportingType=" + self.ebaReportingType)
        #print("ebaEntryPointKey=" + self.ebaEntryPointKey)
        #print("newURL=" + self.newUrl)

    def close(self, event=None):
        self.parent.focus_set()
        self.destroy()

    def onEntryPointChanged(self, event):
        combobox = event.widget
        self.ebaEntryPointKey = combobox.value

    def onReportTypeChanged(self, event):
        combobox = event.widget
        self.ebaReportingType = combobox.value
        self.setEntryPointsCombo()

    def onTaxonomyVersionChanged(self, event):
        combobox = event.widget
        self.ebaTaxonomyVersion = combobox.value
        self.setEntryPointsCombo()

    def setEntryPointsCombo(self):
        self.setEntryPoints()
        self.cellEntryPoint['values'] = self.ebaEntryPointValues
        # reuse the same selection if possible
        if self.cellEntryPoint.value not in self.ebaEntryPointValues:
            self.cellEntryPoint.current(0)
            self.ebaEntryPointKey = self.ebaEntryPointValues[0]

    def setEntryPoints(self):
        self.entryPoints = EBA_ENTRY_POINTS_BY_VERSION_BY_REPORT_TYPE.get(self.ebaReportingType).get(self.ebaTaxonomyVersion)
        self.ebaEntryPointValues = sorted(self.entryPoints.keys())

    @property
    def newUrl(self):
        options = self.options
        urlsByEntryPoint = EBA_ENTRY_POINTS_BY_VERSION_BY_REPORT_TYPE.get(self.ebaReportingType).get(self.ebaTaxonomyVersion)
        return urlsByEntryPoint[options.ebaEntryPointKey]
    
    @property
    def reportName(self):
        return self.options.ebaEntryPointKey

def improveEbaCompliance(modelXbrl, cntlr, lang="en"):
    ':type modelXbrl: ModelXbrl'
    try:
        if not isEbaInstance(modelXbrl, checkAlsoEiopa=True):
            modelXbrl.modelManager.showStatus(_("Only applicable to EBA instances"), 5000)
            return
        modelXbrl.modelManager.showStatus(_("Improving the EBA compliance"))
        deleteNilFacts(modelXbrl, cntlr)
        factWalkingAction = FactWalkingAction(modelXbrl)
        newFactItemOptions = getFactItemOptions(modelXbrl, cntlr)
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

        groupTableRels = modelXbrl.modelXbrl.relationshipSet(XbrlConst.euGroupTable)
        modelTables = []

        def viewTable(modelTable, factWalkingAction):
            # Use this code to walk through the tables.
            # For the time being, it is no longer needed.
            #if isinstance(modelTable, (ModelEuTable, ModelTable)):
            #    # status
            #    modelXbrl.modelManager.cntlr.addToLog("improving: " + modelTable.id)

            #    viewWalkerRenderedGrid(modelXbrl,
            #                           factWalkingAction,
            #                           lang=lang,
            #                           viewTblELR=modelTable,
            #                           sourceView=View(modelTable, False, False, True))

            #for rel in groupTableRels.fromModelObject(modelTable):
            #    viewTable(rel.toModelObject, factWalkingAction)
            pass

    
        for rootConcept in groupTableRels.rootConcepts:
            sourceline = 0
            for rel in modelXbrl.modelXbrl.relationshipSet(XbrlConst.euGroupTable).fromModelObject(rootConcept):
                sourceline = rel.sourceline
                break
            modelTables.append((rootConcept, sourceline))
            
        for modelTable, order in sorted(modelTables, key=lambda x: x[1]):  # @UnusedVariable
            viewTable(modelTable, factWalkingAction)

        updateFactItemOptions(modelXbrl, newFactItemOptions, cntlr)
        modelXbrl.modelManager.showStatus(_("EBA compliance improved"), 5000)
        cntlr.reloadTableView(modelXbrl)
    except Exception as ex:
        modelXbrl.error("exception",
            _("EBA compliance improvements generation exception: %(error)s"), error=ex,
            modelXbrl=modelXbrl,
            exc_info=True)

def deleteNilFacts(modelXbrl, contlr):
    contlr.addToLog(_("Removal of empty facts and unused contexts started."))
    numberOfNilFacts = modelXbrl.deleteNilFacts()
    contlr.addToLog(_("Removal of empty facts and unused contexts finished successfully. %s empty facts deleted." % numberOfNilFacts))

'''
def removeUselessFilingIndicatorsInModel(modelXbrl):
    '' ':type dts: ModelXbrl'' '
    # First remove the context
    if 'c' in modelXbrl.contexts:
        context = modelXbrl.contexts["c"]
        parent = context.getparent()
        parent.remove(context)
        del modelXbrl.contexts["c"]
    # Remove the elements from the facts and factsInInstance data structure
    filingIndicatorsElements = modelXbrl.factsByQname(qnFindFilingIndicators, set())
    for fact in filingIndicatorsElements:
        modelXbrl.removeFactInModel(fact)
    filingIndicatorElements = modelXbrl.factsByQname(qnFindFilingIndicator, set())
    for fact in filingIndicatorElements:
        modelXbrl.removeFact(fact)
        # non-top-level elements are not in 'facts'
    modelXbrl.setIsModified()

    
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
'''

def updateFactItemOptions(modelXbrl, newFactItemOptions, contlr):
    ''':type dts: ModelXbrl
       :type newFactItemOptions: NewFactItemOptions
    '''
    
    contlr.addToLog(_("Update of fact options started."))
    changedContexts = 0
    for fact in modelXbrl.facts:
        context = fact.context
        if context is not None:
            context.updateEntityIdentifierElement(newFactItemOptions.entityIdentScheme,
                                                  newFactItemOptions.entityIdentValue)
            context.updatePeriod(newFactItemOptions.startDate,
                                 newFactItemOptions.endDate)
            changedContexts += 1
    try:
        filingIndicatorsContext = modelXbrl.contexts["c"]
        filingIndicatorsContext.updateEntityIdentifierElement(newFactItemOptions.entityIdentScheme,
                                              newFactItemOptions.entityIdentValue)
        filingIndicatorsContext.updatePeriod(newFactItemOptions.startDate,
                             newFactItemOptions.endDate)
    except:
        pass
    if changedContexts > 0:
        modelXbrl.setIsModified()
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
    modelXbrl = cntlr.modelManager.modelXbrl
    getFactItemOptions(modelXbrl, cntlr)
    import threading
    thread = threading.Thread(target=lambda 
                                  _modelXbrl=modelXbrl: 
                                        improveEbaCompliance(_modelXbrl, cntlr))
    thread.daemon = True
    thread.start()

def customNewFile(cntlr):
    dialog = DialogNewFileOptions(cntlr.parent)
    if dialog.accepted:
        newUrl = dialog.newUrl
        reportName = dialog.reportName
        cntlr.fileOpenFile(newUrl, reportName=reportName)

def getReportNameFromEntryPoint(cntlr, entryPoint):
    for reportGroup in ALL_EBA_ENTRY_POINTS:
        for reportName, ep in reportGroup.items():
            if ep == entryPoint:
                return reportName
    return None                 
    
def fileOpenExtender(cntlr, menu):
    menu.add_command(label=_('New EBA File...'), underline=0, command=lambda: customNewFile(cntlr) )

__pluginInfo__ = {
    'name': 'Improve EBA compliance and help create new EBA report',
    'version': '1.10',
    'description': '''This module extends the File menu with the 'New EBA File...' entry
that helps choosing a new EBA report.
When saving XBRL instances, it also removes any nil facts and unused contexts and units.''',
    'license': 'Apache-2',
    'author': 'Acsone S.A.',
    'copyright': '(c) Copyright 2014, 2015 Acsone S.A.',
    # classes of mount points (required)
    'CntlrWinMain.Menu.Tools': improveEbaComplianceMenuExtender,
    'CntlrWinMain.Menu.File.Open': fileOpenExtender,
    'GetReportNameFromEntryPoint': getReportNameFromEntryPoint
}
