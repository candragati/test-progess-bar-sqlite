from PyQt4 import QtCore, QtGui
from colorama import *



init(autoreset=True)

def tampilan():    
    file = QtCore.QFile('style.css')
    file.open(QtCore.QFile.ReadOnly)
    styleSheet = file.readAll()
    try:
        # Python v2.
        styleSheet = unicode(styleSheet, encoding='utf8')
    except NameError:
        # Python v3.
        styleSheet = str(styleSheet, encoding='utf8')
    QtGui.qApp.setStyleSheet(styleSheet)        

def bg_kuning():
    return "QLineEdit{background-color: rgb(255, 255, 142);}QLineEdit:focus{background-color: rgb(70, 255, 85);} QLineEdit:disabled{background-color: rgb(201, 201, 201);}"

def brushabu():
    brush = QtGui.QBrush(QtGui.QColor(100, 100, 100, 50))
    brush.setStyle(QtCore.Qt.SolidPattern)
    return brush

def brushkuning():
    brush = QtGui.QBrush(QtGui.QColor(255, 255, 127, 255))
    brush.setStyle(QtCore.Qt.SolidPattern)
    return brush    

def brushijo():
    brush = QtGui.QBrush(QtGui.QColor(70, 255, 185,150))
    brush.setStyle(QtCore.Qt.SolidPattern)
    return brush    

def brushmerah():
    brush = QtGui.QBrush(QtGui.QColor(255, 14, 14,150))
    brush.setStyle(QtCore.Qt.SolidPattern)
    return brush    

