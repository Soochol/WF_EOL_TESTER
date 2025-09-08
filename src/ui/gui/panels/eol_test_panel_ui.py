# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'eol_test_panel.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QGroupBox, QHBoxLayout,
    QHeaderView, QLabel, QProgressBar, QPushButton,
    QSizePolicy, QSpacerItem, QTableWidget, QTableWidgetItem,
    QTextEdit, QVBoxLayout, QWidget)

class Ui_EOLTestPanel(object):
    def setupUi(self, EOLTestPanel):
        if not EOLTestPanel.objectName():
            EOLTestPanel.setObjectName(u"EOLTestPanel")
        EOLTestPanel.resize(800, 600)
        self.mainLayout = QVBoxLayout(EOLTestPanel)
        self.mainLayout.setSpacing(20)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(12, 12, 12, 12)
        self.topRowLayout = QHBoxLayout()
        self.topRowLayout.setSpacing(16)
        self.topRowLayout.setObjectName(u"topRowLayout")
        self.controlGroup = QGroupBox(EOLTestPanel)
        self.controlGroup.setObjectName(u"controlGroup")
        self.controlLayout = QVBoxLayout(self.controlGroup)
        self.controlLayout.setSpacing(8)
        self.controlLayout.setObjectName(u"controlLayout")
        self.controlLayout.setContentsMargins(16, 20, 16, 16)
        self.startTestButton = QPushButton(self.controlGroup)
        self.startTestButton.setObjectName(u"startTestButton")
        self.startTestButton.setMinimumSize(QSize(0, 29))
        self.startTestButton.setMaximumSize(QSize(16777215, 29))

        self.controlLayout.addWidget(self.startTestButton)

        self.buttonSpacer1 = QSpacerItem(20, 8, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.controlLayout.addItem(self.buttonSpacer1)

        self.stopTestButton = QPushButton(self.controlGroup)
        self.stopTestButton.setObjectName(u"stopTestButton")
        self.stopTestButton.setEnabled(False)
        self.stopTestButton.setMinimumSize(QSize(0, 29))
        self.stopTestButton.setMaximumSize(QSize(16777215, 29))

        self.controlLayout.addWidget(self.stopTestButton)

        self.buttonSpacer2 = QSpacerItem(20, 8, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.controlLayout.addItem(self.buttonSpacer2)

        self.resetButton = QPushButton(self.controlGroup)
        self.resetButton.setObjectName(u"resetButton")
        self.resetButton.setMinimumSize(QSize(0, 29))
        self.resetButton.setMaximumSize(QSize(16777215, 29))

        self.controlLayout.addWidget(self.resetButton)

        self.controlVerticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.controlLayout.addItem(self.controlVerticalSpacer)


        self.topRowLayout.addWidget(self.controlGroup)

        self.resultsGroup = QGroupBox(EOLTestPanel)
        self.resultsGroup.setObjectName(u"resultsGroup")
        self.resultsLayout = QVBoxLayout(self.resultsGroup)
        self.resultsLayout.setSpacing(12)
        self.resultsLayout.setObjectName(u"resultsLayout")
        self.resultsLayout.setContentsMargins(16, 20, 16, 16)
        self.summaryLabel = QLabel(self.resultsGroup)
        self.summaryLabel.setObjectName(u"summaryLabel")

        self.resultsLayout.addWidget(self.summaryLabel)

        self.resultsTable = QTableWidget(self.resultsGroup)
        self.resultsTable.setObjectName(u"resultsTable")
        self.resultsTable.setAlternatingRowColors(True)
        self.resultsTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.resultsTable.horizontalHeader().setStretchLastSection(True)

        self.resultsLayout.addWidget(self.resultsTable)


        self.topRowLayout.addWidget(self.resultsGroup)


        self.mainLayout.addLayout(self.topRowLayout)

        self.progressGroup = QGroupBox(EOLTestPanel)
        self.progressGroup.setObjectName(u"progressGroup")
        self.progressLayout = QVBoxLayout(self.progressGroup)
        self.progressLayout.setSpacing(12)
        self.progressLayout.setObjectName(u"progressLayout")
        self.progressLayout.setContentsMargins(16, 20, 16, 16)
        self.statusLabel = QLabel(self.progressGroup)
        self.statusLabel.setObjectName(u"statusLabel")

        self.progressLayout.addWidget(self.statusLabel)

        self.progressBar = QProgressBar(self.progressGroup)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(0)

        self.progressLayout.addWidget(self.progressBar)


        self.mainLayout.addWidget(self.progressGroup)

        self.logGroup = QGroupBox(EOLTestPanel)
        self.logGroup.setObjectName(u"logGroup")
        self.logLayout = QVBoxLayout(self.logGroup)
        self.logLayout.setSpacing(12)
        self.logLayout.setObjectName(u"logLayout")
        self.logLayout.setContentsMargins(16, 20, 16, 16)
        self.testLogText = QTextEdit(self.logGroup)
        self.testLogText.setObjectName(u"testLogText")
        self.testLogText.setMaximumSize(QSize(16777215, 150))
        self.testLogText.setReadOnly(True)

        self.logLayout.addWidget(self.testLogText)


        self.mainLayout.addWidget(self.logGroup)


        self.retranslateUi(EOLTestPanel)

        QMetaObject.connectSlotsByName(EOLTestPanel)
    # setupUi

    def retranslateUi(self, EOLTestPanel):
        EOLTestPanel.setWindowTitle(QCoreApplication.translate("EOLTestPanel", u"EOL Test Panel", None))
        self.controlGroup.setTitle(QCoreApplication.translate("EOLTestPanel", u"Test Control", None))
        self.controlGroup.setStyleSheet(QCoreApplication.translate("EOLTestPanel", u"QGroupBox {\n"
"    font-weight: bold;\n"
"    font-size: 12px;\n"
"    border: 2px solid #E8E8E8;\n"
"    border-radius: 8px;\n"
"    margin-top: 1ex;\n"
"    padding-top: 10px;\n"
"}\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 10px;\n"
"    padding: 0 8px 0 8px;\n"
"}", None))
        self.startTestButton.setText(QCoreApplication.translate("EOLTestPanel", u"Start EOL Test", None))
        self.startTestButton.setStyleSheet(QCoreApplication.translate("EOLTestPanel", u"QPushButton {\n"
"    background-color: #27AE60;\n"
"    color: white;\n"
"    border: none;\n"
"    border-radius: 6px;\n"
"    font-weight: bold;\n"
"    font-size: 13px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: #229954;\n"
"}\n"
"QPushButton:pressed {\n"
"    background-color: #1E8449;\n"
"}", None))
        self.stopTestButton.setText(QCoreApplication.translate("EOLTestPanel", u"Stop Test", None))
        self.stopTestButton.setStyleSheet(QCoreApplication.translate("EOLTestPanel", u"QPushButton {\n"
"    background-color: #E74C3C;\n"
"    color: white;\n"
"    border: none;\n"
"    border-radius: 6px;\n"
"    font-weight: bold;\n"
"    font-size: 13px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: #CD4335;\n"
"}\n"
"QPushButton:pressed {\n"
"    background-color: #B03A2E;\n"
"}\n"
"QPushButton:disabled {\n"
"    background-color: #BDC3C7;\n"
"    color: #7F8C8D;\n"
"}", None))
        self.resetButton.setText(QCoreApplication.translate("EOLTestPanel", u"Reset", None))
        self.resetButton.setStyleSheet(QCoreApplication.translate("EOLTestPanel", u"QPushButton {\n"
"    background-color: #F39C12;\n"
"    color: white;\n"
"    border: none;\n"
"    border-radius: 6px;\n"
"    font-weight: bold;\n"
"    font-size: 13px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: #E67E22;\n"
"}\n"
"QPushButton:pressed {\n"
"    background-color: #D35400;\n"
"}", None))
        self.resultsGroup.setTitle(QCoreApplication.translate("EOLTestPanel", u"Test Results", None))
        self.resultsGroup.setStyleSheet(QCoreApplication.translate("EOLTestPanel", u"QGroupBox {\n"
"    font-weight: bold;\n"
"    font-size: 12px;\n"
"    border: 2px solid #E8E8E8;\n"
"    border-radius: 8px;\n"
"    margin-top: 1ex;\n"
"    padding-top: 10px;\n"
"}\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 10px;\n"
"    padding: 0 8px 0 8px;\n"
"}", None))
        self.summaryLabel.setText(QCoreApplication.translate("EOLTestPanel", u"No test results available", None))
        self.summaryLabel.setStyleSheet(QCoreApplication.translate("EOLTestPanel", u"color: #7F8C8D; padding: 4px; font-weight: bold; font-size: 11px;", None))
        self.resultsTable.setStyleSheet(QCoreApplication.translate("EOLTestPanel", u"QTableWidget {\n"
"    gridline-color: #E8E8E8;\n"
"    font-size: 10px;\n"
"}\n"
"QHeaderView::section {\n"
"    background-color: #F8F9FA;\n"
"    padding: 6px;\n"
"    border: 1px solid #E8E8E8;\n"
"    font-weight: bold;\n"
"}", None))
        self.progressGroup.setTitle(QCoreApplication.translate("EOLTestPanel", u"Test Progress", None))
        self.progressGroup.setStyleSheet(QCoreApplication.translate("EOLTestPanel", u"QGroupBox {\n"
"    font-weight: bold;\n"
"    font-size: 12px;\n"
"    border: 2px solid #E8E8E8;\n"
"    border-radius: 8px;\n"
"    margin-top: 1ex;\n"
"    padding-top: 10px;\n"
"}\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 10px;\n"
"    padding: 0 8px 0 8px;\n"
"}", None))
        self.statusLabel.setText(QCoreApplication.translate("EOLTestPanel", u"Ready to start test", None))
        self.statusLabel.setStyleSheet(QCoreApplication.translate("EOLTestPanel", u"color: #2C3E50; padding: 4px; font-size: 11px;", None))
        self.progressBar.setStyleSheet(QCoreApplication.translate("EOLTestPanel", u"QProgressBar {\n"
"    border: 2px solid #BDC3C7;\n"
"    border-radius: 6px;\n"
"    text-align: center;\n"
"    font-weight: bold;\n"
"    font-size: 11px;\n"
"}\n"
"QProgressBar::chunk {\n"
"    background-color: #3498DB;\n"
"    border-radius: 4px;\n"
"}", None))
        self.logGroup.setTitle(QCoreApplication.translate("EOLTestPanel", u"Test Log", None))
        self.logGroup.setStyleSheet(QCoreApplication.translate("EOLTestPanel", u"QGroupBox {\n"
"    font-weight: bold;\n"
"    font-size: 12px;\n"
"    border: 2px solid #E8E8E8;\n"
"    border-radius: 8px;\n"
"    margin-top: 1ex;\n"
"    padding-top: 10px;\n"
"}\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 10px;\n"
"    padding: 0 8px 0 8px;\n"
"}", None))
        self.testLogText.setStyleSheet(QCoreApplication.translate("EOLTestPanel", u"QTextEdit {\n"
"    background-color: #FAFAFA;\n"
"    border: 1px solid #E8E8E8;\n"
"    border-radius: 4px;\n"
"    padding: 8px;\n"
"    font-family: 'Consolas', 'Monaco', monospace;\n"
"    font-size: 9px;\n"
"    color: #2C3E50;\n"
"}", None))
    # retranslateUi

