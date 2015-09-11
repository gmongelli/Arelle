
from tkinter import *
try:
    from tkinter.ttk import *
except ImportError:
    from ttk import *
try:
    import regex as re
except ImportError:
    import re

def getActiveFormula(mainWin):
    selectionList = []
    modelManager =  mainWin.modelManager
    modelXbrl = modelManager.cntlr.getModelXbrl()
    schemaRef = "None"
    maxSingleFormulaRunTime = 0
    reportName = "No instance loaded"
    
    if modelXbrl is None:
        if False:
            # for testing purposes
            for i in range(25):
                label = "checBox #%s" % i
                selectionList.append(SelectionItem(label, label, True))
    else:
        schemaRef = modelXbrl.getSingleSchemaRef()
        reportName = modelXbrl.getReportName()
        # we use the schema as an identifier for a report of a taxonomy version...
        #TODO: should express this as a report name in a taxonomy version but things are not easily accessed for now
        # get previous settings for this schema if any
        reportFormulaSettings = modelManager.getActiveFormulaForModel(modelXbrl)
                        
        # get model variable sets and sort by id
        vsDict = {vs.id: vs for vs in modelXbrl.modelVariableSets}
        vsIds = sorted(vsDict.keys())
        for vsId in vsIds:
            vs = vsDict[vsId]
            selection = True
            # get actual selection from previous settings if any
            if reportFormulaSettings is not None:
                try:
                    selection = reportFormulaSettings[vs.id]
                except KeyError:
                    pass
            selectionList.append(SelectionItem(vs.id, getVsLabel(vs, modelXbrl), selection))
            
        maxSingleFormulaRunTime = modelManager.formulaOptions.maxSingleFormulaRunTime

    dialogTitle = _("Active formula selection")
    
    dialogInfo = schemaRef.replace("http://", "")
    if reportName is not None:
        dialogInfo = reportName + "\n" + dialogInfo
    dialog = DialogSelectionList(mainWin, dialogTitle, dialogInfo, selectionList, maxSingleFormulaRunTime)
    if dialog.accepted:
        if modelXbrl is not None:
            allSelected = True
            for vs in selectionList:
                if not(vs.sel):
                    allSelected = False
                    break
            if allSelected:
                # clear useless entries from config
                modelManager.setActiveFormulaForModel(modelXbrl, None)
            else:
                newSettings = {vs.itemId: vs.sel for vs in selectionList}
                modelManager.setActiveFormulaForModel(modelXbrl, newSettings)
            modelManager.formulaOptions.maxSingleFormulaRunTime = dialog.getMaxRuntime()
            mainWin.config["formulaParameters"] = modelManager.formulaOptions.__dict__.copy()
            mainWin.saveConfig()

def getVsLabel(modelVariableSet, modelXbrl):
    itemId = modelVariableSet.id
    label = modelVariableSet.xlinkLabel
    if itemId != label:
        label = itemId + " " + label
    classname = modelVariableSet.__class__.__name__
    classname = classname.replace("Model", "")
    aspectModel = modelVariableSet.aspectModel
    implicitFiltering = "impl=1" if modelVariableSet.implicitFiltering else "impl=0"
    test = str(modelVariableSet.test)
    
    # get last evaluation time if any
    lastTime = "??.??s"
    if modelXbrl.lastEvaluationTimesByModelVariableSetId is not None:
        try:
            lastTime = modelXbrl.lastEvaluationTimesByModelVariableSetId[itemId]
            if lastTime.startswith("-"):
                lastTime = ">" + lastTime[1:] + "<"
        except:
            pass
    result = " ".join([label, lastTime, classname, aspectModel, implicitFiltering, test])
    return result    
    
class SelectionItem:
    def __init__(self, itemId, label, isSelected):
        self.itemId = itemId
        self.label = label
        self.sel = isSelected
        self.valueVar = None
        self.cb = None
    
class DialogSelectionList(Toplevel):
    
    def __init__(self, mainWin, dialogTitle, dialogInfo, selectionList, maxSingleFormulaRunTime):
        self.parent = mainWin.parent
        self.modelManager = mainWin.modelManager
        super(DialogSelectionList, self).__init__(self.parent)
        self.selectionList = selectionList
        self.maxSingleFormulaRunTime = maxSingleFormulaRunTime
        
        parentGeometry = re.match("(\d+)x(\d+)[+]?([-]?\d+)[+]?([-]?\d+)", self.parent.geometry())
        dialogX = int(parentGeometry.group(3))
        dialogY = int(parentGeometry.group(4))
        self.accepted = False
        self.transient(self.parent)
        self.title(dialogTitle)
        
        # first frame with 2 rows and 3 columns
        # row 0 spans 3 cols and contains entry point
        # row 1 is used to enter the max runtime for a rule
        # row 2 spans the 3 columns and contains the bodyFrame
        # row 3 contains buttons in col 1 and 2
        # all stretch for row 1 col 0
        self.frame = Frame(self)
        self.frame.focus_set()
        
        self.frame.rowconfigure(0, weight=0)
        self.frame.rowconfigure(1, weight=0)
        self.frame.rowconfigure(2, weight=3)
        self.frame.rowconfigure(3, weight=0)
        self.frame.columnconfigure(0, weight=3)
        self.frame.columnconfigure(1, weight=0)
        self.frame.columnconfigure(2, weight=0)
        self.frame.columnconfigure(3, weight=0)
        self.frame.columnconfigure(4, weight=0)
        self.frame.grid(row=0, column=0, sticky=(N, S, E, W), padx=3, pady=3)
        
        y = 0
        lbl = Label(self.frame, text=dialogInfo)
        lbl.grid(row=y, column=0, sticky=(N, E, W), padx=2, pady=2)
        y += 1

        lbl = Label(self.frame, text="Max. formula runtime (sec):")
        lbl.grid(row=y, column=0, sticky=(N, E), padx=2, pady=2)
        content = StringVar()
        content.set(self.maxSingleFormulaRunTime)
        self.maxFormulaRunTimeEntry = Entry(self.frame, width=10, textvariable=content)
        self.maxFormulaRunTimeEntry.grid(row=y, column=1, sticky=(N, W), padx=2, pady=2)
        y += 1
        
        # bodyFrame has 2 rows and 2 cols
        # row 0 col 0 form Text, row 0 col 1 for vscroll
        # row 1 spans the two cols for vscroll
        bodyFrame = Frame(self.frame)
        bodyFrame.columnconfigure(0, weight=3)
        bodyFrame.columnconfigure(1, weight=0)
        bodyFrame.rowconfigure(0, weight=3)
        bodyFrame.rowconfigure(1, weight=0)
        bodyFrame.grid(row=y, column=0, columnspan=5, sticky=(N, S, E, W), padx=3, pady=3)
        y += 1

        verticalScrollbar = Scrollbar(bodyFrame, orient=VERTICAL)
        horizontalScrollbar = Scrollbar(bodyFrame, orient=HORIZONTAL)
        
        yy = 0
        self.text = Text(bodyFrame, xscrollcommand=horizontalScrollbar.set, yscrollcommand=verticalScrollbar.set)
        self.text.grid(row=yy, column=0, sticky=(N, S, E, W))
        verticalScrollbar["command"] = self.text.yview
        verticalScrollbar.grid(row=yy, column=1, sticky=(N, S))   
        yy += 1
        
        horizontalScrollbar["command"] = self.text.xview
        horizontalScrollbar.grid(row=yy, column=0, sticky=(W, E))
        
        for selectionItem in selectionList:
            label = selectionItem.label.ljust(500)

            selectionItem.valueVar = StringVar() 
            selectionItem.valueVar.set(("1" if selectionItem.sel else "0"))
            cb = Checkbutton(self.text, text=label, variable=selectionItem.valueVar)
            self.text.window_create("end", window=cb)
            self.text.insert("end", "\n") # force one checkbox per line

            selectionItem.cb = cb
        
        selectAllButton = Button(self.frame, text=_("All"), command=self.selectAll)
        selectAllButton.grid(row=y, column=1, sticky=(S,E), pady=2, padx=2)
        selectNoneButton = Button(self.frame, text=_("None"), command=self.selectNone)
        selectNoneButton.grid(row=y, column=2, sticky=(S,E), pady=2, padx=2)
        okButton = Button(self.frame, text=_("OK"), command=self.ok)
        okButton.grid(row=y, column=3, sticky=(S,E), pady=2, padx=2)
        cancelButton = Button(self.frame, text=_("Cancel"), command=self.close)
        cancelButton.grid(row=y, column=4, sticky=(S,E), pady=2, padx=2)
        
        window = self.winfo_toplevel()
        window.columnconfigure(0, weight=1)
        self.geometry("+{0}+{1}".format(dialogX+50,dialogY+100))
        
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.grab_set()
        self.wait_window(self)

    def setOptions(self):
        for selectionItem in self.selectionList:
            selectionItem.sel = selectionItem.valueVar.get() == "1"
        try:
            mx = self.maxFormulaRunTimeEntry.get()
            maxFormulaRunTimeInt = int(mx)
            self.maxSingleFormulaRunTime = mx
        except:
            pass
    
    def getMaxRuntime(self):
        return self.maxSingleFormulaRunTime        
            
    def ok(self, event=None):
        self.setOptions()
        self.accepted = True
        self.close()
        
    def close(self, event=None):
        self.parent.focus_set()
        self.destroy()
    
    def selectAll(self, event=None):
        for selectionItem in self.selectionList:
            selectionItem.valueVar.set("1")
            
    def selectNone(self, event=None):
        for selectionItem in self.selectionList:
            selectionItem.valueVar.set("0")
        
    