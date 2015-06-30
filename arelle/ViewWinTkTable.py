'''
Created on Apr 5, 2015

@author: Acsone S. A.
(c) Copyright 2015 Mark V Systems Limited, All rights reserved.
'''

from arelle.UITkTable import ScrolledTkTableFrame
from arelle.ViewWinPane import ViewPane

class ViewTkTable(ViewPane):
    def __init__(self, modelXbrl, tabWin, tabTitle,
                 hasToolTip=False, lang=None, browseCmd=None):
        contentView = ScrolledTkTableFrame(tabWin, browseCmd)
        super(ViewTkTable, self).__init__(modelXbrl, tabWin, tabTitle,
                                       contentView, hasToolTip=hasToolTip,
                                       lang=lang)
        self.table = self.viewFrame.table
        self.setHeightANdWidth()
        self.table.contextMenuClick = self.contextMenuClick

    def contextMenu(self):
        super(ViewTkTable, self).contextMenu()
        self.bindContextMenu(self.table)
        return self.menu
    
    def setHeightANdWidth(self):
        frameWidth = self.tabWin.winfo_width()
        frameHeight = self.tabWin.winfo_height()
        extraspace = 10 # extra vertical space as a nasty patch to avoid sometimes hiding part of last table row
        self.table.config(maxheight=frameHeight-self.viewFrame.horizontalScrollbarHeight-extraspace,
                          maxwidth=frameWidth-self.viewFrame.verticalScrollbarWidth)
