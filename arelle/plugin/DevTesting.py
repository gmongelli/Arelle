'''
(c) Copyright 2015 Acsone S. A., All rights reserved.
'''
import gc
from pympler import muppy
import math

class RecordedTableLayout:
    def __init__(self):
        self.tableData = {} # dictionary of columns by row number
    
    def add(self, x, y, cellType, value):
        c = [cellType, value]
        try:
            col = self.tableData[str(y)]
        except:
            col = self.tableData[str(y)] = {}
        col[str(x)] = c
        
class TestContext:
    def __init__(self):
        self.tableLayout = RecordedTableLayout()
        self.checkMemoryOnClose = False
        self.dumpFilePrefix = None
        self.diffNumObjects = 0
        self.recordTableLayout = False
        self.saveFilePath = None # used instead of dialog question when creating a new report

    def __repr__(self):
        return super(TestContext, self).__repr__() + " recordTableLayout=" + str(self.recordTableLayout) + " checkMemoryOnClose=" + str(self.checkMemoryOnClose)

        
__testContext = TestContext()
    
def getTestContext():
    return __testContext

        
def fileCloseStart(cntlrWinMain, modelXbrl):
    print("Numdocs= " + str(len(modelXbrl.urlDocs)))

def fileCloseEnd(cntlrWinMain, filename):
    if __testContext.checkMemoryOnClose:
        gc.collect()
        try:
            xx = cntlrWinMain.prevNumObjects
            cntlrWinMain.dumpIdx
        except:
            cntlrWinMain.prevNumObjects = 0
            cntlrWinMain.dumpIdx = 0
        cntlrWinMain.dumpIdx += 1
        all_objects = muppy.get_objects()
        numObjects = len(all_objects)
        diffObjects = numObjects - cntlrWinMain.prevNumObjects
        cntlrWinMain.prevNumObjects = numObjects
        print("numObjects=" + str(numObjects) + " (" + str(diffObjects) + " more)")
        if False:
            with open(__testContext.dumpFilePrefix + str(cntlrWinMain.dumpIdx) + ".txt", "w") as text_file:
                idx = 0
                for o in all_objects:
                    idx += 1
                    otype = ""
                    try:
                        otype = str(type(o))
                    except:
                        pass
                    try:
                        print("type=" + otype + " " + str(o), file=text_file)
                    except:
                        pass
            all_objects =  None
            gc.collect()
            print(numObjects)
            print("End of close " + filename)
        __testContext.diffNumObjects = diffObjects
        
def getFilePath(cntlrWinMain, modelXbrl):
    return getTestContext().saveFilePath

def initCellValue(value, x, y):
    if __testContext.recordTableLayout:
        __testContext.tableLayout.add(x, y, "v", value)

def initCellCombobox(value, values, x, y):
    if __testContext.recordTableLayout:
        __testContext.tableLayout.add(x, y, "cb", value)

def initHeaderCellValue(headerLabel, x, y):
    if __testContext.recordTableLayout:
        __testContext.tableLayout.add(x, y, "h", headerLabel)

def initHeaderCombobox(x, y):
    if __testContext.recordTableLayout:
        __testContext.tableLayout.add(x, y, "hcb", None)
    
def humanizeSize(size):
    size = abs(size)
    if (size==0):
        return "0B"
    units = ['B','KiB','MiB','GiB','TiB','PiB','EiB','ZiB','YiB']
    p = math.floor(math.log(size, 2)/10)
    return "%.3f %s" % (size/math.pow(1024,p),units[int(p)])

__pluginInfo__ = {
    'name': 'Development utilities',
    'version': '1.0',
    'description': "Testing and development utilities",
    'license': 'Apache-2',
    'author': 'Acsone',
    'copyright': '(c) Copyright 2015 Acsone S. A.',
    # classes of mount points (required)
    'DevTesting.FileCloseStart': fileCloseStart,
    'DevTesting.FileCloseEnd': fileCloseEnd,
    'DevTesting.GetFilePath': getFilePath,
    'DevTesting.InitCellValue': initCellValue,
    'DevTesting.InitCellCombobox': initCellCombobox,
    'DevTesting.InitHeaderCellValue': initHeaderCellValue,
    'DevTesting.InitHeaderCombobox': initHeaderCombobox,    
    'DevTesting.GetTestContext': getTestContext   
}