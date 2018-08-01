from PyQt4 import QtGui, QtCore
from raw_ui import reportPeriodePlusLabel_ui
import sys,os
import myDB
import sqlite3
import time



searchDict = {
        "NO. TRANS":"noTrans",
        "TIPE":"tipe",
        "TANGGAL":"tanggal",
        "KODE SALES":"kodeSales",
        "NAMA SALES":"namaSales",
        "KODE CUST":"kodeCust",
        "NAMA CUST":"namaCust",
        "NO PO.":"nopo",
        "PAYMENT":"payment",
        "TOP":"top",
        "KETERANGAN":"keterangan",
        "TOTAL":"total",
        "NODR":"nodr",
        "KODE ITEM":"kodeItem",
        "NAMA ITEM":"namaItem",
        "ISI":"isi",
        "JUMLAH":"jumlah",
        "HARGA":"harga",
        "DISKON":"diskon",
        "DISKON AMOUNT":"diskonAmount",
        "TOTAL":"totalTrans",
    }

h = (
        "NO. TRANS",
        "TIPE",
        "TANGGAL",
        "KODE SALES",
        "NAMA SALES",
        "KODE CUST",       
        "NAMA CUST",       
        "NO PO.",
        "PAYMENT",
        "TOP",
        "KETERANGAN",
        "TOTAL",
        "NODR",
        "KODE ITEM",
        "NAMA ITEM",
        "ISI",
        "JUMLAH",
        "HARGA",
        "DISKON",
        "DISKON AMOUNT",
        "TOTAL" 
    )


class QCustomTableWidgetItem (QtGui.QTableWidgetItem):
    def __init__ (self, value):
        super(QCustomTableWidgetItem, self).__init__(QtCore.QString('%s' % value))

    def __lt__ (self, other):
        if (isinstance(other, QCustomTableWidgetItem)):  
            try:          
                selfDataValue  = float(self.data(QtCore.Qt.EditRole).toString().replace(',',''))
                otherDataValue = float(other.data(QtCore.Qt.EditRole).toString().replace(',',''))
                return selfDataValue < otherDataValue            
            except:
                return QtGui.QTableWidgetItem.__lt__(self, other)
        else:
            return QtGui.QTableWidgetItem.__lt__(self, other)

class Main(QtGui.QMainWindow,reportPeriodePlusLabel_ui.Ui_MainWindow):
    def __init__(self,parent = None,kdpengguna = None,nama = None,status = None):
        self.kdpengguna = kdpengguna
        self.nama = nama
        self.status = status
        QtGui.QMainWindow.__init__(self)
        self.cariSQL=""
        self.judul="Laporan Realisasi Sales Per Periode"
        self.folder_tgl='\\data\\Laporan\\'+time.strftime("%Y")+'\\'+time.strftime("%m")+'\\'+time.strftime("%d")+'\\'
        self.simpan = os.getcwd()+self.folder_tgl+"LaporanRealisasiSalesDetail"
        
        self.koneksiDatabase()
        self.setupUi(self)
        self.actionKeluar.deleteLater()
        self.labelTipe.hide()
        self.comboBox.hide()
        myDB.tampilan()
        self.setWindowTitle(self.judul)
        self.comboBoxSearch.addItems(h)
        self.aksi()
        self.formNormal()

    def formNormal(self):
        self.progressBar.hide()
        some_date = QtCore.QDate.currentDate()
        self.dateEditAwal.setDate(some_date)
        self.dateEditAkhir.setDate(some_date)

        self.comboBox.setCurrentIndex(0)
        self.lineEditCari.clear()
        self.tableWidget.clear()
        
        self.tableWidget.setColumnCount(len(h))
        self.tableWidget.setRowCount(0)
        self.tableWidget.setHorizontalHeaderLabels(h)
        self.statusBar().showMessage("")
        self.lineEditJumCust.setText('0')
        self.lineEditJumQty.setText('0')
        self.lineEditJumHargaSebelum.setText('0')
        self.lineEditJumHargaSetelah.setText('0')
        self.labelLaba.hide()
        self.lineEditLaba.hide()

    def aksi(self):
        self.actionShow_Data.triggered.connect(self.onShowData)
        self.lineEditCari.returnPressed.connect(self.onShowData)
        self.comboBox.currentIndexChanged.connect(self.onShowData)
        
        self.tableWidget.doubleClicked.connect(self.onDblKlik)
        self.pushButtonReset.pressed.connect(self.formNormal)
        self.connect(QtGui.QShortcut(QtGui.QKeySequence("F4"), self), QtCore.SIGNAL(
            'activated()'), self.onShowData)

    def onDblKlik(self,item):
        r=item.row()
        c= item.column()
        self.comboBoxSearch.setCurrentIndex(c)
        kata = str(self.comboBoxSearch.currentText())
        
        try:
            strCari=(str(self.tableWidget.item(r,c).text()).replace(',',''))
            self.lineEditCari.setText(strCari)
            self.cariSQL = " AND "+str(searchDict[kata])+" LIKE UPPER('" + strCari + "')"        
            self.onShow()
        except:
            QtGui.QMessageBox.warning(self,"Perhatian!","Tidak dapat mencari pada kolom %s"%kata)


    def onShowData(self):
        strCari=(str(self.lineEditCari.text()))
        if strCari=="":
            self.cariSQL=""
        else:
            kata = str(self.comboBoxSearch.currentText())
            self.cariSQL = " AND "+str(searchDict[kata])+" LIKE UPPER('%" + strCari + "%')"
        self.onShow()

    def hitung(self):
        a = []
        qty = 0
        sb = 0
        sd = 0

        r = self.tableWidget.rowCount()
        for i in range(r):
            a.append(str(self.tableWidget.item(i,5).text()))
            qty += int(str(self.tableWidget.item(i,16).text().replace(',','')))
            sb += int(str(self.tableWidget.item(i,17).text().replace(',','')))*int(str(self.tableWidget.item(i,16).text().replace(',','')))
            sd += int(str(self.tableWidget.item(i,20).text().replace(',','')))
        self.lineEditJumCust.setText(format(len(set(a)),',.0f'))
        self.lineEditJumQty.setText(format(qty,',.0f'))
        self.lineEditJumHargaSebelum.setText(format(sb,',.0f'))
        self.lineEditJumHargaSetelah.setText(format(sd,',.0f'))

    
    def onShow(self):
        self.tableWidget.setRowCount(0)
        self.tableWidget.setSortingEnabled(False)
        tgl_awal = str(self.dateEditAwal.date().toPyDate())+" 00:00:00"
        tgl_akhir = str(self.dateEditAkhir.date().toPyDate())+" 23:59:59"
        self.sql = """
            SELECT 
                noTrans,
                tipe,
                tanggal,
                kodeSales,
                namaSales,
                kodeCust,
                namaCust,
                nopo,
                payment,
                top,
                keterangan,
                total,
                nodr,
                kodeItem,
                namaItem,
                isi,
                jumlah,
                harga,
                diskon,
                diskonAmount,
                totalTrans
            FROM isi
            WHERE
                ((tanggal >= '%s') AND (tanggal <= '%s')) %s 
            
            """ %(tgl_awal, tgl_akhir,self.cariSQL)
        
        bar, jum = self.eksekusi(self.sql)
        self.tableWidget.setRowCount(jum)
        self.sumTotal=0
        self.progressBar.show()
        for e in range(101):
            a= (jum*e)/100
            b = (jum*(e+1))/100            
            for data in range(a,b):                
                if data < int(jum):                            
                    harga = bar[data][17]
                    nilai = bar[data][20]
                    teks=(
                        bar[data][0],
                        bar[data][1],
                        bar[data][2],
                        bar[data][3],
                        bar[data][4],
                        bar[data][5],
                        bar[data][6],
                        bar[data][7],
                        bar[data][8],
                        bar[data][9],
                        bar[data][10],
                        bar[data][11],
                        bar[data][12],
                        bar[data][13],
                        bar[data][14],
                        bar[data][15],
                        bar[data][16],
                        harga,
                        bar[data][18],
                        bar[data][19],
                        nilai

                    )             
                    
                    # self.sumTotal += float(bar[data][9]) 
                    for i in range(len(teks)):
                        
                        item = QCustomTableWidgetItem((str(teks[i])))
                        item.setFlags(
                            QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                        item.setToolTip(str(teks[i]))
                        item.setText(str(teks[i]))
                        self.tableWidget.setItem(data,i,item)
                    self.progressBar.setFormat("membaca... %p% "+str(data)+" baris")
                    self.progressBar.setValue(e)
        self.warnaTabel()
        self.tableWidget.setSortingEnabled(True)
        self.tableWidget.sortByColumn(0,0)
        self.hitung()
        self.progressBar.hide()
        # self.statusBar().setStyleSheet("color:lightblue;background-color: rgb(0, 0, 0);font:bold 12pt Verdana")
        # self.statusBar().showMessage("Total : %s"%(format(self.sumTotal,',.2f')))

    def warnaTabel(self):
        r = self.tableWidget.rowCount()
        for i in range(r):
            self.tableWidget.item(i, 9).setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.tableWidget.item(i, 11).setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.tableWidget.item(i, 15).setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.tableWidget.item(i, 16).setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.tableWidget.item(i, 17).setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.tableWidget.item(i, 18).setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.tableWidget.item(i, 19).setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.tableWidget.item(i, 20).setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.tableWidget.resizeColumnsToContents()
        
    def koneksiDatabase(self):
        self.db = sqlite3.connect("database.db")
        self.cur = self.db.cursor()

    def eksekusi(self,sql):
        self.cur.execute(sql)
        self.db.commit()
        lineData = self.cur.fetchall()
        totData = len(lineData)
        return lineData, totData

    def onClose(self):
        self.db.close()
        self.close()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    form = Main()
    form.show()
    sys.exit(app.exec_())