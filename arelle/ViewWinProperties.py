'''
Created on Oct 5, 2010

@author: Mark V Systems Limited
(c) Copyright 2010 Mark V Systems Limited, All rights reserved.
'''
from arelle import (ViewWinTree, ModelObject)
from tkinter import TRUE

def viewProperties(modelXbrl, tabWin):
    modelXbrl.modelManager.showStatus(_("viewing properties"))
    view = ViewProperties(modelXbrl, tabWin, editableColumns=['#1'])
    view.treeView["columns"] = ("value")
    view.treeView.column("#0", width=75, anchor="w")
    view.treeView.heading("#0", text="Property")
    view.treeView.column("value", width=600, anchor="w")
    view.treeView.heading("value", text="Value")
    view.treeView["displaycolumns"] = ("value")
    view.view()
    return view
    
class ViewProperties(ViewWinTree.ViewTree):
    def __init__(self, modelXbrl, tabWin, editableColumns=[]):
        tabName = "Properties (" + modelXbrl.getInstanceFilenameForView() + ")"
        super(ViewProperties, self).__init__(modelXbrl, tabWin, tabName, True, editableColumns=editableColumns, valueChangedCallback=self.valueChanged)
        self.openProperties = set()
        self.properties = None
        self.modelFact = None
                
    def view(self):
        self.viewProperties(None, "")
        
    def cleanPreviousNodes(self,parentNode):
        for previousNode in self.treeView.get_children(parentNode):
            self.cleanPreviousNodes(previousNode) 
            text = self.treeView.item(previousNode,'text')
            if str(self.treeView.item(previousNode,'open')) in ('true','1'): self.openProperties.add(text)
            else: self.openProperties.discard(text)
            self.treeView.delete(previousNode)        
        
    def viewProperties(self, modelObject, parentNode):
        try:
            self.cleanPreviousNodes(parentNode)
        except Exception:
            pass    # possible tkinter issues
        if modelObject is not None:
            try:
                self.properties = modelObject.propertyView
                self.showProperties(self.properties, parentNode, 1)
            except:
                pass
            
    def showProperties(self, properties, parentNode, identifier):
        for currentTuple in properties:
            if currentTuple:
                lenTuple = len(currentTuple)
                if 2 <= lenTuple <= 4:
                    if lenTuple == 2 and "modelFact" == str(currentTuple[0]):
                        #keep a reference in case we need to change the value
                        self.modelFact = currentTuple[1]
                    else:
                        strId = str(identifier)
                        appearanceTag = "odd" if (identifier & 1)!=0 else "even"
                        if lenTuple==4:
                            if currentTuple[3] == "editable":
                                tagList = (appearanceTag, "editable")
                            else:
                                tagList = (appearanceTag,)
                        else:
                            tagList = (appearanceTag,)
                        node = self.treeView.insert(parentNode, "end", strId, text=currentTuple[0], tags=tagList)
                        self.treeView.set(strId, "value", currentTuple[1])
                        identifier += 1;
                        if lenTuple == 3 or lenTuple == 4:
                            if currentTuple[0] in self.openProperties:
                                self.treeView.item(node,open=True)
                            newProperties = currentTuple[2]
                            if newProperties is not None:
                                identifier = self.showProperties(newProperties, node, identifier)
        return identifier
    
    def viewModelObject(self, modelObject):
        self.viewProperties(modelObject, "")
        
    def refreshTitle(self):
        tid = str(self.viewFrame)
        text = "Properties (" + self.modelXbrl.getInstanceFilenameForView() + ")"
        self.tabWin.tab(tid, text=text)
        self.tabTitle = text
        
    def valueChanged(self, rowID, column, value):
        if self.modelFact is not None:
            newValue = str(value).replace(",","")
            if str(self.modelFact.text) != newValue:
                print("value changed rowID={0} column={1} {2} newValue={2} oldValue={3}".format(str(rowID), str(column), str(value), str(self.modelFact.text)))
                self.modelFact.text = newValue
                #TODO: refactor things in updateInstanceFromFactPrototypes so that
                #      we get access to a proper fact value change, including setting modelXbrl modified etc
                #TODO: Actually no way to save the instance changes with the GUI (would save a facts table)
                print("Refreshing facts view would get stuck")
                #self.modelFact.modelXbrl.guiViews.factTableView.view()
            
