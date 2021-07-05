import os
import datetime
from datetime import date
from GUI_LOG import Ui_logViewer
from PyQt5.QtWidgets import QFileDialog
from PyQt5 import QtWidgets 
import logging 
import re


today = date.today()
stringBuff = ""
cwd = os.getcwd()
log_path = f'{cwd}/logs'
log_name = f'/log-{today}'
log_extension = '.txt'
file_name = log_path + log_name + log_extension
_started = False 

port = ""

class LogViewer(QtWidgets.QWidget): ## GUI 
    def __init__(self, logFile):
        super().__init__()
        self.logFile = logFile
        self.delete_count = 0 
        self.ui =  Ui_logViewer()
        self.ui.setupUi(self)
        text = open(self.logFile).read()
        last_modified = datetime.datetime.fromtimestamp(os.path.getmtime(self.logFile))
        self.ui.label_lastUpdated.setText(str(last_modified.strftime('%c')))
        self.ui.logFileWindow.insertPlainText(text)
        self.ui.label_fileName.setText(logFile)
        self.ui.logFileWindow.ensureCursorVisible()
        self.ui.button_saveAs.clicked.connect(self.saveAs)
        self.ui.button_deleteLog.clicked.connect(self.delete)
        self.ui.button_Save.clicked.connect(self.save)
        self.ui.button_quit.clicked.connect(self.close)
        self.ui.label_debugText.setText("")

    def keyPressEvent(self, event): # Escape key functionality 
        escape = 16777216 
        key = event.key()
        #print(key)
        if (key == escape):
            self.close()

    def delete(self):
        self.debugText(text = "Click Again to Delete")
        self.ui.button_deleteLog.setStyleSheet(u"background-color: rgb(200, 0, 0);")
        self.delete_count = self.delete_count + 1
        if (self.delete_count > 1):
            try: 
                stopLogger()
                os.remove(self.logFile)
                self.close()
            except: 
                self.debugText(text = "Log is open in another file!")

    def save(self):
        newFile = open(self.logFile, 'w')
        newFile.write(self.ui.logFileWindow.toPlainText())
        newFile.close()
        LogViewPopup(self, filename = self.logFile)
        self.close()

    def saveAs(self):
        options = QFileDialog.Options()
        fileName = QFileDialog.getSaveFileName(self,"Save Log As","","Text Files (*.txt);; Comma Seperated File (*.csv);; Tab Seperated File (*.tsv)", options=options)
        if fileName[0]:
            print(fileName[0])
            self.logFile = fileName[0]
            self.save()

    def debugText(self, text = "", color = "black"):
        self.ui.label_debugText.setStyleSheet(f"color:{color}; font: bold 12px;")
        self.ui.label_debugText.setText(text)
        pass 

def changeLogPath():
    folder = QFileDialog.getExistingDirectory(caption = "Set Log Directory",options = QFileDialog.ShowDirsOnly)
    return folder

def LogViewPopup(self, filename = "", latest = False):
    if latest: 
        filename = file_name
    if filename == "":
        try:
            options = QFileDialog.Options()
            files = QFileDialog.getOpenFileNames(self, "Open Log File", log_path, "*.txt", options=options)
            filename = files[0][0]
            print(filename)
        except Exception as e:
            print("ERROR GETTING FILE NAME: ", e)
    print("Opening Log: ", filename)
    if not filename: ## No File Selected
        return True
    if os.path.exists(filename):
        self.window = LogViewer(filename)
        self.window.show()
        return True
    else: 
        return False

    ## NON-GUI FUNCTIONS --------------------


def startLogger():
    global _started
    if not _started: 
        _started = True
        print("Starting Logger")
        logging.basicConfig(filename = file_name, format = f'{port}|%(asctime)s.%(msecs)03d|\t %(message)s', datefmt='%I:%M:%S')
    else: 
        stopLogger()

def stopLogger():
    global _started 
    _started = False
    print("Stopping Logger")
    logging.shutdown()
    log = logging.getLogger()  #root logger 
    for hdlr in log.handlers[:]:
        if isinstance(hdlr,logging.FileHandler):
            log.removeHandler(hdlr)

def setLogPath(new_log_path = ""): 
    print("Setting new Log Path:" , new_log_path)
    if len(new_log_path) > 5: 
        stopLogger()
        global log_path
        log_path = new_log_path
        log_name = f'\\log-{today}'
        log_extension = '.txt'
        global file_name
        file_name = log_path + log_name + log_extension 

def setPort(com_port = "NO_PORT"):
    global port
    port = com_port.ljust(7)
    print("Set logging port to:", port)

def addLine(text):
    global _started
    if not _started: 
        startLogger()
    global stringBuff
    stringBuff = stringBuff + text.replace("\r", '')
    if '\n' in stringBuff: 
        logList = re.split('(\n)' , stringBuff)
        logList = stringBuff.splitlines(True)
        #print(logList)
        stringBuff = ""
        for line in logList:
            if "\n" in line:
                line = line.replace("\n", "")
                #print(line)
                logging.warning(line)
            else:
                #print(line, "waiting for newline!")
                stringBuff += line

def archiveLog():
    stopLogger()
    logIndex = 1 
    new_name = log_name + f'({logIndex})' + log_extension
    while (os.path.exists(log_path + new_name)):
        print(f"{new_name} already exists!")
        logIndex += 1
        new_name = log_name + f'({logIndex})' + log_extension
    os.rename(file_name, log_path + new_name)
    #print("Archived Log to:", new_name) 
    addLine("Log archived by user\n")
    return new_name

setPort()

# I have this because Im an idiot and run this program often, thinking it's main...
if __name__ == '__main__':
    import main
    main.execute()

    

