#!/usr/bin/python2 -B
# -*- coding: utf-8 -*-
#
# Webcamod, webcam capture plasmoid.
# Copyright (C) 2011-2012  Gonzalo Exequiel Pedone
#
# Webcamod is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Webcamod is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Webcamod. If not, see <http://www.gnu.org/licenses/>.
#
# Email     : hipersayan DOT x AT gmail DOT com
# Web-Site 1: http://github.com/hipersayanX/Webcamoid
# Web-Site 2: http://kde-apps.org/content/show.php/Webcamoid?content=144796

import sys

from PyQt4 import QtCore, QtGui
from PyKDE4 import kdeui
from v4l2 import v4l2

import v4l2tools
import appenvironment


class WebcamConfig(QtGui.QWidget):
    def __init__(self, parent=None, tools=None):
        QtGui.QWidget.__init__(self)

        self.appEnvironment = appenvironment.AppEnvironment()
        self.setWindowTitle(self.tr('Set Webcam Preferences'))
        self.setWindowIcon(kdeui.KIcon('camera-web'))

        self.tools = v4l2tools.V4L2Tools(self) if tools is None else tools
        self.captureDevices = self.tools.captureDevices()
        self.videoFormats = {}

        self.gridLayout = QtGui.QGridLayout(self)

        lblProcess = QtGui.QLabel(self)
        lblProcess.setText(self.tr('GStreamer executable'))

        self.gridLayout.addWidget(lblProcess, 0, 0, 1, 1)

        self.txtProcess = QtGui.QLineEdit(self)
        self.txtProcess.setText(self.tools.processExecutable())
        self.txtProcess.textChanged.connect(self.tools.setProcessExecutable)
        self.gridLayout.addWidget(self.txtProcess, 0, 1, 1, 1)

        btnProcess = QtGui.QPushButton(self)
        btnProcess.setText('...')
        btnProcess.clicked.connect(self.searchProcessExecutable)
        self.gridLayout.addWidget(btnProcess, 0, 2, 1, 1)

        self.tabWidget = QtGui.QTabWidget(self)

        self.resetting = False

        for captureDevice in self.captureDevices:
            page = QtGui.QWidget()
            gridLayout = QtGui.QGridLayout(page)

            cindex = 0

            lblVideoFormat = QtGui.QLabel(page)
            lblVideoFormat.setText(self.tr('Video Format'))
            gridLayout.addWidget(lblVideoFormat, cindex, 0, 1, 1)

            self.videoFormats[captureDevice[0]] = \
                 self.tools.videoFormats(captureDevice[0])

            wdgVideoFormat = QtGui.QWidget(page)

            wdgVideoFormat.setSizePolicy(QtGui.QSizePolicy.Preferred,
                                         QtGui.QSizePolicy.Maximum)

            hlyVideoFormat = QtGui.QHBoxLayout(wdgVideoFormat)

            cbxVideoFormat = QtGui.QComboBox(wdgVideoFormat)
            cbxVideoFormat.setProperty('deviceName', captureDevice[0])
            cbxVideoFormat.setProperty('controlName', '')
            cbxVideoFormat.setProperty('controlDefaultValue', 0)
            cbxVideoFormat.setProperty('deviceOption', 'videoFormat')

            cbxVideoFormat.addItems(['{}x{} {}'.format(videoFormat[0],
                                     videoFormat[1],
                                     self.tools.fcc2s(videoFormat[2]))
                                     for videoFormat in self.
                                            videoFormats[captureDevice[0]]])

            currentVideoFormat = self.tools.\
                                        currentVideoFormat(captureDevice[0])

            cbxVideoFormat.setCurrentIndex(self.videoFormats[captureDevice[0]].
                                                index(currentVideoFormat))

            cbxVideoFormat.currentIndexChanged.\
                           connect(self.on_combobox_currentIndexChanged)

            hlyVideoFormat.addWidget(cbxVideoFormat)

            hspVideoFormat = QtGui.QSpacerItem(0,
                                               0,
                                               QtGui.QSizePolicy.Expanding,
                                               QtGui.QSizePolicy.Minimum)

            hlyVideoFormat.addItem(hspVideoFormat)

            gridLayout.addWidget(wdgVideoFormat, cindex, 1, 1, 1)

            btnResetDevice = QtGui.QPushButton(page)
            btnResetDevice.setProperty('deviceName', captureDevice[0])
            btnResetDevice.setProperty('controlName', '')
            btnResetDevice.setProperty('deviceOption', 'resetDevice')
            btnResetDevice.setText(self.tr("Reset"))
            btnResetDevice.clicked.connect(self.on_pushButton_clicked)
            gridLayout.addWidget(btnResetDevice, cindex, 2, 1, 1)

            cindex = 1

            for control in self.tools.listControls(captureDevice[0]):
                if control[1] == v4l2.V4L2_CTRL_TYPE_INTEGER or \
                   control[1] == v4l2.V4L2_CTRL_TYPE_INTEGER64:
                    lblControl = QtGui.QLabel(page)
                    lblControl.setText(control[0])
                    gridLayout.addWidget(lblControl, cindex, 0, 1, 1)

                    sldControl = QtGui.QSlider(page)
                    sldControl.setProperty('deviceName', captureDevice[0])
                    sldControl.setProperty('controlName', control[0])
                    sldControl.setProperty('controlDefaultValue', control[5])
                    sldControl.setOrientation(QtCore.Qt.Horizontal)
                    sldControl.setRange(control[2], control[3])
                    sldControl.setSingleStep(control[4])
                    sldControl.setValue(control[6])
                    sldControl.sliderMoved.connect(self.on_slider_sliderMoved)
                    gridLayout.addWidget(sldControl, cindex, 1, 1, 1)

                    spbControl = QtGui.QSpinBox(page)
                    spbControl.setProperty('deviceName', captureDevice[0])
                    spbControl.setProperty('controlName', control[0])
                    spbControl.setProperty('controlDefaultValue', control[5])
                    spbControl.setRange(control[2], control[3])
                    spbControl.setSingleStep(control[4])
                    spbControl.setValue(control[6])

                    spbControl.valueChanged.\
                               connect(self.on_spinbox_valueChanged)

                    gridLayout.addWidget(spbControl, cindex, 2, 1, 1)

                    sldControl.sliderMoved.connect(spbControl.setValue)
                    spbControl.valueChanged.connect(sldControl.setValue)
                elif control[1] == v4l2.V4L2_CTRL_TYPE_BOOLEAN:
                    chkControl = QtGui.QCheckBox(page)
                    chkControl.setProperty('deviceName', captureDevice[0])
                    chkControl.setProperty('controlName', control[0])
                    chkControl.setProperty('controlDefaultValue', control[5])
                    chkControl.setText(control[0])
                    chkControl.setChecked(False if control[6] == 0 else True)
                    chkControl.toggled.connect(self.on_checkbox_toggled)
                    gridLayout.addWidget(chkControl, cindex, 0, 1, 3)
                elif control[1] == v4l2.V4L2_CTRL_TYPE_MENU:
                    lblControl = QtGui.QLabel(page)
                    lblControl.setText(control[0])
                    gridLayout.addWidget(lblControl, cindex, 0, 1, 1)

                    wdgControl = QtGui.QWidget(page)

                    wdgControl.setSizePolicy(QtGui.QSizePolicy.Preferred,
                                             QtGui.QSizePolicy.Maximum)

                    hlyControl = QtGui.QHBoxLayout(wdgControl)

                    cbxControl = QtGui.QComboBox(wdgControl)
                    cbxControl.setProperty('deviceName', captureDevice[0])
                    cbxControl.setProperty('controlName', control[0])
                    cbxControl.setProperty('controlDefaultValue', control[5])
                    cbxControl.addItems(control[7])
                    cbxControl.setCurrentIndex(control[6])

                    cbxControl.currentIndexChanged.\
                               connect(self.on_combobox_currentIndexChanged)

                    hlyControl.addWidget(cbxControl)

                    hspControl = QtGui.QSpacerItem(0,
                                                   0,
                                                   QtGui.QSizePolicy.Expanding,
                                                   QtGui.QSizePolicy.Minimum)

                    hlyControl.addItem(hspControl)

                    gridLayout.addWidget(wdgControl, cindex, 1, 1, 1)
                else:
                    continue

                cindex += 1

            spacerItem = QtGui.QSpacerItem(0,
                                           0,
                                           QtGui.QSizePolicy.Preferred,
                                           QtGui.QSizePolicy.MinimumExpanding)

            self.gridLayout.addItem(spacerItem, cindex, 0, 1, 1)
            self.tabWidget.addTab(page, captureDevice[1])

        self.gridLayout.addWidget(self.tabWidget, 1, 0, 1, 3)
        self.tabWidget.setCurrentIndex(0)

    def resetControls(self, deviceName):
        for children in self.findChildren(QtCore.QObject):
            variantChildrenDeviceName = children.property('deviceName')

            variantChildrenControlDefaultValue = \
                                    children.property('controlDefaultValue')

            if variantChildrenDeviceName.isValid() and \
               variantChildrenControlDefaultValue.isValid():
                childrenDeviceName = str(variantChildrenDeviceName.toString())

                childrenControlDefaultValue = \
                                variantChildrenControlDefaultValue.toInt()[0]

                if childrenDeviceName == deviceName:
                    if type(children) == QtGui.QComboBox:
                        children.setCurrentIndex(childrenControlDefaultValue)
                    elif type(children) == QtGui.QSlider:
                        children.setValue(childrenControlDefaultValue)
                    elif type(children) == QtGui.QSpinBox:
                        children.setValue(childrenControlDefaultValue)
                    elif type(children) == QtGui.QCheckBox:
                        children.setChecked(
                                    False if childrenControlDefaultValue == 0
                                    else True)

    @QtCore.pyqtSlot()
    def on_pushButton_clicked(self):
        control = self.sender()
        deviceName = str(control.property('deviceName').toString())
        controlName = str(control.property('controlName').toString())
        deviceOption = str(control.property('deviceOption').toString())

        if controlName == '':
            if deviceOption == 'resetDevice':
                self.resetting = True
                self.tools.reset(deviceName)
                self.resetControls(deviceName)
                self.resetting = False

    @QtCore.pyqtSlot(int)
    def on_slider_sliderMoved(self, value):
        control = self.sender()
        deviceName = str(control.property('deviceName').toString())
        controlName = str(control.property('controlName').toString())

        if not self.resetting:
            self.tools.setControls(deviceName, {controlName: value})

    @QtCore.pyqtSlot(int)
    def on_spinbox_valueChanged(self, i):
        control = self.sender()
        deviceName = str(control.property('deviceName').toString())
        controlName = str(control.property('controlName').toString())

        if not self.resetting:
            self.tools.setControls(deviceName, {controlName: i})

    @QtCore.pyqtSlot(bool)
    def on_checkbox_toggled(self, checked):
        control = self.sender()
        deviceName = str(control.property('deviceName').toString())
        controlName = str(control.property('controlName').toString())

        if not self.resetting:
            self.tools.setControls(deviceName,
                                   {controlName: 1 if checked else 0})

    @QtCore.pyqtSlot(int)
    def on_combobox_currentIndexChanged(self, index):
        control = self.sender()
        deviceName = str(control.property('deviceName').toString())
        controlName = str(control.property('controlName').toString())
        deviceOption = str(control.property('deviceOption').toString())

        if controlName == '':
            if deviceOption == 'videoFormat' and not self.resetting:
                self.tools.setVideoFormat(deviceName,
                                          self.videoFormats[deviceName][index])
        else:
            self.tools.setControls(deviceName, {controlName: index})

    @QtCore.pyqtSlot()
    def searchProcessExecutable(self):
        saveFileDialog = QtGui.QFileDialog(self,
                                           self.tr('Select GStreamer Executable'),
                                           '/usr/bin/gst-launch-0.10')

        saveFileDialog.setModal(True)
        saveFileDialog.setFileMode(QtGui.QFileDialog.ExistingFile)
        saveFileDialog.setAcceptMode(QtGui.QFileDialog.AcceptOpen)
        saveFileDialog.exec_()

        selected_files = saveFileDialog.selectedFiles()

        if not selected_files.isEmpty():
            self.txtProcess.setText(selected_files[0])

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    webcamConfig = WebcamConfig()
    webcamConfig.show()
    app.exec_()
