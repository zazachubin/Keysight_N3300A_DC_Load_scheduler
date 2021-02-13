##!/usr/bin/env python3
from PyQt5.QtWidgets import (QMainWindow, QApplication, QLineEdit,
                             QLCDNumber, QWidget, QFileDialog, QMessageBox,
                             QPushButton, QAction, QComboBox, QVBoxLayout, 
                             QHBoxLayout, QLabel, QDockWidget, QGroupBox,
                             QProgressBar, QTableWidget, QHeaderView)
from PyQt5.QtGui import QIcon, QPalette, QColor, QDoubleValidator, QIntValidator
from PyQt5.QtCore import Qt, QDir, QThread, pyqtSignal
from datetime import datetime
import random
import pyvisa
import json
import time

threadAccess = True
# ~~~~~~~~~~~~~~~~~~~~~~~ Scheduler table ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class SchedulerTableView(QTableWidget):
#++++++++++++++++++++++++++++ __init__ ++++++++++++++++++++++++++++++++
    def __init__(self, parent=None):
        super(SchedulerTableView, self).__init__(0,2, parent)
        self.add_del_buttons_index = 0
        self.selected_Row = 0
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.verticalHeader().sectionClicked.connect(self.__determineIndex)
        self.show()
#++++++++++++++++++++++++++++ Set Data ++++++++++++++++++++++++++++++++
    def setData(self, setSchedulerData):
        self.SchedulerData = setSchedulerData
        self.add_del_buttons_index = len(self.SchedulerData["Duration [s]"]) + 1
        self.setRowCount(self.add_del_buttons_index)

        horHeaders = []
        for n, key in enumerate(self.SchedulerData.keys()):
            horHeaders.append(key)
            for m, item in enumerate(self.SchedulerData[key]):
                newitem = QLineEdit()
                newitem.setAlignment(Qt.AlignCenter)
                newitem.setValidator(QDoubleValidator())
                newitem.setText(item)
                self.setCellWidget(m, n, newitem)

        self.setHorizontalHeaderLabels(horHeaders)

        self.addButton = QPushButton('Add row')
        self.addButton.setIcon(QIcon('img/addRow.svg'))
        self.addButton.clicked.connect(self.__addRow)
        self.setCellWidget(self.add_del_buttons_index-1, 0, self.addButton)

        self.removeButton = QPushButton('Remove row')
        self.removeButton.setIcon(QIcon('img/DelRow.svg'))
        self.removeButton.clicked.connect(self.__delRow)
        self.setCellWidget(self.add_del_buttons_index-1, 1, self.removeButton)

        self.selected_Row = self.rowCount()-1
#++++++++++++++++++++++++++++ Get Data ++++++++++++++++++++++++++++++++
    def getData(self):
        self.add_del_buttons_index = self.rowCount()
        self.tableColNumber = self.columnCount()
        SchedulerDataOut = {'Duration [s]':[], 'Current [A]' :[]}

        for column, key in zip(range(self.tableColNumber), self.SchedulerData.keys()):
            for row in range (self.add_del_buttons_index-1):
                SchedulerDataOut[key].append(self.cellWidget(row,column).text())

        return SchedulerDataOut
#++++++++++++++++++++++++++++ Add Row +++++++++++++++++++++++++++++++++
    def __addRow(self):
        self.add_del_buttons_index = self.rowCount()
        self.removeCellWidget(self.add_del_buttons_index, 0)
        self.removeCellWidget(self.add_del_buttons_index, 1)

        self.insertRow(self.selected_Row)

        self.addButton = QPushButton('Add row')
        self.addButton.setIcon(QIcon('img/addRow.svg'))
        self.addButton.clicked.connect(self.__addRow)
        self.setCellWidget(self.add_del_buttons_index, 0, self.addButton)

        self.removeButton = QPushButton('Remove row')
        self.removeButton.setIcon(QIcon('img/DelRow.svg'))
        self.removeButton.clicked.connect(self.__delRow)
        self.setCellWidget(self.add_del_buttons_index, 1, self.removeButton)

        for i in range(2):
            newitem = QLineEdit()
            newitem.setAlignment(Qt.AlignCenter)
            newitem.setValidator(QDoubleValidator())
            self.setCellWidget(self.selected_Row, i, newitem)
#+++++++++++++++++++++++++++ Delete Row +++++++++++++++++++++++++++++++
    def __delRow(self):
        self.add_del_buttons_index = self.rowCount()

        if self.add_del_buttons_index-1 != self.selected_Row:
            self.removeRow(self.selected_Row)
#++++++++++++++++++++++++ Determine index +++++++++++++++++++++++++++++
    def __determineIndex(self):
        self.selected_Row = self.currentRow()

# ~~~~~~~~~~~~~~~~~~~~~~~~~ Custom QComboBox ~~~~~~~~~~~~~~~~~~~~~~~~~~
class ComboBox(QComboBox):
    popupAboutToBeShown = pyqtSignal()
# ++++++++++++++++++++++++++++ showPopup ++++++++++++++++++++++++++++++
    def showPopup(self):
        self.popupAboutToBeShown.emit()
        super(ComboBox, self).showPopup()

# ~~~~~~~~~~~~~~~~~~~~~~~~~ Read Data Thread ~~~~~~~~~~~~~~~~~~~~~~~~~~
class ReadDataThread(QThread):
    change_value = pyqtSignal(float, float, float)
    def __init__(self, device, delay, parent=None):
        super(ReadDataThread, self).__init__()
        self._isRunning = True
        self.device = device
        self.Voltage = 0
        self.Current = 0
        self.Power = 0

        try:
            self.delay = int(float(delay)*1000)
        except ValueError:
            self.delay = int(float(delay.replace(",", "."))*1000)

    def run(self):
        while self._isRunning:
            self.readData()
            self.change_value.emit(self.Voltage,self.Current,self.Power)
            QThread.msleep(self.delay)

    def readData(self):
        global threadAccess
        if threadAccess:
            threadAccess = False
            read = True
            while read:
                try:
                    time.sleep(0.1)
                    V = float(self.device.query("MEAS:VOLT?"))
                    time.sleep(0.1)
                    I = float(self.device.query("MEAS:CURR?"))

                    read = False
                except pyvisa.errors.VisaIOError:
                    V = 0
                    I = 0
                    read = False
                    pass
                except AttributeError:
                    V = random.uniform(9,10)
                    I = random.uniform(10.5,11.5)
                    read = False
                    pass
            
            P = I * V
            self.Voltage = V
            self.Current = I
            self.Power = P

            threadAccess = True
        else:
            pass

    def stop(self):
        self._isRunning = False

# ~~~~~~~~~~~~~~~~~~~~~~~~~~ Control Thread ~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ControlThread(QThread):
    finished = pyqtSignal()
    message = pyqtSignal(str)
    def __init__(self, inst, SchedulerData, repeater, parent=None):
        super(ControlThread, self).__init__()
        self._isRunning = True
        self.inst = inst
        self.SchedulerData = SchedulerData
        self.repeater = repeater

    def run(self):
        self.timerControl()
        self.finished.emit()

    def timerControl(self):
        global threadAccess

        threadAccess = False
        try:
            self.inst.write('FUNC CURR')
        except AttributeError:
            print('>>>> Send comand >> "FUNC CURR"')
        threadAccess = True

        time.sleep(0.2)

        threadAccess = False
        try:
            self.inst.write('CURR 0')
        except AttributeError:
            print('>>>> Send comand >> "CURR 0"')
        threadAccess = True

        DurationPlan = []
        DurationStr = self.SchedulerData['Duration [s]']

        for item in DurationStr:
            try:
                DurationPlan.append(float(item))
            except ValueError:
                pass

        CurrentPlan = []
        CurrentStr = self.SchedulerData['Current [A]']

        for item in CurrentStr:
            if item != '':
                CurrentPlan.append(item)
            else:
                CurrentPlan.append("0")

        for currentIteration in range(self.repeater):
            if not self._isRunning:
                break
            print("####### Itteration {}/{} #######".format(currentIteration+1, self.repeater))
            index = 0
            for duration in DurationPlan:
                if not self._isRunning:
                    break

                self.message.emit("Running >> Duration {}[s] ---> Current {}[A] ".format(duration, CurrentPlan[index]))
                print("--- Step {} ---".format(index+1))
                print(">> Duration {}[s]".format(duration))
                print(">> Current {}[A]".format(CurrentPlan[index]))

                threadAccess = False
                try:
                    self.inst.write('CURR {}'.format(CurrentPlan[index]))
                except AttributeError:
                    print('>>>> Send comand >> "CURR {}"'.format(CurrentPlan[index]))
                threadAccess = True

                start_time = time.time()
                stop_time = start_time
                while(stop_time - start_time <= duration):
                    if not self._isRunning:
                        break
                    stop_time = time.time()
                index += 1

        threadAccess = False
        try:
            self.inst.write('CURR 0')
        except AttributeError:
            print('>>>> Send comand >> "CURR 0"')
        threadAccess = True
        print("#################")
        print("Turn OFF LOAD")
        if self._isRunning: 
            print("Done!")
        else:
            print("Stoped !")

    def stop(self):
        self._isRunning = False

# ~~~~~~~~~~~~~~~~~~~~~~~~ ProgressBar Thread ~~~~~~~~~~~~~~~~~~~~~~~~~
class ProgressBarThread(QThread):
    progress = pyqtSignal(float)
    def __init__(self, SchedulerData, repeater, parent=None):
        super(ProgressBarThread, self).__init__()
        self._isRunning = True
        self.SchedulerData = SchedulerData
        self.repeater = repeater
        self.thread_start_time = time.time()

    def run(self):
        self.progressBarCalc()

    def progressBarCalc(self):
        DurationPlan = []
        DurationStr = self.SchedulerData['Duration [s]']

        for item in DurationStr:
            try:
                DurationPlan.append(float(item))
            except ValueError:
                pass

        self.progress.emit(0)

        full_time = sum(DurationPlan) * self.repeater
        currentTime = time.time()
        while(currentTime-self.thread_start_time <= full_time):
            currentTime = time.time()
            percent = (currentTime-self.thread_start_time)*100/full_time
            self.progress.emit(percent)
            time.sleep(0.5)

    def stop(self):
        self._isRunning = False
#//////////////////////////////////////////////////////////////////////
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ App ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class App(QMainWindow):
# +++++++++++++++++++++++++++++__init__ +++++++++++++++++++++++++++++++
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('img/N3300A.jpg'))
        self.setWindowTitle('DC Load Scheduler')
        self.setGeometry(0, 0, 800, 560)
        self.config = { 'LogPath'  : '',
                        'Port'     : '',
                        'Delay'    : 1,
                        'Scheduler':{'Duration [s]':[],
                                     'Current [A]' :[]},
                        'Repeater' : '5'
                        }
        self.SchedulerData = {'Duration [s]':[], 'Current [A]' :[]}

        self._alreadyRun = False
        self._stop = False

        self.device = pyvisa.ResourceManager()

        ################# Load configuration  #########################
        self.loadConfigs()

        self.initUI()
# +++++++++++++++++++++++++++++ initUI ++++++++++++++++++++++++++++++++
    def initUI(self):
######################### Set Widgets styles ##########################
        self.setStyleSheet("""QLCDNumber {  margin: 1px;
                                            padding: 7px;
                                            background-color: rgba(100,255,255,20);
                                            color: rgb(255,255,255);
                                            border-style: solid;
                                            border-radius: 8px;
                                            border-width: 3px;
                                            border-color: rgba(0,140,255,255);}
                              QDockWidget::title {text-align: center;}
                              QGroupBox:title {subcontrol-position: top center;}""")
######################## Set window to center #########################
        self.center()
########################## Control Buttons ############################
        ######################## Exit #################################
        exitButton = QAction(QIcon('img/close.svg'), 'Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.triggered.connect(self.close)
        ################### Export configs ############################
        exportConfig = QAction(QIcon('img/config.svg'), 'Save configs', self)
        exportConfig.triggered.connect(self.exportConfig)
        ####################### About #################################
        aboutButton = QAction(QIcon('img/info.svg'), 'About', self)
        aboutButton.triggered.connect(self.aboutDialog)
        ######################## Play #################################
        PlayAct = QAction(QIcon('img/play.svg'),'Play', self)
        PlayAct.triggered.connect(self.start)
        ######################## Stop #################################
        StopAct = QAction(QIcon('img/stop.svg'), 'Stop', self)
        StopAct.triggered.connect(self.stop)
####################### Add buttons on toolbar ########################
        toolbar = self.addToolBar('Tools')
        toolbar.addAction(exitButton)
        toolbar.addAction(exportConfig)
        toolbar.addSeparator()
        toolbar.addAction(PlayAct)
        toolbar.addAction(StopAct)
        toolbar.addSeparator()
        toolbar.addAction(aboutButton)
####################### Control groups layout #########################
        GroupVLayout = QVBoxLayout()
########################### Select Device #############################
        Device = QGroupBox('Select Device')
        ################## Selector button ############################
        self.PortSelector = ComboBox()
        self.PortSelector.setStyleSheet("QLineEdit { background-color: yellow }")
        self.PortSelector.popupAboutToBeShown.connect(self.findPorts)
        ##################### Load OFF ################################
        offButton = QPushButton('Device Off')
        offButton.setIcon(QIcon('img/power_button.svg'))
        offButton.clicked.connect(self.deviceOFF)
        #################### set widget ###############################
        Device_VLayout = QVBoxLayout()
        Device_VLayout.addWidget(self.PortSelector)
        Device_VLayout.addWidget(offButton)
        Device.setLayout(Device_VLayout)
############################ Data Export ##############################
        Log_Data = QGroupBox('Data Export')
        ################## Selector button ############################
        self.chooseFile = QPushButton(QIcon('img/files.svg'),"Select File")
        self.chooseFile.clicked.connect(self.saveAs)
        ################ Current path field ###########################
        self.selectedPath = QLineEdit()
        self.selectedPath.setAlignment(Qt.AlignCenter)
        self.selectedPath.setReadOnly(True)
        self.selectedPath.setToolTip("<h5>Current path")
        #################### Delay label ##############################
        delayLabel = QLabel("Delay [s]")
        #################### Delay Layout #############################
        delayHLayout = QHBoxLayout()
        ################# Data export speed ###########################
        validator = QDoubleValidator()
        validator.setRange(1.0, 1000000.0, 1)
        self.delay = QLineEdit()
        self.delay.setAlignment(Qt.AlignCenter)
        self.delay.setValidator(validator)
        ################ Set widgets & layouts ########################
        delayHLayout.addWidget(self.delay)
        delayHLayout.addWidget(delayLabel)

        Log_Data_VLayout = QVBoxLayout()
        Log_Data_VLayout.addWidget(self.chooseFile)
        Log_Data_VLayout.addWidget(self.selectedPath)
        Log_Data_VLayout.addLayout(delayHLayout)
        Log_Data.setLayout(Log_Data_VLayout)
############################# Scheduler ###############################
        Scheduler = QGroupBox('Scheduler')
        ################## Scheduler table ############################
        SchedulerVLayout = QVBoxLayout()
        self.SchedulerTable = SchedulerTableView()

        self.SchedulerTable.setData(self.SchedulerData)
        ################## Repeater field #############################
        onlyInt = QIntValidator()
        self.Repeater = QLineEdit()
        self.Repeater.setAlignment(Qt.AlignCenter)
        self.Repeater.setValidator(onlyInt)
        ################## Repeater label #############################
        repeaterLabel = QLabel("Repeater")
        ################# Repeater Layout #############################
        delayHLayout = QHBoxLayout()
        ################ Set widgets & layouts ########################
        delayHLayout.addWidget(self.Repeater)
        delayHLayout.addWidget(repeaterLabel)

        SchedulerVLayout.addWidget(self.SchedulerTable)
        SchedulerVLayout.addLayout(delayHLayout)
        Scheduler.setLayout(SchedulerVLayout)

        GroupVLayout.addWidget(Device)
        GroupVLayout.addWidget(Log_Data)
        GroupVLayout.addWidget(Scheduler)
############################ LCD displays #############################
        ################## Voltade display ############################
        self.Voltage = QLCDNumber()
        self.Voltage.setDigitCount(9)
        ################## Current display ############################
        self.Current = QLCDNumber()
        self.Current.setDigitCount(9)
        ################### Power display #############################
        self.Power = QLCDNumber()
        self.Power.setDigitCount(9)
        ############## Set displays on layout #########################
        LCD_Vlayout = QVBoxLayout()
        LCD_Vlayout.addWidget(self.Voltage)
        LCD_Vlayout.addWidget(self.Current)
        LCD_Vlayout.addWidget(self.Power)
        ################# Display labels ##############################
        Label_Voltage = QLabel("V")
        Label_Current = QLabel("A")
        Label_Power = QLabel("W")
        ############### Set widgets on layout #########################
        Label_Vlayout = QVBoxLayout()
        Label_Vlayout.addWidget(Label_Voltage)
        Label_Vlayout.addWidget(Label_Current)
        Label_Vlayout.addWidget(Label_Power)
        ######### Set Displays and labels on layout ###################
        LCD_Hlayout = QHBoxLayout()
        LCD_Hlayout.addLayout(LCD_Vlayout,98)
        LCD_Hlayout.addLayout(Label_Vlayout,2)
################# Set control widgets on dockedWidget #################
        ######## Set control widgets on DockWidget area ###############
        self.controlWidgets = QWidget()
        self.controlWidgets.setLayout(GroupVLayout)
        self.controlDockWidget = QDockWidget('Control')
        self.controlDockWidget.setWidget(self.controlWidgets)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.controlDockWidget)
        ######### Set View widgets on DockWidget area #################
        self.ViewWidgets = QWidget()
        self.ViewWidgets.setLayout(LCD_Hlayout)
        self.ViewDockWidget = QDockWidget('Monitoring')
        self.ViewDockWidget.setWidget(self.ViewWidgets)
        self.addDockWidget(Qt.RightDockWidgetArea, self.ViewDockWidget)
############################# ProgressBar  ############################
        self.progressBar = QProgressBar()   
        self.statusBar().addPermanentWidget(self.progressBar)
        self.progressBar.setValue(0)
############################# Set Configs  ############################
        self.setConfigs()
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
# ++++++++++++++++++++++++++++++ Start ++++++++++++++++++++++++++++++++
    def start(self):
        if self._alreadyRun != True and self._filePath != '':
            try:
                self.selected_inst = self.device.open_resource(self.PortSelector.currentText())
            except pyvisa.errors.VisaIOError:
                self.selected_inst = ""

            self.SchedulerData = self.SchedulerTable.getData()
            self.config['Repeater'] = self.Repeater.text()

            self.thread1 = ReadDataThread(self.selected_inst, self.delay.text())
            self.thread1.change_value.connect(self.viewData)

            self.thread2 = ControlThread(self.selected_inst, self.SchedulerData, int(self.config['Repeater']))
            self.thread2.message.connect(self.statuseMessage)
            self.thread2.finished.connect(self.finish)

            self.thread3 = ProgressBarThread(self.SchedulerData, int(self.config['Repeater']))
            self.thread3.progress.connect(self.viewProgressBar)

            try:
                self.f = open(self._filePath,"w+")
                self.f.write("Time,Voltage[V],Current[A],Power[Pa]\n")
                self.f.close()
            except FileNotFoundError:
                self.statuseMessage("Path doesn't exist!")
                pass

            self._alreadyRun = True
            self.thread1.start()
            self.thread2.start()
            self.thread3.start()
            self.statuseMessage("Running")
# ++++++++++++++++++++++++++++++ Stop +++++++++++++++++++++++++++++++++
    def stop(self):
        self._alreadyRun = False
        self._stop = True
        try:
            self.thread1.stop()
            self.thread2.stop()
            self.thread3.stop()
            self.statuseMessage("Stop")
        except AttributeError:
            pass
# +++++++++++++++++++++++++++++ Finish +++++++++++++++++++++++++++++++++
    def finish(self):
        self.stop()
        self.statuseMessage("Finish")
# ++++++++++++++++++++++++++++ View data +++++++++++++++++++++++++++++++
    def viewData(self, Voltage, Current, Power):
        timestampStr = str(datetime.fromtimestamp(datetime.utcnow().timestamp()))

        self.Voltage.display("%.4f" % (Voltage))
        self.Current.display("%.4f" % (Current))
        self.Power.display("%.4f" % (Power))
        
        try:
            self.f = open(self._filePath,"a+")
            self.f.write("{},".format(timestampStr) + "%.6f,%.6f,%.6f\n" % (Voltage,Current,Power))
            self.f.close()
        except FileNotFoundError:
            self.statuseMessage("Path doesn't exist!")
            pass
# +++++++++++++++++++++++ View ProgressBar ++++++++++++++++++++++++++++
    def viewProgressBar(self, percent):
        self.progressBar.setValue(percent)
# +++++++++++++++++++++++++++++ Save ++++++++++++++++++++++++++++++++++
    def saveAs(self):
        saveAspath, _ = QFileDialog.getSaveFileName(self, 'Save as', QDir.homePath(), "TXT Files(*.txt)")
        if saveAspath != '':
            self._filePath = saveAspath
            self.selectedPath.setText(self._filePath)
            self.statuseMessage("Log file is selected")
# ++++++++++++++++++++++++++ About dialog +++++++++++++++++++++++++++++
    def aboutDialog(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("About")
        msg.setText("Keysight N3300A System DC Electronic Load")
        msg.setInformativeText("This is DC electronic load scheduler, created by Zaza Chubinidze Email : zazachubin@gmail.com, Source code: https://github.com/zazachubin/Keysight_N3300A_DC_Load_scheduler")
        msg.exec_()
# +++++++++++++++++++++++++ export Config +++++++++++++++++++++++++++++
    def exportConfig(self):
        configPath = "config.json"

        self.config['LogPath'] = self._filePath
        self.config['Port'] = self.PortSelector.currentText()
        self.config['Delay'] = self.delay.text()
        self.SchedulerData = self.SchedulerTable.getData()
        self.config['Scheduler'] = self.SchedulerData
        self.config['Repeater'] = self.Repeater.text()

        with open(configPath, 'w') as outfile:
            json.dump(self.config, outfile, indent=4)
        
        self.statuseMessage("Save configs")
# ++++++++++++++++++++++++++ loadConfigs ++++++++++++++++++++++++++++++
    def loadConfigs(self):
        configPath = "config.json"
        with open(configPath, 'r') as outfile:
            self.config = json.load(outfile)
        
        self._filePath = self.config['LogPath']
        self.SchedulerData = self.config['Scheduler']
# ++++++++++++++++++++++++++ Set Configs ++++++++++++++++++++++++++++++
    def setConfigs(self):
        self.PortSelector.addItem(self.config['Port'])
        self.delay.setText(self.config['Delay'])
        self.selectedPath.setText(self._filePath)
        self.Repeater.setText(self.config['Repeater'])
# ++++++++++++++++++++++++++ Finde ports ++++++++++++++++++++++++++++++
    def findPorts(self):
        self.device = pyvisa.ResourceManager()
        port_list = self.device.list_resources()
        port_list_names = []
        self.PortSelector.clear()

        for port in port_list:
            port_list_names.append(port)
        self.PortSelector.addItems(port_list_names)
# ++++++++++++++++++++++++ Status Messages ++++++++++++++++++++++++++++
    def statuseMessage(self, message):
        self.statusBar().showMessage(message)
# +++++++++++++++++++++++++++ Device Off ++++++++++++++++++++++++++++++
    def deviceOFF(self):
        try:
            self.selected_inst = self.device.open_resource(self.PortSelector.currentText())
        except pyvisa.errors.VisaIOError:
            self.selected_inst = ""

        try:
            self.selected_inst.write('CURR 0')
        except AttributeError:
            print('>>>> Simulation >> Send comand >> "CURR 0"')
        self.statuseMessage("Device OFF")

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