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
    
class ViewProperties(ViewWinTree.ViewTree):
    def __init__(self, modelXbrl, tabWin, editableColumns=[]):
        super(ViewProperties, self).__init__(modelXbrl, tabWin, "Properties", True, editableColumns=editableColumns)
        self.openProperties = set()
                
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
        if modelObject is not None and hasattr(modelObject, "propertyView"):
            self.showProperties(modelObject.propertyView, parentNode, 1)
            
    def showProperties(self, properties, parentNode, identifier):
        for currentTuple in properties:
            if currentTuple:
                lenTuple = len(currentTuple)
                if 2 <= lenTuple <= 4:
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
