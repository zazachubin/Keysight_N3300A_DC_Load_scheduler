from PyQt5.QtWidgets import (QMainWindow, QApplication,
                             QWidget, QFileDialog, QMessageBox,
                             QAction, QVBoxLayout, QHBoxLayout,
                             QGroupBox, QCheckBox, QDialog, QPushButton)
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtCore import Qt, QDir
from datetime import datetime
from datetime import timezone
import pyqtgraph as pg
import numpy
import arrow
import pytz
import csv

# ~~~~~~~~~~~~~~~~~~~~~ File Converter Dialog ~~~~~~~~~~~~~~~~~~~~~~~~~
class FileConverterDialog(QDialog):
# ++++++++++++++++++++++++++++ __init__ +++++++++++++++++++++++++++++++
    def __init__(self, parent = None):
        QDialog.__init__(self, parent)
        self.setStyleSheet("""QGroupBox:title {subcontrol-position: top left;}""")
        self.applayState = False

        self.pathContainer = {'ICS_Power_supply_log_path' : '',
                              'DC_Load_log_path'          : '',
                              'Env_Temperature_log_path'  : '',
                              'Env_Humidity_log_path'     : '',
                              'Env_Pressure_log_path'     : '',
                              'SaveAsPath'                : '',
                              'OneFilePath'               : ''}

        VLbox = QVBoxLayout()

        self.setWindowTitle('Files Selector')
        self.setWindowIcon(QIcon('img/open.svg'))

        OneFilePathSelector = QPushButton(QIcon('img/open.svg'),"Select file")
        OneFilePathSelector.clicked.connect(lambda : self.__selectFilePath(pathKey = 'OneFilePath', fileFormats = "CSV Files(*.csv)"))

        Onefile = QGroupBox('One file')
        Onefile.setCheckable(True)
        Onefile.setChecked(False)
        Onefile_Vlayout = QVBoxLayout()
        Onefile_Vlayout.addWidget(OneFilePathSelector)
        Onefile.setLayout(Onefile_Vlayout)

        ICS_Power_supply_log = QPushButton(QIcon('img/open.svg'),"ICS Power supply log")
        DC_Load_log = QPushButton(QIcon('img/open.svg'),"DC Load log")
        Env_Temperature_log = QPushButton(QIcon('img/open.svg'),"Environment Temperature log")
        Env_Humidity_log = QPushButton(QIcon('img/open.svg'),"Environment Humidity log")
        Env_Pressure_log = QPushButton(QIcon('img/open.svg'),"Environment Pressure log")

        ICS_Power_supply_log.clicked.connect(lambda : self.__selectFilePath(pathKey = 'ICS_Power_supply_log_path', fileFormats = "CSV Files(*.csv)"))
        DC_Load_log.clicked.connect(lambda : self.__selectFilePath(pathKey = 'DC_Load_log_path', fileFormats = "Text files(*.txt)"))
        Env_Temperature_log.clicked.connect(lambda : self.__selectFilePath(pathKey = 'Env_Temperature_log_path', fileFormats = "CSV Files(*.csv)"))
        Env_Humidity_log.clicked.connect(lambda : self.__selectFilePath(pathKey = 'Env_Humidity_log_path', fileFormats = "CSV Files(*.csv)"))
        Env_Pressure_log.clicked.connect(lambda : self.__selectFilePath(pathKey = 'Env_Pressure_log_path', fileFormats = "CSV Files(*.csv)"))

        fileSelectors_Vlayout = QVBoxLayout()
        fileSelectors_Vlayout.addWidget(ICS_Power_supply_log)
        fileSelectors_Vlayout.addWidget(DC_Load_log)
        fileSelectors_Vlayout.addWidget(Env_Temperature_log)
        fileSelectors_Vlayout.addWidget(Env_Humidity_log)
        fileSelectors_Vlayout.addWidget(Env_Pressure_log)

        OneFileConvertPathSelector = QPushButton(QIcon('img/open.svg'),"Select path for generate file")
        OneFileConvertPathSelector.clicked.connect(self.__saveAs)

        OnefileConvert = QGroupBox("One file convert")
        OnefileConvert.setCheckable(True)
        OnefileConvert.setChecked(False)
        OnefileConvert_Vlayout = QVBoxLayout()
        OnefileConvert_Vlayout.addWidget(OneFileConvertPathSelector)
        OnefileConvert.setLayout(OnefileConvert_Vlayout)

        filesSelector = QGroupBox("Separated files")
        filesSelector.setCheckable(True)
        filesSelector.setChecked(False)
        fileSelectors_Vlayout.addWidget(OnefileConvert)
        filesSelector.setLayout(fileSelectors_Vlayout)

        Apply = QPushButton("Apply")
        Cancel = QPushButton("Cancel")

        Apply.clicked.connect(self.__apply)
        Cancel.clicked.connect(self.__cancel)

        apply_cancel_Hlayout = QHBoxLayout()
        apply_cancel_Hlayout.addWidget(Apply)
        apply_cancel_Hlayout.addWidget(Cancel)

        VLbox.addWidget(Onefile)
        VLbox.addWidget(filesSelector)
        VLbox.addLayout(apply_cancel_Hlayout)

        self.setLayout(VLbox)
# ++++++++++++++++++++++++++ get Settings +++++++++++++++++++++++++++++
    def getApplyStatus(self):
        return self.pathContainer, self.applayState
# ++++++++++++++++++++++++ Select file path +++++++++++++++++++++++++++
    def __selectFilePath(self, pathKey, fileFormats):
        OpenfilePath, _ = QFileDialog.getOpenFileName(self, 'Open File', QDir.currentPath(), fileFormats)
        if OpenfilePath != '':
            self.pathContainer[pathKey] = OpenfilePath
# ++++++++++++++++++++++++++++ Save as ++++++++++++++++++++++++++++++++
    def __saveAs(self):
        saveAspath, _ = QFileDialog.getSaveFileName(self, 'Save as', QDir.currentPath(), "CSV Files(*.csv)")
        if saveAspath != '':
            self.pathContainer['SaveAsPath'] = saveAspath
# +++++++++++++++++++++++++++++ Apply +++++++++++++++++++++++++++++++++
    def __apply(self):
        self.applayState = True
        self.close()
# +++++++++++++++++++++++++++++ Cancel ++++++++++++++++++++++++++++++++
    def __cancel(self):
        self.applayState = False
        self.close()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~ TimeAxisItem ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class TimeAxisItem(pg.AxisItem):
# ++++++++++++++++++++++++++++ __init__ +++++++++++++++++++++++++++++++
    """Internal timestamp for x-axis"""
    def __init__(self, *args, **kwargs):
        super(TimeAxisItem, self).__init__(*args, **kwargs)
# +++++++++++++++++++++++++++ tickStrings +++++++++++++++++++++++++++++
    def tickStrings(self, values, scale, spacing):
        """Function overloading the weak default version to provide timestamp"""
        return [datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S') for value in values]
# ~~~~~~~~~~~~~~~~~~~~~~~~~~ Custom Graph ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Graph(QWidget):
# ++++++++++++++++++++++++++++ __init__ +++++++++++++++++++++++++++++++
    def __init__(self, ch1_label, ch2_label, ch3_label, ch4_label, ch5_label, ch6_label, ch7_label, parent=None):
        super(Graph, self).__init__(parent)
        self.ch1_label = ch1_label
        self.ch2_label = ch2_label
        self.ch3_label = ch3_label
        self.ch4_label = ch4_label
        self.ch5_label = ch5_label
        self.ch6_label = ch6_label
        self.ch7_label = ch7_label

        self.ch_1_data = [[],[]]
        self.ch_2_data = [[],[]]
        self.ch_3_data = [[],[]]
        self.ch_4_data = [[],[]]
        self.ch_5_data = [[],[]]
        self.ch_6_data = [[],[]]
        self.ch_7_data = [[],[]]

        self._InitialTime = [datetime.strptime(str(datetime.fromtimestamp(datetime.utcnow().timestamp())),'%Y-%m-%d %H:%M:%S.%f').timestamp()]

        self.initUI()
# +++++++++++++++++++++++++++++ initUI ++++++++++++++++++++++++++++++++
    def initUI(self):
############################### layout ################################
        windowHLayout = QHBoxLayout()
############################ Create plots #############################
        ######################## Axis #################################
        self.a2 = pg.AxisItem("left")
        self.a3 = pg.AxisItem("left")
        self.a4 = pg.AxisItem("left")
        self.a5 = pg.AxisItem("left")
        self.a6 = pg.AxisItem("left")
        self.a7 = pg.AxisItem("left")
        ################### Graphics view #############################
        plotView = pg.GraphicsView()
        # background white color
        #plotView.setBackground('w')
        ###################### Layout #################################
        self.layout = pg.GraphicsLayout()
        plotView.setCentralWidget(self.layout)
        ################ Add axis to self.layout ###########################
        self.layout.addItem(self.a2, row = 2, col = 6,  rowspan=1, colspan=1)
        self.layout.addItem(self.a3, row = 2, col = 5,  rowspan=1, colspan=1)
        self.layout.addItem(self.a4, row = 2, col = 4,  rowspan=1, colspan=1)
        self.layout.addItem(self.a5, row = 2, col = 3,  rowspan=1, colspan=1)
        self.layout.addItem(self.a6, row = 2, col = 2,  rowspan=1, colspan=1)
        self.layout.addItem(self.a7, row = 2, col = 1,  rowspan=1, colspan=1)
        ############### Plotitem and viewbox ##########################
        self.pI = pg.PlotItem(axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        ############## add plotitem to self.layout #########################
        self.layout.addItem(self.pI, row = 2, col = 7,  rowspan=1, colspan=1)
        #################### Set Grid #################################
        self.pI.showGrid(x=True, y=True)
        ##################### ViewBoxes ###############################
        self.v1 = self.pI.vb
        self.v2 = pg.ViewBox()
        self.v3 = pg.ViewBox()
        self.v4 = pg.ViewBox()
        self.v5 = pg.ViewBox()
        self.v6 = pg.ViewBox()
        self.v7 = pg.ViewBox()
        ############# Add viewboxes to self.layout #########################
        self.layout.scene().addItem(self.v2)
        self.layout.scene().addItem(self.v3)
        self.layout.scene().addItem(self.v4)
        self.layout.scene().addItem(self.v5)
        self.layout.scene().addItem(self.v6)
        self.layout.scene().addItem(self.v7)
        ############ Link axis with viewboxes #########################
        self.a2.linkToView(self.v2)
        self.a3.linkToView(self.v3)
        self.a4.linkToView(self.v4)
        self.a5.linkToView(self.v5)
        self.a6.linkToView(self.v6)
        self.a7.linkToView(self.v7)
        ################ Link viewboxes ###############################
        self.v2.setXLink(self.v1)
        self.v3.setXLink(self.v2)
        self.v4.setXLink(self.v3)
        self.v5.setXLink(self.v4)
        self.v6.setXLink(self.v5)
        self.v7.setXLink(self.v6)
        ################# Plot menu off ###############################
        self.v1.setMenuEnabled(False)
        self.v2.setMenuEnabled(False)
        self.v3.setMenuEnabled(False)
        self.v4.setMenuEnabled(False)
        self.v5.setMenuEnabled(False)
        self.v6.setMenuEnabled(False)
        self.v7.setMenuEnabled(False)
        ################## Axes labels ################################
        self.pI.getAxis("left").setLabel(self.ch1_label, color='#FE2E64')
        self.a2.setLabel(self.ch2_label, color='#FFFF00')
        self.a3.setLabel(self.ch3_label, color='#2EFEF7')
        self.a4.setLabel(self.ch4_label, color='#2E2EFE')
        self.a5.setLabel(self.ch5_label, color='#2EFE2E')
        self.a6.setLabel(self.ch6_label, color='#FFFFFF')
        self.a7.setLabel(self.ch7_label, color='#FF56FF')
        ############# Updates when resized ############################
        self.v1.sigResized.connect(self.updateViews)
        ###### Autorange once to fit views at start ###################
        self.v2.enableAutoRange(axis= pg.ViewBox.XYAxes, enable=True)
        self.v3.enableAutoRange(axis= pg.ViewBox.XYAxes, enable=True)
        self.v4.enableAutoRange(axis= pg.ViewBox.XYAxes, enable=True)
        self.v5.enableAutoRange(axis= pg.ViewBox.XYAxes, enable=True)
        self.v6.enableAutoRange(axis= pg.ViewBox.XYAxes, enable=True)
        self.v7.enableAutoRange(axis= pg.ViewBox.XYAxes, enable=True)
        ############# plot initialization #############################
        self.v1.addItem(pg.PlotCurveItem(self._InitialTime, [0], pen='#FE2E64'))
        ################ Update Views #################################
        self.updateViews()
        ################# Checkboxes ##################################
        self.ch_1_CheckBox = QCheckBox(self.ch1_label)
        self.ch_2_CheckBox = QCheckBox(self.ch2_label)
        self.ch_3_CheckBox = QCheckBox(self.ch3_label)
        self.ch_4_CheckBox = QCheckBox(self.ch4_label)
        self.ch_5_CheckBox = QCheckBox(self.ch5_label)
        self.ch_6_CheckBox = QCheckBox(self.ch6_label)
        self.ch_7_CheckBox = QCheckBox(self.ch7_label)
        ############## Checkboxes status ##############################
        self.ch_1_CheckBox.setChecked(True)
        self.ch_2_CheckBox.setChecked(True)
        self.ch_3_CheckBox.setChecked(True)
        self.ch_4_CheckBox.setChecked(True)
        self.ch_5_CheckBox.setChecked(True)
        self.ch_6_CheckBox.setChecked(True)
        self.ch_7_CheckBox.setChecked(True)
        ############# Checkboxes signals ##############################
        self.ch_1_CheckBox.toggled.connect(self.ch1_On_Off)
        self.ch_2_CheckBox.toggled.connect(self.ch2_On_Off)
        self.ch_3_CheckBox.toggled.connect(self.ch3_On_Off)
        self.ch_4_CheckBox.toggled.connect(self.ch4_On_Off)
        self.ch_5_CheckBox.toggled.connect(self.ch5_On_Off)
        self.ch_6_CheckBox.toggled.connect(self.ch6_On_Off)
        self.ch_7_CheckBox.toggled.connect(self.ch7_On_Off)
        ########## Set checkBoxes on self.layout ###########################
        vLayout_CheckBox = QVBoxLayout()
        vLayout_CheckBox.addWidget(self.ch_1_CheckBox)
        vLayout_CheckBox.addWidget(self.ch_2_CheckBox)
        vLayout_CheckBox.addWidget(self.ch_3_CheckBox)
        vLayout_CheckBox.addWidget(self.ch_4_CheckBox)
        vLayout_CheckBox.addWidget(self.ch_5_CheckBox)
        vLayout_CheckBox.addWidget(self.ch_6_CheckBox)
        vLayout_CheckBox.addWidget(self.ch_7_CheckBox)
        ############# Channels GroupBox ###############################
        channelsGroupBox = QGroupBox('Parameters')
        channelsGroupBox.setLayout(vLayout_CheckBox)
        ########### Set Layout on window ##############################
        windowHLayout.setSpacing(0)
        windowHLayout.addWidget(plotView)
        windowHLayout.addWidget(channelsGroupBox)

        self.setLayout(windowHLayout)
# +++++++++++++++++++++++++++ updateViews +++++++++++++++++++++++++++++
    def updateViews(self):
        self.v2.setGeometry(self.v1.sceneBoundingRect())
        self.v3.setGeometry(self.v1.sceneBoundingRect())
        self.v4.setGeometry(self.v1.sceneBoundingRect())
        self.v5.setGeometry(self.v1.sceneBoundingRect())
        self.v6.setGeometry(self.v1.sceneBoundingRect())
        self.v7.setGeometry(self.v1.sceneBoundingRect())
# +++++++++++++++++++++++++++ ch1 On_Off ++++++++++++++++++++++++++++++
    def ch1_On_Off(self):
        if self.ch_1_CheckBox.isChecked() == False:
            self.v1.clear()
        if self.ch_1_CheckBox.isChecked() == True:
            self.v1.addItem(pg.PlotCurveItem(self.ch_1_data[0], self.ch_1_data[1], pen='#FE2E64'))
# +++++++++++++++++++++++++++ ch2 On_Off ++++++++++++++++++++++++++++++
    def ch2_On_Off(self):
        if self.ch_2_CheckBox.isChecked() == False:
            self.v2.clear()
            self.layout.removeItem(self.a2)
        if self.ch_2_CheckBox.isChecked() == True:
            self.layout.addItem(self.a2, row = 2, col = 6,  rowspan=1, colspan=1)
            self.v2.addItem(pg.PlotCurveItem(self.ch_2_data[0], self.ch_2_data[1], pen='#FFFF00'))
# +++++++++++++++++++++++++++ ch3 On_Off ++++++++++++++++++++++++++++++
    def ch3_On_Off(self):
        if self.ch_3_CheckBox.isChecked() == False:
            self.v3.clear()
            self.layout.removeItem(self.a3)
        if self.ch_3_CheckBox.isChecked() == True:
            self.layout.addItem(self.a3, row = 2, col = 5,  rowspan=1, colspan=1)
            self.v3.addItem(pg.PlotCurveItem(self.ch_3_data[0], self.ch_3_data[1], pen='#2EFEF7'))
# +++++++++++++++++++++++++++ ch4 On_Off ++++++++++++++++++++++++++++++
    def ch4_On_Off(self):
        if self.ch_4_CheckBox.isChecked() == False:
            self.v4.clear()
            self.layout.removeItem(self.a4)
        if self.ch_4_CheckBox.isChecked() == True:
            self.layout.addItem(self.a4, row = 2, col = 4,  rowspan=1, colspan=1)
            self.v4.addItem(pg.PlotCurveItem(self.ch_4_data[0], self.ch_4_data[1], pen='#2E2EFE'))
# +++++++++++++++++++++++++++ ch5 On_Off ++++++++++++++++++++++++++++++
    def ch5_On_Off(self):
        if self.ch_5_CheckBox.isChecked() == False:
            self.v5.clear()
            self.layout.removeItem(self.a5)
        if self.ch_5_CheckBox.isChecked() == True:
            self.layout.addItem(self.a5, row = 2, col = 3,  rowspan=1, colspan=1)
            self.v5.addItem(pg.PlotCurveItem(self.ch_5_data[0], self.ch_5_data[1], pen='#2EFE2E'))
# +++++++++++++++++++++++++++ ch6 On_Off ++++++++++++++++++++++++++++++
    def ch6_On_Off(self):
        if self.ch_6_CheckBox.isChecked() == False:
            self.v6.clear()
            self.layout.removeItem(self.a6)
        if self.ch_6_CheckBox.isChecked() == True:
            self.layout.addItem(self.a6, row = 2, col = 2,  rowspan=1, colspan=1)
            self.v6.addItem(pg.PlotCurveItem(self.ch_6_data[0], self.ch_6_data[1], pen='#FFFFFF'))
# +++++++++++++++++++++++++++ ch7 On_Off ++++++++++++++++++++++++++++++
    def ch7_On_Off(self):
        if self.ch_7_CheckBox.isChecked() == False:
            self.v7.clear()
            self.layout.removeItem(self.a7)
        if self.ch_7_CheckBox.isChecked() == True:
            self.layout.addItem(self.a7, row = 2, col = 1,  rowspan=1, colspan=1)
            self.v7.addItem(pg.PlotCurveItem(self.ch_7_data[0], self.ch_7_data[1], pen='#FFFFFF'))
# +++++++++++++++++++++++++++ updatePlot ++++++++++++++++++++++++++++++
    def updatePlot(self, ch_1_data, ch_2_data, ch_3_data, ch_4_data, ch_5_data, ch_6_data, ch_7_data):
        ################### Clear all plots ###########################
        self.v1.clear()
        self.v2.clear()
        self.v3.clear()
        self.v4.clear()
        self.v5.clear()
        self.v6.clear()
        self.v7.clear()

        self.ch_1_data = ch_1_data
        self.ch_2_data = ch_2_data
        self.ch_3_data = ch_3_data
        self.ch_4_data = ch_4_data
        self.ch_5_data = ch_5_data
        self.ch_6_data = ch_6_data
        self.ch_7_data = ch_7_data

        self.v1.addItem(pg.PlotCurveItem(self.ch_1_data[0], self.ch_1_data[1], pen='#FE2E64'))
        self.v2.addItem(pg.PlotCurveItem(self.ch_2_data[0], self.ch_2_data[1], pen='#FFFF00'))
        self.v3.addItem(pg.PlotCurveItem(self.ch_3_data[0], self.ch_3_data[1], pen='#2EFEF7'))
        self.v4.addItem(pg.PlotCurveItem(self.ch_4_data[0], self.ch_4_data[1], pen='#2E2EFE'))
        self.v5.addItem(pg.PlotCurveItem(self.ch_5_data[0], self.ch_5_data[1], pen='#2EFE2E'))
        self.v6.addItem(pg.PlotCurveItem(self.ch_6_data[0], self.ch_6_data[1], pen='#FFFFFF'))
        self.v7.addItem(pg.PlotCurveItem(self.ch_7_data[0], self.ch_7_data[1], pen='#FF56FF'))

        self.v1.enableAutoRange(axis= pg.ViewBox.XYAxes, enable=True)
        self.v2.enableAutoRange(axis= pg.ViewBox.XYAxes, enable=True)
        self.v3.enableAutoRange(axis= pg.ViewBox.XYAxes, enable=True)
        self.v4.enableAutoRange(axis= pg.ViewBox.XYAxes, enable=True)
        self.v5.enableAutoRange(axis= pg.ViewBox.XYAxes, enable=True)
        self.v6.enableAutoRange(axis= pg.ViewBox.XYAxes, enable=True)
        self.v7.enableAutoRange(axis= pg.ViewBox.XYAxes, enable=True)

#//////////////////////////////////////////////////////////////////////
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ App ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class App(QMainWindow):
# +++++++++++++++++++++++++++++__init__ +++++++++++++++++++++++++++++++
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('img/programIcon.svg'))
        self.setWindowTitle('DataPlotter')
        self.setGeometry(0, 0, 1600, 800)

        self._filePath = ''

        self.ch_1_data = [[], []]
        self.ch_2_data = [[], []]
        self.ch_3_data = [[], []]
        self.ch_4_data = [[], []]
        self.ch_5_data = [[], []]
        self.ch_6_data = [[], []]
        self.ch_7_data = [[], []]

        self.initUI()
# +++++++++++++++++++++++++++++ initUI ++++++++++++++++++++++++++++++++
    def initUI(self):
        self.setStyleSheet("""QGroupBox:title {subcontrol-position: top center;}""")
######################## Set window to center #########################
        self.center()
########################## Control Buttons ############################
        ######################## Exit #################################
        exitButton = QAction(QIcon('img/close.svg'), 'Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.triggered.connect(self.close)
        ######################## open #################################
        openAct = QAction(QIcon('img/open.svg'),'Open files', self)
        openAct.setShortcut("Ctrl+O")
        openAct.triggered.connect(self.openFile)
        ####################### About #################################
        aboutAct = QAction(QIcon('img/info.svg'), 'About', self)
        aboutAct.triggered.connect(self.aboutDialog)
####################### Add buttons on toolbar ########################
        toolbar = self.addToolBar('Tools')
        toolbar.addAction(exitButton)
        toolbar.addSeparator()
        toolbar.addAction(openAct)
        toolbar.addSeparator()
        toolbar.addAction(aboutAct)
############################### Graph #################################
        self.plot = Graph(  ch1_label='Temperature [*C]',
                            ch2_label='Temperature min-max diff [*C]',
                            ch3_label='Voltage [V]',
                            ch4_label='Current [A]',
                            ch5_label='Env_Temperature [*C]',
                            ch6_label='Env_Humidity [%]',
                            ch7_label='Env_Pressure [hPa]')

        self.setCentralWidget(self.plot)
############################## Show GUI ###############################
        self.show()
#//////////////////////////////////////////////////////////////////////
# +++++++++++++++++++++++++++++ Center ++++++++++++++++++++++++++++++++
    def center(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())
# +++++++++++++++ Zurich time stamp to UTC converter ++++++++++++++++++
    def Zurich_to_UTC(self, Zurich_timestamp):
        timestamp_Ru = datetime.strptime(Zurich_timestamp, '%Y/%m/%d %H:%M:%S.%f')
        timezone = pytz.timezone('Europe/Zurich')
        dt = arrow.get(timezone.localize(timestamp_Ru)).to('UTC')

        if '.' in str(dt.time()):
            convertedStamp = str(dt.date()) + ' ' + str(dt.time())
        else:
            convertedStamp = str(dt.date()) + ' ' + str(dt.time()) +'.000'

        return convertedStamp
# +++++++++++++++++++++++ Open one file log +++++++++++++++++++++++++++
    def openOneFileLog(self, FilePath):
        Time_T   = []
        Time_V   = []
        Time_I   = []

        Time_E_T = []
        Time_E_H = []
        Time_E_P = []

        T = []
        V = []
        I = []

        E_T = []
        E_H = []
        E_P = []

        counter = 1
        try:
            with open(FilePath) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                for row in csv_reader:
                    if counter > 1:
                        try:
                            T.append(float(row[1]))                    
                            Time_T.append(datetime.strptime(row[0],'%Y/%m/%d %H:%M:%S.%f').timestamp())
                        except ValueError:
                            pass
                        try:
                            V.append(float(row[2]))
                            Time_V.append(datetime.strptime(row[0],'%Y/%m/%d %H:%M:%S.%f').timestamp())
                        except ValueError:
                            pass
                        try:
                            I.append(float(row[3]))
                            Time_I.append(datetime.strptime(row[0],'%Y/%m/%d %H:%M:%S.%f').timestamp())
                        except ValueError:
                            pass
                        try:
                            E_T.append(float(row[4]))
                            Time_E_T.append(datetime.strptime(row[0],'%Y/%m/%d %H:%M:%S.%f').timestamp())
                        except ValueError:
                            pass
                        try:
                            E_H.append(float(row[5]))
                            Time_E_H.append(datetime.strptime(row[0],'%Y/%m/%d %H:%M:%S.%f').timestamp())
                        except ValueError:
                            pass
                        try:
                            E_P.append(float(row[6]))
                            Time_E_P.append(datetime.strptime(row[0],'%Y/%m/%d %H:%M:%S.%f').timestamp())
                        except ValueError:
                            pass
                    counter+=1
        except IndexError:
            print("Bad One lile log ile format!")

        OneFileDataOut = {  'Time_T': Time_T,
                            'Time_V': Time_V,
                            'Time_I': Time_I,
                            'Time_E_T': Time_E_T,
                            'Time_E_H': Time_E_H,
                            'Time_E_P': Time_E_P,

                            'T'     : T,
                            'V'     : V,
                            'I'     : I,

                            'E_T'     : E_T,
                            'E_H'     : E_H,
                            'E_P'     : E_P
                            }

        return OneFileDataOut
# +++++++++++++++++++++ Open power supply log +++++++++++++++++++++++++
    def openPowerSupplyLog(self, FilePath):
        Time_V = []
        Time_I = []
        Time_T = []

        V = []
        I = []
        T = []

        counter = 1
        try:
            with open(FilePath) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                for row in csv_reader:
                    if counter >= 3:
                        try:
                            if float(row[1]) != 0:
                                V.append(float(row[1]))
                                Time_V.append(datetime.strptime(self.Zurich_to_UTC(row[0]),'%Y-%m-%d %H:%M:%S.%f').timestamp())
                        except ValueError:
                            pass
                        try:
                            I.append(float(row[2]))
                            Time_I.append(datetime.strptime(self.Zurich_to_UTC(row[0]),'%Y-%m-%d %H:%M:%S.%f').timestamp())
                        except ValueError:
                            pass
                        try:
                            if float(row[4])/1000 < 100 and float(row[4])/1000 > 0:
                                T.append(float(row[4])/1000)                    
                                Time_T.append(datetime.strptime(self.Zurich_to_UTC(row[0]),'%Y-%m-%d %H:%M:%S.%f').timestamp())
                        except ValueError:
                            pass
                    counter+=1
        except IndexError:
            print("Bad ICS_Power_supply_log file format!")

        PowerSupplyDataOut = {  'Time_V': Time_V,
                                'Time_I': Time_I,
                                'Time_T': Time_T,
                                'V'     : V,
                                'I'     : I,
                                'T'     : T
                                }

        return PowerSupplyDataOut
# +++++++++++++++++++++++ Open DC_Load log ++++++++++++++++++++++++++++
    def openDC_LoadLog(self, FilePath):
        Time_V = []
        Time_I = []

        V = []
        I = []

        counter = 1
        try:
            with open(FilePath) as txt_file:
                txt_reader = csv.reader(txt_file, delimiter=',')
                for row in txt_reader:
                    if counter >= 2:
                        try:
                            V.append(float(row[1]))
                            Time_V.append(datetime.strptime(row[0],'%Y-%m-%d %H:%M:%S.%f').timestamp())
                        except ValueError:
                            pass
                        try:
                            I.append(float(row[2]))
                            Time_I.append(datetime.strptime(row[0],'%Y-%m-%d %H:%M:%S.%f').timestamp())
                        except ValueError:
                            pass
                    counter+=1
        except IndexError:
            print("Bad DC_Load_log file format!")

        DC_LoaderDataOut = {'Time_V': Time_V,
                            'Time_I': Time_I,
                            'V'     : V,
                            'I'     : I,
                            }

        return DC_LoaderDataOut
# +++++++++++++++++++++ Open Temperature Log ++++++++++++++++++++++++++
    def openTemperatureLog(self, FilePath):
        Time_E_T = []
        E_T = []

        counter = 1
        try:
            with open(FilePath) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                for row in csv_reader:
                    if counter >= 2:
                        try:
                            E_T.append(float(row[1]))
                            Time_E_T.append(datetime.strptime(self.Zurich_to_UTC(row[0]),'%Y-%m-%d %H:%M:%S.%f').timestamp())
                        except ValueError:
                            pass
                    counter+=1
        except IndexError:
            print("Bad Env_Temperature_log file format!")

        TemperatureDataOut = {  'Time_E_T': Time_E_T,
                                'E_T'     : E_T
                                }

        return TemperatureDataOut
# +++++++++++++++++++++++ Open Humidity Log +++++++++++++++++++++++++++
    def openHumidityLog(self, FilePath):
        Time_E_H = []
        E_H = []

        counter = 1
        try:
            with open(FilePath) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                for row in csv_reader:
                    if counter >= 2:
                        try:
                            if float(row[1]) < 100 and float(row[1]) > 0:
                                E_H.append(float(row[1]))
                                Time_E_H.append(datetime.strptime(self.Zurich_to_UTC(row[0]),'%Y-%m-%d %H:%M:%S.%f').timestamp())
                        except ValueError:
                            pass
                    counter+=1
        except IndexError:
            print("Bad Env_Humidity_log file format!")

        HumidityDataOut = { 'Time_E_H': Time_E_H,
                            'E_H'     : E_H
                            }

        return HumidityDataOut
# +++++++++++++++++++++++ Open Pressure Log +++++++++++++++++++++++++++
    def openPressureLog(self, FilePath):
        Time_E_P = []
        E_P = []

        counter = 1
        try:
            with open(FilePath) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                for row in csv_reader:
                    if counter >= 2:
                        try:
                            E_P.append(float(row[1]))
                            Time_E_P.append(datetime.strptime(self.Zurich_to_UTC(row[0]),'%Y-%m-%d %H:%M:%S.%f').timestamp())
                        except ValueError:
                            pass
                    counter+=1
        except IndexError:
            print("Bad Env_Pressure_log file format!")

        PressureDataOut = { 'Time_E_P': Time_E_P,
                            'E_P'     : E_P
                            }

        return PressureDataOut
# ++++++++++++++++++++++++++++ openFile +++++++++++++++++++++++++++++++
    def openFile(self):
        ConverterDialog = FileConverterDialog()
        ConverterDialog.exec_()
        pathContainer, acceptState = ConverterDialog.getApplyStatus()
        if acceptState == True:
            self.ch_1_data = [[], []]
            self.ch_2_data = [[], []]
            self.ch_3_data = [[], []]
            self.ch_4_data = [[], []]
            self.ch_5_data = [[], []]
            self.ch_6_data = [[], []]
            self.ch_7_data = [[], []]

            if pathContainer['OneFilePath'] != '':
                self.oneFileDataOut = self.openOneFileLog(pathContainer['OneFilePath'])
                self.ch_1_data = [self.oneFileDataOut['Time_T'], self.oneFileDataOut['T']]
                self.temperatureMinMaxDiff()
                self.ch_3_data = [self.oneFileDataOut['Time_V'], self.oneFileDataOut['V']]
                self.ch_4_data = [self.oneFileDataOut['Time_I'], self.oneFileDataOut['I']]
                self.ch_5_data = [self.oneFileDataOut['Time_E_T'], self.oneFileDataOut['E_T']]
                self.ch_6_data = [self.oneFileDataOut['Time_E_H'], self.oneFileDataOut['E_H']]
                self.ch_7_data = [self.oneFileDataOut['Time_E_P'], self.oneFileDataOut['E_P']]

            else:
                if pathContainer['ICS_Power_supply_log_path'] != '':
                    self.PSdataOut = self.openPowerSupplyLog(pathContainer['ICS_Power_supply_log_path'])
                    self.ch_1_data = [self.PSdataOut['Time_T'], self.PSdataOut['T']]
                    self.temperatureMinMaxDiff()

                if pathContainer['DC_Load_log_path'] != '':
                    self.DC_LoaderDataOut = self.openDC_LoadLog(pathContainer['DC_Load_log_path'])
                    self.ch_3_data = [self.DC_LoaderDataOut['Time_V'], self.DC_LoaderDataOut['V']]
                    self.ch_4_data = [self.DC_LoaderDataOut['Time_I'], self.DC_LoaderDataOut['I']]

                if pathContainer['Env_Temperature_log_path'] != '':
                    self.TemperatureDataOut = self.openTemperatureLog(pathContainer['Env_Temperature_log_path'])
                    self.ch_5_data = [self.TemperatureDataOut['Time_E_T'], self.TemperatureDataOut['E_T']]

                if pathContainer['Env_Humidity_log_path'] != '':
                    self.HumidityDataOut = self.openHumidityLog(pathContainer['Env_Humidity_log_path'])
                    self.ch_6_data = [self.HumidityDataOut['Time_E_H'], self.HumidityDataOut['E_H']]

                if pathContainer['Env_Pressure_log_path'] != '':
                    self.PressureDataOut = self.openPressureLog(pathContainer['Env_Pressure_log_path'])
                    self.ch_7_data = [self.PressureDataOut['Time_E_P'], self.PressureDataOut['E_P']]

                if pathContainer['SaveAsPath'] != '':
                    if pathContainer['ICS_Power_supply_log_path'] != '' and pathContainer['DC_Load_log_path'] != '' and pathContainer['Env_Temperature_log_path'] != '' and pathContainer['Env_Humidity_log_path'] != '' and pathContainer['Env_Pressure_log_path'] != '':
                        self.generateFile(pathContainer['SaveAsPath'])

            self.plot.updatePlot(self.ch_1_data, self.ch_2_data, self.ch_3_data, self.ch_4_data, self.ch_5_data, self.ch_6_data, self.ch_7_data)
# +++++++++++++++++++ Temperature Min Max Diff ++++++++++++++++++++++++
    def temperatureMinMaxDiff(self):
            dt = numpy.diff(self.ch_1_data[0])
            dT = numpy.diff(self.ch_1_data[1])

            d = dT/dt
            derivative = d.tolist()

            tempNegative = []
            tempNegativeIndexes = []

            minPoints_time = []
            minPoints = []

            for Index in range(len(derivative)):
                if abs(derivative[Index]) > 0.015:
                    if derivative[Index] < 0:
                        tempNegative.append(derivative[Index])
                        tempNegativeIndexes.append(Index)

                    if derivative[Index] > 0:                        
                        try:
                            tempMin = min(tempNegative)
                            minPointIndex = tempNegative.index(tempMin)

                            minPoints_time.append(self.ch_1_data[0][tempNegativeIndexes[minPointIndex]])
                            minPoints.append(derivative[tempNegativeIndexes[minPointIndex]])

                        except ValueError:
                            pass

                        tempNegative = []
                        tempNegativeIndexes = []

            temperatureDiff_time = []
            temperatureDiff_value = []
            for index in range(len(minPoints_time)):
                try:
                    middleTime = minPoints_time[index] + ((minPoints_time[index+1] - minPoints_time[index])/2)
                    temperatureDiff_time.append(middleTime)

                    startIndex = self.ch_1_data[0].index(minPoints_time[index])
                    stopIndex = self.ch_1_data[0].index(minPoints_time[index+1])

                    minValue = min(self.ch_1_data[1][startIndex:stopIndex])
                    maxValue = max(self.ch_1_data[1][startIndex:stopIndex])

                    temperatureDiff_value.append(maxValue-minValue)
                except IndexError:
                    pass
            self.ch_2_data = [temperatureDiff_time, temperatureDiff_value]
# +++++++++++++++++++++++ Generate one File +++++++++++++++++++++++++++
    def generateFile(self, path):                
        data_ch1 = {}
        data_ch3 = {}
        data_ch4 = {}
        data_ch5 = {}
        data_ch6 = {}
        data_ch7 = {}
        
        for index in range(len(self.ch_1_data[0])):
            data_ch1[self.ch_1_data[0][index]] = round(self.ch_1_data[1][index],2)

        for index in range(len(self.ch_3_data[0])):
            data_ch3[self.ch_3_data[0][index]] = round(self.ch_3_data[1][index],2)

        for index in range(len(self.ch_4_data[0])):
            data_ch4[self.ch_4_data[0][index]] = round(self.ch_4_data[1][index],2)

        for index in range(len(self.ch_5_data[0])):
            data_ch5[self.ch_5_data[0][index]] = round(self.ch_5_data[1][index],2)

        for index in range(len(self.ch_6_data[0])):
            data_ch6[self.ch_6_data[0][index]] = round(self.ch_6_data[1][index],2)

        for index in range(len(self.ch_7_data[0])):
            data_ch7[self.ch_7_data[0][index]] = round(self.ch_7_data[1][index],2)

        data = {}

        for key, value in data_ch1.items():
            data[key] = {'ch1':value}

        for key, value in data_ch3.items():
            if key in data.keys():
                data[key].update({'ch3':value})
            else:
                data[key] = {'ch3':value}

        for key, value in data_ch4.items():
            if key in data.keys():
                data[key].update({'ch4':value})
            else:
                data[key] = {'ch4':value}

        for key, value in data_ch5.items():
            if key in data.keys():
                data[key].update({'ch5':value})
            else:
                data[key] = {'ch5':value}

        for key, value in data_ch6.items():
            if key in data.keys():
                data[key].update({'ch6':value})
            else:
                data[key] = {'ch6':value}
        
        for key, value in data_ch7.items():
            if key in data.keys():
                data[key].update({'ch7':value})
            else:
                data[key] = {'ch7':value}

        dataSorted = dict(sorted(data.items()))

        f = open(path,"w")
        f.write("{},{},{},{},{},{},{}\n".format('Time', 'Temperature[*C]', 'Voltage[V]', 'Current[A]', 'Env_temperature[*C]', 'Env_humidity', 'Env_pressure'))

        for key, value in dataSorted.items():
            line = "{},".format(datetime.utcfromtimestamp(key).strftime('%Y/%m/%d %H:%M:%S.%f'))

            try:
                line += "{},".format(value['ch1'])
            except KeyError:
                line += ","

            try:
                line += "{},".format(value['ch3'])
            except KeyError:
                line += ","

            try:
                line += "{},".format(value['ch4'])
            except KeyError:
                line += ","

            try:
                line += "{},".format(value['ch5'])
            except KeyError:
                line += ","

            try:
                line += "{},".format(value['ch6'])
            except KeyError:
                line += ","

            try:
                line += "{}".format(value['ch7'])
            except KeyError:
                pass

            line += "\n"

            f.write(line)
        f.close()
# ++++++++++++++++++++++++++ About dialog +++++++++++++++++++++++++++++
    def aboutDialog(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("About")
        msg.setText("Data plotter")
        msg.setInformativeText("This is Data plotter from different logs, created by Zaza Chubinidze Email : zazachubin@gmail.com, Source code: https://github.com/zazachubin/Keysight_N3300A_DC_Load_scheduler")
        msg.exec_()

if __name__ == '__main__':
    app = QApplication([])
    app.setStyle('Fusion')
    
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    
    ex = App()
    app.exec_()