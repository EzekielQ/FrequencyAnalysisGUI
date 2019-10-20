import sys
from PyQt5.Qt import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
import numpy as np

from backendImg import initplot, plot_origin, noise_plot, plott_origin, methodd, errorPlot


class Window1(QMainWindow):
    def __init__(self):
        # 父类的初始化
        super().__init__()

        # 初始化文件读取状态
        self.loadSignalStatus = False
        self.loadNoiseStatus = False
        self.signalFile = ''
        self.noiseFile = ''

        # 初始化信号与噪声参数
        self.snr = 0.0
        self.signal = 0
        self.noise = 0
        self.signalNoise = 0
        self.fs = 0
        self.interFreq = 0

        # UI初始化
        self.initUI()

    # 初始化关于窗口
    def initDialog(self):
        self.aboutDialog = QDialog()
        self.aboutDialog.setWindowTitle('关于')
        self.aboutDialog.setWindowModality(Qt.ApplicationModal)
        aboutLayout = QGridLayout(self.aboutDialog)
        self.aboutDialog.setLayout(aboutLayout)
        aboutLabel1 = QLabel(self)
        labelLine0 = '信号频率检测仿真\n'
        labelLine1 = '实现了:\n1.生成多种不同的信号和噪声\n2.用四种方法检测频率\n3.计算信噪比/频率误差曲线\n4.调节干扰信号的频率\n5.调节Welch法的重叠区域\n版本: 0.0.1\n'
        labelLine2 = '部分功能不完善'
        aboutLabel1.setText(labelLine0 + labelLine1 + labelLine2)
        aboutLayout.addWidget(aboutLabel1, 0, 0, 1, 1)

    # 初始化各种部件
    def initWidgets(self):

        # 绘制没有执行分析时的背景图片
        self.LTopCavans = initplot('Origin Signal')
        self.LBotmCavans = initplot('Received Signal')
        self.RTopCavans = initplot('Unknown')
        self.RBotmCavans = initplot('Unknown')

        # 设置信号选择下拉框
        self.signalComboItems = ['单频信号', '双频信号', '调幅信号', '调相信号', '无']
        self.signalCombo = QComboBox(self)
        self.signalCombo.setStatusTip('修改发射信号')
        self.signalCombo.addItems(self.signalComboItems)
        self.signalCombo.currentIndexChanged.connect(self.signalStatusChange)

        # 设置噪声选择下拉框
        self.noiseComboItems = ['无', '高斯白噪声', '均匀白噪声', '干扰信号']
        self.noiseCombo = QComboBox(self)
        self.noiseCombo.setStatusTip('修改噪声或干扰')
        self.noiseCombo.addItems(self.noiseComboItems)

        # 设置信噪比滑块
        self.snrSlider = QSlider(Qt.Horizontal, self)
        self.snrSlider.setStatusTip('修改信噪比')
        self.snrSlider.setMinimum(0)
        self.snrSlider.setMaximum(200)
        self.snrSlider.setSingleStep(1)
        self.snrSlider.setTickPosition(QSlider.TicksBelow)
        self.snrSlider.setTickInterval(10)
        self.snrSlider.setSliderPosition(100)
        self.snrSlider.valueChanged.connect(self.snrChanger)

        # 设置信噪比滑块显示
        self.snrChangeLabel = QLabel(self)
        self.snrChangeLabel.setText(
            '信噪比: ' + str(0) + 'dB')

        # 设置信噪比显示
        self.snrLabel = QLabel(self)
        self.snrLabel.setText('当前值: ' + str(self.snr) + 'dB')

        # 设置显示按钮
        self.displayButton = QPushButton(self)
        self.displayButton.setText('显示')
        self.displayButton.setStatusTip('显示选择的信号和噪声')
        self.displayButton.clicked.connect(self.display)

        # 设置分析信息显示
        self.infoLabel = QLabel(self)
        self.infoLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.infoLabel.setText('未运行分析')

        # 设置分析方法下拉框
        self.detcMethodComboItems = ['直接变换法', '自相关变换', 'Bartlett法', 'Welch法']
        self.detcMethodCombo = QComboBox(self)
        self.detcMethodCombo.setStatusTip('选择频率检测方式')
        self.detcMethodCombo.addItems(self.detcMethodComboItems)

        # 设置高级分析方法下拉框
        self.advancedComboItems = ['单频错误率分析', '干扰频移分析', 'Welch法重叠分析', '无']
        self.advancedCombo = QComboBox(self)
        self.advancedCombo.setStatusTip('选择高级分析模式')
        self.advancedCombo.addItems(self.advancedComboItems)
        self.advancedCombo.setEnabled(False)
        self.advancedCombo.setCurrentText('无')
        self.advancedCombo.currentTextChanged.connect(self.advancedStatus)

        # 设置额外参数输入框
        self.extraInputLine = QLineEdit(self)
        self.extraInputLine.setStatusTip('为高级分析输入额外参数')
        self.extraInputLine.setEnabled(False)
        self.extraInputLine.setPlaceholderText('额外参数:无')

        # 设置高级分析方法勾选框
        self.advAnalysisCheck = QCheckBox(self)
        self.advAnalysisCheck.setText('开启高级分析')
        self.advAnalysisCheck.toggle()
        self.advAnalysisCheck.setCheckState(False)
        self.advAnalysisCheck.stateChanged.connect(self.advancedStatus)

        # 设置分析按钮
        self.analysisButton = QPushButton(self)
        self.analysisButton.setText('分析')
        self.analysisButton.setStatusTip('开始进行频率分析')
        self.analysisButton.clicked.connect(self.analysis)

    def initUI(self):
        self.resize(1200, 900)  # 设置主窗口大小
        self.setWindowTitle('信号频率检测仿真')  # 设置标题
        self.statusBar().showMessage('加载中')  # 设置状态栏显示
        self.show()  # 显示主窗口

        self.initWidgets()
        self.initDialog()

        # 设置菜单栏

        # 设置加载信号动作
        self.loadSignalAct = QAction('加载信号', self)
        self.loadSignalAct.setShortcut('Ctrl+S')
        self.loadSignalAct.setStatusTip('加载文件中的信号')
        self.loadSignalAct.triggered.connect(self.loadSignal)

        # 设置加载噪声动作
        self.loadNoiseAct = QAction('加载噪声', self)
        self.loadNoiseAct.setShortcut('Ctrl+N')
        self.loadNoiseAct.setStatusTip('加载文件中的噪声或干扰')
        self.loadNoiseAct.triggered.connect(self.loadNoise)

        # 设置关于动作
        self.aboutAct = QAction('关于', self)
        self.aboutAct.setStatusTip('关于此程序的信息')
        self.aboutAct.triggered.connect(self.showAboutDialog)

        # 设置退出动作
        self.exitAct = QAction('退出', self)
        self.exitAct.setShortcut('Ctrl+Q')
        self.exitAct.setStatusTip('关闭当前程序')
        self.exitAct.triggered.connect(qApp.quit)

        # 把动作添加到菜单栏
        self.menuBarTop = self.menuBar()
        self.menuBarTop.addAction(self.loadSignalAct)
        self.menuBarTop.addAction(self.loadNoiseAct)
        self.menuBarTop.addAction(self.aboutAct)
        self.menuBarTop.addAction(self.exitAct)

        mainWidget = QWidget(self)  # 创建主要部件
        self.setCentralWidget(mainWidget)  # 把主要部件设为主窗口中央部件
        self.grid = QGridLayout()  # 创建网格布局
        mainWidget.setLayout(self.grid) #设置主要部件的布局为网格布局
        # mainWidget.setStyleSheet('background-color:white')

        #为网格布局添加子部件
        self.grid.addWidget(self.LTopCavans, 0, 0, 3, 4)
        self.grid.addWidget(self.LBotmCavans, 3, 0, 3, 4)
        self.grid.addWidget(self.RTopCavans, 0, 4, 3, 4)
        self.grid.addWidget(self.RBotmCavans, 3, 4, 3, 4)
        self.grid.addWidget(self.signalCombo, 6, 0, 1, 1)
        self.grid.addWidget(self.noiseCombo, 7, 0, 1, 1)
        self.grid.addWidget(self.snrSlider, 6, 1, 1, 3)
        self.grid.addWidget(self.snrChangeLabel, 7, 1, 1, 1)
        self.grid.addWidget(self.snrLabel, 7, 2, 1, 1)
        self.grid.addWidget(self.displayButton, 7, 3, 1, 1)
        self.grid.addWidget(self.infoLabel, 6, 4, 1, 3)
        self.grid.addWidget(self.detcMethodCombo, 7, 4, 1, 1)
        self.grid.addWidget(self.advancedCombo, 7, 5, 1, 1)
        self.grid.addWidget(self.extraInputLine, 7, 6, 1, 1)
        self.grid.addWidget(self.advAnalysisCheck, 6, 7, 1, 1)
        self.grid.addWidget(self.analysisButton, 7, 7, 1, 1)

        self.statusBar().showMessage('就绪')
        self.update()

    #滑动滑块时显示信噪比
    def snrChanger(self):
        self.snrChangeLabel.setText(
            '信噪比: ' + str(round(self.snrSlider.value() / 10 - 15, 2)) + 'dB')

    #信号为'无'时使显示按钮无效
    def signalStatusChange(self):
        if self.signalCombo.currentText() == '无':
            self.displayButton.setEnabled(False)
            self.snrSlider.setEnabled(False)
            self.snrSlider.setValue(0)
        else:
            self.displayButton.setEnabled(True)
            self.snrSlider.setEnabled(True)

    #勾选高级分析勾选框和选择下拉框时改变UI设定
    def advancedStatus(self):
        if self.advAnalysisCheck.isChecked():
            self.advancedCombo.setEnabled(True)
            self.extraInputLine.setEnabled(True)
            self.loadNoiseAct.setEnabled(False)
            self.loadSignalAct.setEnabled(False)
            if self.advancedCombo.currentIndex() == 0:
                self.extraInputLine.setPlaceholderText('信噪比:begin end step')
                self.detcMethodCombo.setEnabled(True)
            elif self.advancedCombo.currentIndex() == 1:
                self.extraInputLine.setPlaceholderText('干扰信号频率:f')
                self.noiseCombo.setCurrentText('干扰信号')
                self.noiseCombo.setEnabled(False)
                self.detcMethodCombo.setEnabled(True)
            elif self.advancedCombo.currentIndex() == 2:
                self.extraInputLine.setPlaceholderText('窗口重叠因子:n')
                self.detcMethodCombo.setCurrentText('Welch法')
                self.noiseCombo.setEnabled(True)
                self.detcMethodCombo.setEnabled(False)
        else:
            self.advancedCombo.setCurrentText('无')
            self.advancedCombo.setEnabled(False)
            self.extraInputLine.setPlaceholderText('额外参数:无')
            self.extraInputLine.setEnabled(False)
            self.loadNoiseAct.setEnabled(True)
            self.loadSignalAct.setEnabled(True)
            self.noiseCombo.setEnabled(True)
            self.detcMethodCombo.setEnabled(True)

    #读取文件中的信号
    def loadSignal(self):
        self.signalFile = QFileDialog.getOpenFileName(
            self, '选择信号文件', './', '文本文件(*.txt)')
        self.statusBar().showMessage(str(self.signalFile))
        if (not self.loadSignalStatus) and (not self.signalFile[0] == ''):
            self.signal = np.loadtxt(self.signalFile[0])
            self.signalCombo.addItem('加载的信号')
            self.loadSignalStatus = True

    #读取文件中的噪声
    def loadNoise(self):
        self.noiseFile = QFileDialog.getOpenFileName(
            self, '选择噪声文件', './', '文本文件(*.txt)')
        self.statusBar().showMessage(str(self.noiseFile))
        if (not self.loadNoiseStatus) and (not self.noiseFile[0] == ''):
            self.noise = np.loadtxt(self.noiseFile[0])
            self.noiseCombo.addItem('加载的噪声')
            self.loadNoiseStatus = True

    #按下显示按钮时,显示选择的信号,信号频谱,加噪信号
    def display(self):
        if not self.advAnalysisCheck.isChecked():
            self.snr = round(self.snrSlider.value() / 10 - 15, 2)
            self.snrLabel.setText('当前值: ' + str(self.snr) + 'dB')

            LTopCavans, self.signal, self.fs = plot_origin(
                self.signalCombo.currentIndex(), self.signal)
            self.grid.itemAtPosition(0, 0).widget().deleteLater()
            self.grid.addWidget(LTopCavans, 0, 0, 3, 4)

            LBotmCavans, self.signalNoise = noise_plot(self.noiseCombo.currentIndex(
            ), self.snr, self.signal, self.fs, noise_txt=self.noise)
            self.grid.itemAtPosition(3, 0).widget().deleteLater()
            self.grid.addWidget(LBotmCavans, 3, 0, 3, 4)

            RTopCavans = plott_origin(self.signal, self.fs)
            self.grid.itemAtPosition(0, 4).widget().deleteLater()
            self.grid.addWidget(RTopCavans, 0, 4, 3, 4)
        else:
            self.snr = round(self.snrSlider.value() / 10 - 15, 2)
            self.snrLabel.setText('当前值: ' + str(self.snr) + 'dB')

            LTopCavans, self.signal, self.fs = plot_origin(
                self.signalCombo.currentIndex(), self.signal)
            self.grid.itemAtPosition(0, 0).widget().deleteLater()
            self.grid.addWidget(LTopCavans, 0, 0, 3, 4)
            if self.advancedCombo.currentIndex() == 1:
                LBotmCavans, self.signalNoise = noise_plot(self.noiseCombo.currentIndex(
                ), self.snr, self.signal, self.fs, f00=self.interFreq)
            else:
                LBotmCavans, self.signalNoise = noise_plot(self.noiseCombo.currentIndex(
                ), self.snr, self.signal, self.fs, noise_txt=self.noise)
            self.grid.itemAtPosition(3, 0).widget().deleteLater()
            self.grid.addWidget(LBotmCavans, 3, 0, 3, 4)

            RTopCavans = plott_origin(self.signal, self.fs)
            self.grid.itemAtPosition(0, 4).widget().deleteLater()
            self.grid.addWidget(RTopCavans, 0, 4, 3, 4)

    #按下分析时,根据选择的不同,显示不同的图形
    def analysis(self):
        if not self.advAnalysisCheck.isChecked():
            self.display()
            RBotmCavans, text = methodd(
                self.detcMethodCombo.currentIndex(), self.fs, self.signalNoise)
            self.grid.itemAtPosition(3, 4).widget().deleteLater()
            self.grid.addWidget(RBotmCavans, 3, 4, 3, 4)
            self.infoLabel.setText(text)
        elif self.advancedCombo.currentIndex() == 0:
            snrRange = self.extraInputLine.text().split()
            snrRange = [float(x) for x in snrRange]
            if len(snrRange) == 3:
                RBotmCavans, text = errorPlot(
                    self.detcMethodCombo.currentIndex(), snrRange[0], snrRange[1], snrRange[2])
            else:
                RBotmCavans, text = errorPlot(
                    self.detcMethodCombo.currentIndex())
            self.grid.itemAtPosition(3, 4).widget().deleteLater()
            self.grid.addWidget(RBotmCavans, 3, 4, 3, 4)
            self.infoLabel.setText(text)
            self.grid.itemAtPosition(0, 0).widget().deleteLater()
            self.grid.itemAtPosition(3, 0).widget().deleteLater()
            self.grid.itemAtPosition(0, 4).widget().deleteLater()
            self.LTopCavans = initplot('Original Signal')
            self.LBotmCavans = initplot('Received Signal')
            self.RTopCavans = initplot('Unknown')
            self.grid.addWidget(self.LTopCavans, 0, 0, 3, 4)
            self.grid.addWidget(self.LBotmCavans, 3, 0, 3, 4)
            self.grid.addWidget(self.RTopCavans, 0, 4, 3, 4)
        elif self.advancedCombo.currentIndex() == 1:
            x = self.extraInputLine.text()
            if x == '':
                self.interFreq = 10e2
            else:
                self.interFreq = float(x)
            self.display()
            RBotmCavans, text = methodd(
                self.detcMethodCombo.currentIndex(), self.fs, self.signalNoise)
            self.grid.itemAtPosition(3, 4).widget().deleteLater()
            self.grid.addWidget(RBotmCavans, 3, 4, 3, 4)
            self.infoLabel.setText(text)
        elif self.advancedCombo.currentIndex() == 2:
            self.display()
            n = self.extraInputLine.text()
            if n == '':
                n = 8
            elif float(n) >= 127:
                n = 127
            else:
                n = int(round(float(n)))
            RBotmCavans, text = methodd(
                self.detcMethodCombo.currentIndex(), self.fs, self.signalNoise, n)
            self.grid.itemAtPosition(3, 4).widget().deleteLater()
            self.grid.addWidget(RBotmCavans, 3, 4, 3, 4)
            self.infoLabel.setText(text)

    #显示关于窗口
    def showAboutDialog(self):
        self.aboutDialog.show()
        self.aboutDialog.exec()


if __name__ == '__main__':
    app = QApplication(sys.argv) #创建启动APP
    win1 = Window1() #为APP创建窗口
    sys.exit(app.exec()) #退出APP
