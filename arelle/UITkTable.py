'''
Created on Mar, 30 2015

@author: Acsone S. A.
(c) Copyright 2015 Mark V Systems Limited, All rights reserved.
'''

import numpy

from arelle import TkTableWrapper
from tkinter import *
from _sqlite3 import Row
try:
    from tkinter.ttk import *
    _Combobox = ttk.Combobox
except ImportError:
    from ttk import *
    _Combobox = Combobox

LEFT_JUSTIFIED = 0;
RIGHT_JUSTIFIED = 1;

class Coordinate(object):
    def __init__(self, row, column):
        self.x = int(column)
        self.y = int(row)


    def __str__(self):
        return "%i,%i"%(self.y,self.x)


    def __repr__(self):
        return self.__str__()


class XbrlTable(TkTableWrapper.Table):
    '''
    This class implements all the GUI elements needed for representing
    the sliced 2D-view of an Xbrl Table
    '''


    def valueCommand(self, event):
        if event.i == 0:
            return self.data[event.r, event.c]
        else:
            self.data[event.r, event.c] = event.S
            self.isModified[Coordinate(event.r, event.c)] = True
            return 'set'
    def __init__(self, parentWidget, rows, columns, titleRows, titleColumns,
                 tableName):
        '''
        The initial size of the table (including the header sizes) must be
        supplied at table creation time.
        The contextual menu must also be supplied in order to be effective
        '''
        self.data = numpy.empty((rows, columns), dtype=str)
        self.isModified = dict()
        self.data.fill('')

        super(XbrlTable, self).__init__(parentWidget,
                                        rows=rows,
                                        cols=columns,
                                        state='normal',
                                        titlerows=titleRows,
                                        titlecols=titleColumns,
                                        roworigin=0,
                                        colorigin=0,
                                        selectmode='extended',
                                        selecttype='cell',
                                        rowstretch='last',
                                        colstretch='last',
                                        rowheight=-26,
                                        colwidth=15,
                                        flashmode='off',
                                        anchor='e',
                                        usecommand=1,
                                        background='#fffffffff',
                                        relief='sunken',
                                        command=self.valueCommand,
                                        takefocus=False,
                                        rowseparator='\n')

    def initCellValue(self, value, x, y, backgroundColour,
                     justification):
        '''
        Initialise the content of a cell. The resulting cell will be writable.
        '''


    def initCellCombobox(self, values, x, y):
        '''
        Initialise the content of a cell as a combobox.
        The combobox is read-only, no new value can be added to the combobox.
        '''


    def initReadonlyCell(self, x, y, colspan, rowspan):
        '''
        Make the specified cell read-only
        '''


    def initHeaderCellValue(self, value, x, y, colspan, rowspan, justification):
        '''
        Initialise the read-only content of a header cell.
        '''


    def initHeaderCombobox(self, values, x, y, colspan, rowspan,
                           isOpen):
        '''
        Initialise the read-only content of a header cell as a combobox.
        New values can be added to the combobox if isOpen==True.
        '''


    def initHeaderBorder(self, value, x, y,
                         hasLeftBorder=False, hasTopBorder=False,
                         hasRightBorder=False, hasBottomBorder=False):
        '''
        Set the border around a header cell. The border will always have the
        same size.
        '''
