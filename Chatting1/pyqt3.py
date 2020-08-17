from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QGridLayout, QLineEdit, QLabel, QGroupBox, QVBoxLayout,
                             QHBoxLayout, QApplication, QDialog, QButtonGroup, QRadioButton, QPushButton, QTextEdit)
import threading
import socket

CONNECT_TRY = 100
STATE_CONNECTED = 0
STATE_DISCONNECTED = 1
DEFAULTPORTNUMBER = 43210



class ConnectDialog(QDialog):
    def __init__(self, parent=None):
        super(ConnectDialog, self).__init__(parent)
        self.ButtonPressed = 0

        self.createOkButton()
        self.createCancelButton()
        self.createLineEdit()

        mainLayout = QGridLayout()
        mainLayout.addLayout(self.verticalLayout, 0, 0, 1, 2)
        mainLayout.addWidget(self.OkButton, 2, 0)
        mainLayout.addWidget(self.CancelButton, 2, 1)
        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)
        self.setLayout(mainLayout)

        self.setWindowTitle("Connection")
        self.setModal(True)

    def createLineEdit(self):
        self.lineIpAddress = QLineEdit()
        IpLabel = QLabel("IP address   ")

        self.linePortNumber = QLineEdit()
        AccessPortNumber = str(DEFAULTPORTNUMBER)
        self.linePortNumber.setText(AccessPortNumber)
        portLabel = QLabel("Port number ")

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(2)
        horizontalLayout1 = QHBoxLayout()
        horizontalLayout2 = QHBoxLayout()

        horizontalLayout1.addWidget(IpLabel)
        horizontalLayout1.addWidget(self.lineIpAddress)
        horizontalLayout2.addWidget(portLabel)
        horizontalLayout2.addWidget(self.linePortNumber)
        self.verticalLayout.addLayout(horizontalLayout1)
        self.verticalLayout.addLayout(horizontalLayout2)

    def createOkButton(self):
        layout = QVBoxLayout()
        self.OkButton = QPushButton("Ok")
        self.OkButton.setCheckable(True)
        self.OkButton.toggle()
        self.OkButton.clicked.connect(lambda: self.IpAddressFunction(self.lineIpAddress))
        self.OkButton.clicked.connect(lambda: self.PortNumberFunction(self.linePortNumber))
        self.OkButton.clicked.connect(lambda: self.DisconnectFunction())
        layout.addWidget(self.OkButton)

    def DisconnectFunction(self):
        self.ButtonPressed = CONNECT_TRY
        self.close()

    def createCancelButton(self):
        layout = QVBoxLayout()
        self.CancelButton = QPushButton("Cancel")
        self.CancelButton.setCheckable(False)
        self.CancelButton.toggle()
        self.CancelButton.clicked.connect(lambda: self.close())
        layout.addWidget(self.CancelButton)

    def IpAddressFunction(self, b):
        self.IpAddress = b.text()

    def PortNumberFunction(self, b):
        self.PortNumber = b.text()

class SendEnter(QTextEdit):
    def __init__(self, parent):
        print(self, parent)
        QTextEdit.__init__(self)
        self.parent = parent
        self.currentStr = ""
        self.prevStr = ""

    def keyPressEvent(self, event):
        QTextEdit.keyPressEvent(self, event)
        if event.key() == Qt.Key_Return:
            self.currentStr = self.toPlainText()
            if self.prevStr == "":
                newStr = self.currentStr
            else:
                newStr = self.currentStr[len(self.prevStr):]
            self.prevStr = self.currentStr
            newText = "\n".join(newStr.split("\n")[:-1])
            self.parent.EnterPressed(newText)

class WidgetGallery(QDialog):
    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)
        self.ButtonState = 0

        self.createSendTextBox()
        self.createReceiveTextBox()
        self.createSendButton()
        self.createConnectButton()
        self.createClearSendButton()
        self.createClearReceiveButton()

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.SendTextBox, 1, 0)
        mainLayout.addWidget(self.ReceiveTextBox, 1, 1)
        mainLayout.addWidget(self.SendButton, 2, 0)
        mainLayout.addWidget(self.ConnectButton, 2, 1)
        mainLayout.addWidget(self.ClearSendButtonBox, 3, 0)
        mainLayout.addWidget(self.ClearReceiveButtonBox, 3, 1)
        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(2, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)
        self.setLayout(mainLayout)

        self.setWindowTitle("Chatting")
        self.setModal(False)

    def createSendTextBox(self):
        self.SendTextBox = QGroupBox("Sending Text")

        self.SendMessage = SendEnter(self)
        self.SendMessage.setPlainText("")
        SendBoxLayout = QHBoxLayout()
        SendBoxLayout.setContentsMargins(5, 5, 5, 5)
        SendBoxLayout.addWidget(self.SendMessage)
        self.SendTextBox.setLayout(SendBoxLayout)

    def createReceiveTextBox(self):
        self.ReceiveTextBox = QGroupBox("Receiving Text")

        self.ReceiveMessage = QTextEdit()
        self.ReceiveMessage.setPlainText("")
        self.ReceiveMessage.setReadOnly(True)
        ReceiveBoxLayout = QHBoxLayout()
        ReceiveBoxLayout.setContentsMargins(5, 5, 5, 5)
        ReceiveBoxLayout.addWidget(self.ReceiveMessage)
        self.ReceiveTextBox.setLayout(ReceiveBoxLayout)

    def createSendButton(self):
        layout = QVBoxLayout()
        self.SendButton = QPushButton("Send")
        self.SendButton.setCheckable(True)
        self.SendButton.setEnabled(False)
        self.SendButton.setAutoDefault(True)
        self.SendButton.toggle()
        self.SendButton.clicked.connect(lambda: self.SendButtonFunction(self.SendMessage))
        self.SendButton.clicked.connect(lambda: self.ClearButtonSendBoxFunction())
        layout.addWidget(self.SendButton)

    def createConnectButton(self):
        layout = QVBoxLayout()
        self.ButtonState = STATE_CONNECTED
        self.ConnectButton = QPushButton("Connect")
        self.ConnectButton.setCheckable(False)
        self.ConnectButton.toggle()
        self.ConnectButton.clicked.connect(lambda: self.ConnectButtonFunction())
        self.ConnectButton.clicked.connect(lambda: self.ClearButtonReceiveBoxFunction())
        layout.addWidget(self.ConnectButton)

    def createClearSendButton(self):
        self.ClearSendButtonBox = QGroupBox("Sending Mode")

        layout = QGridLayout()
        self.ClearSendButton = QRadioButton("Clear")
        self.StaySendButton = QRadioButton("Stay")
        self.ClearSendButton.setChecked(True)

        SendMode = QButtonGroup()
        SendMode.addButton(self.ClearSendButton)
        SendMode.addButton(self.StaySendButton)

        layout.addWidget(self.ClearSendButton, 0, 0)
        layout.addWidget(self.StaySendButton, 1, 0)
        self.ClearSendButtonBox.setLayout(layout)

    def createClearReceiveButton(self):
        self.ClearReceiveButtonBox = QGroupBox("Receiving Mode")

        layout = QGridLayout()
        self.ClearReceiveButton = QRadioButton("Clear")
        self.StayReceiveButton = QRadioButton("Stay")
        self.ClearReceiveButton.setChecked(True)

        ReceiveMode = QButtonGroup()
        ReceiveMode.addButton(self.ClearReceiveButton)
        ReceiveMode.addButton(self.StayReceiveButton)

        layout.addWidget(self.ClearReceiveButton, 0, 0)
        layout.addWidget(self.StayReceiveButton, 1, 0)
        self.ClearReceiveButtonBox.setLayout(layout)

    def ClearButtonSendBoxFunction(self):
        if self.ClearSendButton.isChecked() == True:
            self.SendMessage.clear()
        else:
            return

    def ClearButtonReceiveBoxFunction(self):
        if self.ButtonState == STATE_CONNECTED:
            if self.ClearReceiveButton.isChecked() == True:
                self.ReceiveMessage.clear()
            else:
                return
        else:
            return

    def SendButtonFunction(self, b):
        self.MessageSent = b.toPlainText()
        bytesToSend = self.MessageSent.encode("utf-8")
        self.NetworkC.UDPMySocket.sendto(bytesToSend, self.serverAddressPort)

    def EnterPressed(self, b):
        if self.ButtonState == STATE_DISCONNECTED:
            bytesToSend = b.encode("utf-8")
            PortNumber = int(self.ConnectD.PortNumber)
            self.serverAddressPort = (self.ConnectD.IpAddress, PortNumber)
            self.NetworkC.UDPMySocket.sendto(bytesToSend, self.serverAddressPort)
        else:
            return

    def ConnectButtonFunction(self):
        if self.ButtonState == STATE_CONNECTED:
            self.SendButton.setEnabled(False)
            self.ConnectD = ConnectDialog()
            self.ConnectD.show()
            self.ConnectD.exec_()
            if self.ConnectD.ButtonPressed == CONNECT_TRY:
                self.SendButton.setEnabled(True)
                PortNumber = int(self.ConnectD.PortNumber)
                self.NetworkC = NetworkConnect()
                self.serverAddressPort = (self.ConnectD.IpAddress, PortNumber)
                self.NetworkC.run(self.ReceiveMessage)
                self.ConnectButton.setText("Disconnect")
                self.ButtonState = STATE_DISCONNECTED
        else:
            self.SendButton.setEnabled(False)
            self.NetworkC._receiving = False
            self.NetworkC.Receiving.join()
            self.NetworkC.UDPMySocket.close()
            self.ConnectButton.setText("Connect")
            self.ButtonState = STATE_CONNECTED

class NetworkConnect:
    def __init__(self):
        self.bufferSize = 1024
        self.UDPMySocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        IpAddrStr = str(IPAddr)
        print(IpAddrStr)
        self.UDPMySocket.bind((IpAddrStr, DEFAULTPORTNUMBER))
        self.UDPMySocket.settimeout(1.0)

    def receive_function(self, b):
        while self._receiving:
            try:
                msgFromThem = self.UDPMySocket.recvfrom(self.bufferSize)
                if not msgFromThem:
                    break
                msg = msgFromThem[0].decode('utf-8', 'ignore')
                b.append(msg)
            except socket.timeout:
                continue

    def run(self, b):
        self._receiving = True
        self.Receiving = threading.Thread(target=self.receive_function, args=(b, ))
        self.Receiving.start()


import sys

app = QApplication(sys.argv)
Chatting = WidgetGallery()
Chatting.show()
sys.exit(app.exec_())