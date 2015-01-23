# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qgsfieldcalculatorbase.ui'
#
# Created: Tue Dec  9 18:51:20 2014
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_QgsFieldCalculatorBase(object):
    def setupUi(self, QgsFieldCalculatorBase):
        QgsFieldCalculatorBase.setObjectName(_fromUtf8("QgsFieldCalculatorBase"))
        QgsFieldCalculatorBase.resize(681, 624)
        self.gridLayout = QtGui.QGridLayout(QgsFieldCalculatorBase)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.mUpdateExistingGroupBox = QtGui.QGroupBox(QgsFieldCalculatorBase)
        self.mUpdateExistingGroupBox.setFlat(True)
        self.mUpdateExistingGroupBox.setCheckable(True)
        self.mUpdateExistingGroupBox.setChecked(False)
        self.mUpdateExistingGroupBox.setObjectName(_fromUtf8("mUpdateExistingGroupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.mUpdateExistingGroupBox)
        self.verticalLayout.setContentsMargins(3, 9, 3, 0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.mExistingFieldComboBox = QtGui.QComboBox(self.mUpdateExistingGroupBox)
        self.mExistingFieldComboBox.setObjectName(_fromUtf8("mExistingFieldComboBox"))
        self.verticalLayout.addWidget(self.mExistingFieldComboBox)
        self.gridLayout.addWidget(self.mUpdateExistingGroupBox, 0, 1, 1, 1)
        self.widget = QtGui.QWidget(QgsFieldCalculatorBase)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.gridLayout_2 = QtGui.QGridLayout(self.widget)
        self.gridLayout_2.setMargin(0)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.mInfoIcon = QtGui.QLabel(self.widget)
        self.mInfoIcon.setMinimumSize(QtCore.QSize(64, 64))
        self.mInfoIcon.setMaximumSize(QtCore.QSize(64, 64))
        self.mInfoIcon.setText(_fromUtf8(""))
        self.mInfoIcon.setObjectName(_fromUtf8("mInfoIcon"))
        self.gridLayout_2.addWidget(self.mInfoIcon, 0, 0, 1, 1)
        #self.mOnlyVirtualFieldsInfoLabel = QtGui.QLabel(self.widget)
        #self.mOnlyVirtualFieldsInfoLabel.setWordWrap(True)
        #self.mOnlyVirtualFieldsInfoLabel.setObjectName(_fromUtf8("mOnlyVirtualFieldsInfoLabel"))
        #self.gridLayout_2.addWidget(self.mOnlyVirtualFieldsInfoLabel, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.widget, 2, 0, 1, 2)
        self.builder = gui.QgsExpressionBuilderWidget(QgsFieldCalculatorBase)
        self.builder.setAutoFillBackground(False)
        self.builder.setObjectName(_fromUtf8("builder"))
        self.gridLayout.addWidget(self.builder, 1, 0, 1, 2)
        self.mButtonBox = QtGui.QDialogButtonBox(QgsFieldCalculatorBase)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mButtonBox.sizePolicy().hasHeightForWidth())
        self.mButtonBox.setSizePolicy(sizePolicy)
        self.mButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.mButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Help|QtGui.QDialogButtonBox.Ok)
        self.mButtonBox.setObjectName(_fromUtf8("mButtonBox"))
        self.gridLayout.addWidget(self.mButtonBox, 6, 0, 1, 2)
        self.mNewFieldGroupBox = QtGui.QGroupBox(QgsFieldCalculatorBase)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mNewFieldGroupBox.sizePolicy().hasHeightForWidth())
        self.mNewFieldGroupBox.setSizePolicy(sizePolicy)
        self.mNewFieldGroupBox.setFlat(True)
        self.mNewFieldGroupBox.setCheckable(True)
        self.mNewFieldGroupBox.setChecked(True)
        self.mNewFieldGroupBox.setObjectName(_fromUtf8("mNewFieldGroupBox"))
        self.gridlayout = QtGui.QGridLayout(self.mNewFieldGroupBox)
        self.gridlayout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.gridlayout.setContentsMargins(3, 9, 3, 0)
        self.gridlayout.setVerticalSpacing(3)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.mOutputFieldPrecisionSpinBox = QtGui.QSpinBox(self.mNewFieldGroupBox)
        self.mOutputFieldPrecisionSpinBox.setProperty("value", 2)
        self.mOutputFieldPrecisionSpinBox.setObjectName(_fromUtf8("mOutputFieldPrecisionSpinBox"))
        self.gridlayout.addWidget(self.mOutputFieldPrecisionSpinBox, 5, 3, 1, 1)
        self.mFieldNameLabel = QtGui.QLabel(self.mNewFieldGroupBox)
        self.mFieldNameLabel.setObjectName(_fromUtf8("mFieldNameLabel"))
        self.gridlayout.addWidget(self.mFieldNameLabel, 3, 0, 1, 1)
        self.mOutputFieldWidthLabel = QtGui.QLabel(self.mNewFieldGroupBox)
        self.mOutputFieldWidthLabel.setObjectName(_fromUtf8("mOutputFieldWidthLabel"))
        self.gridlayout.addWidget(self.mOutputFieldWidthLabel, 5, 0, 1, 1)
        self.mOutputFieldTypeComboBox = QtGui.QComboBox(self.mNewFieldGroupBox)
        self.mOutputFieldTypeComboBox.setObjectName(_fromUtf8("mOutputFieldTypeComboBox"))
        self.gridlayout.addWidget(self.mOutputFieldTypeComboBox, 4, 1, 1, 3)
        self.mOutputFieldWidthSpinBox = QtGui.QSpinBox(self.mNewFieldGroupBox)
        self.mOutputFieldWidthSpinBox.setMinimum(0)
        self.mOutputFieldWidthSpinBox.setProperty("value", 15)
        self.mOutputFieldWidthSpinBox.setObjectName(_fromUtf8("mOutputFieldWidthSpinBox"))
        self.gridlayout.addWidget(self.mOutputFieldWidthSpinBox, 5, 1, 1, 1)
        self.mOutputFieldNameLineEdit = QtGui.QLineEdit(self.mNewFieldGroupBox)
        self.mOutputFieldNameLineEdit.setObjectName(_fromUtf8("mOutputFieldNameLineEdit"))
        self.gridlayout.addWidget(self.mOutputFieldNameLineEdit, 3, 1, 1, 3)
        self.mOutputFieldTypeLabel = QtGui.QLabel(self.mNewFieldGroupBox)
        self.mOutputFieldTypeLabel.setObjectName(_fromUtf8("mOutputFieldTypeLabel"))
        self.gridlayout.addWidget(self.mOutputFieldTypeLabel, 4, 0, 1, 1)
        self.mOutputFieldPrecisionLabel = QtGui.QLabel(self.mNewFieldGroupBox)
        self.mOutputFieldPrecisionLabel.setObjectName(_fromUtf8("mOutputFieldPrecisionLabel"))
        self.gridlayout.addWidget(self.mOutputFieldPrecisionLabel, 5, 2, 1, 1)
        #self.mCreateVirtualFieldCheckbox = QtGui.QCheckBox(self.mNewFieldGroupBox)
        #self.mCreateVirtualFieldCheckbox.setObjectName(_fromUtf8("mCreateVirtualFieldCheckbox"))
        #self.gridlayout.addWidget(self.mCreateVirtualFieldCheckbox, 2, 0, 1, 4)
        self.gridLayout.addWidget(self.mNewFieldGroupBox, 0, 0, 1, 1)
        self.mFieldNameLabel.setBuddy(self.mOutputFieldNameLineEdit)
        self.mOutputFieldWidthLabel.setBuddy(self.mOutputFieldWidthSpinBox)
        self.mOutputFieldTypeLabel.setBuddy(self.mOutputFieldTypeComboBox)
        self.mOutputFieldPrecisionLabel.setBuddy(self.mOutputFieldPrecisionSpinBox)

        self.retranslateUi(QgsFieldCalculatorBase)
        QtCore.QObject.connect(self.mButtonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), QgsFieldCalculatorBase.accept)
        QtCore.QObject.connect(self.mButtonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), QgsFieldCalculatorBase.reject)
        QtCore.QMetaObject.connectSlotsByName(QgsFieldCalculatorBase)
        QgsFieldCalculatorBase.setTabOrder(self.mOutputFieldNameLineEdit, self.mOutputFieldTypeComboBox)
        QgsFieldCalculatorBase.setTabOrder(self.mOutputFieldTypeComboBox, self.mOutputFieldWidthSpinBox)
        QgsFieldCalculatorBase.setTabOrder(self.mOutputFieldWidthSpinBox, self.mOutputFieldPrecisionSpinBox)
        QgsFieldCalculatorBase.setTabOrder(self.mOutputFieldPrecisionSpinBox, self.mButtonBox)

    def retranslateUi(self, QgsFieldCalculatorBase):
        QgsFieldCalculatorBase.setWindowTitle(_translate("QgsFieldCalculatorBase", "Field calculator", None))
        self.mUpdateExistingGroupBox.setTitle(_translate("QgsFieldCalculatorBase", "Update existing field", None))
        #self.mOnlyVirtualFieldsInfoLabel.setText(_translate("QgsFieldCalculatorBase", "This layer does not support adding new provider fields. You can only add virtual fields.", None))
        self.mNewFieldGroupBox.setTitle(_translate("QgsFieldCalculatorBase", "Create a new field", None))
        self.mFieldNameLabel.setText(_translate("QgsFieldCalculatorBase", "Output field name", None))
        self.mOutputFieldWidthLabel.setText(_translate("QgsFieldCalculatorBase", "Output field width", None))
        self.mOutputFieldWidthSpinBox.setToolTip(_translate("QgsFieldCalculatorBase", "Width of complete output. For example 123,456 means 6 as field width.", None))
        self.mOutputFieldTypeLabel.setText(_translate("QgsFieldCalculatorBase", "Output field type", None))
        self.mOutputFieldPrecisionLabel.setText(_translate("QgsFieldCalculatorBase", "Precision", None))
        #self.mCreateVirtualFieldCheckbox.setToolTip(_translate("QgsFieldCalculatorBase", "<p>A virtual field will be recalculated every time it is used. Its definition will be saved in the project file. It will not be saved in the dataprovider and therefore its values not be available in other software.</p>", None))
        #self.mCreateVirtualFieldCheckbox.setText(_translate("QgsFieldCalculatorBase", "Create virtual field", None))

from qgis import gui
