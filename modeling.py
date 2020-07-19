# coding: utf-8

import sys
import math
import numpy as np
from matplotlib import pyplot as plt
from numpy import arange, abs, random
from numpy.fft import fftn
from modeling_ui import *


class MyWin(QtWidgets.QMainWindow):
    signal = []
    string_s = ""
    type_sk = ""

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.leF1.setEnabled(False)
        self.ui.pbMakePlots.setCursor(QtCore.Qt.PointingHandCursor)

        self.ui.pbMakePlots.clicked.connect(self.on_clicked_pbMakePlots)
        self.ui.cbTelegraphy.currentIndexChanged.connect(self.on_changed_cbTelegraphy)
        self.ui.cbIshodnSignal.currentIndexChanged.connect(self.on_changed_cbModeSignal)

    def on_changed_cbTelegraphy(self):
        currIndex = self.ui.cbTelegraphy.currentIndex()
        if currIndex is 0:
            self.ui.leF1.setEnabled(False)
        elif currIndex is 1:
            self.ui.leF1.setEnabled(True)
        elif currIndex is 2:
            self.ui.leF1.setEnabled(False)

    def read_from_text_file(self):
        file_name_ = QtWidgets.QFileDialog.getOpenFileName()[0]
        if file_name_ is not "":
            print("Файл названий классов:", file_name_)
            with open(file_name_, "rt") as f:
                sig = f.read()
                self.signal = []
                self.string_s = ""
                for s in sig:
                    if s is "1" or s in "0":
                        self.string_s = self.string_s + s
                        self.signal.append(s)
                self.ui.lePosledovatelnost.setText(self.string_s)

    def on_changed_cbModeSignal(self):
        currIndex = self.ui.cbIshodnSignal.currentIndex()
        if currIndex is 1:
            self.signal = []
            self.ui.lePosledovatelnost.setText("")
            self.read_from_text_file()
            self.ui.lePosledovatelnost.setEnabled(False)
        else:
            self.ui.lePosledovatelnost.setEnabled(True)

    def on_clicked_pbMakePlots(self):

        V_baud = float(self.ui.leVBaud.text())
        F_d = float(self.ui.leFd.text())
        F_1 = float(self.ui.leF1.text())
        F_2 = float(self.ui.leF2.text())
        Amplitude = float(self.ui.leAmp.text())
        EbNo = float(self.ui.leSigNoise.text())
        radiosignal = []
        noised_rsignal = []

        if self.signal is not []:
            try:
                PowerNoise = 10 * math.log10(int(Amplitude) / int(EbNo))
                count_sps = int(F_d) / int(V_baud)
                ot = int(int(F_d) / (int(V_baud)))
                self.signal = []
                for i in self.ui.lePosledovatelnost.text():
                    self.signal.append(float(i) * Amplitude)
                t = arange(0, float(len(self.signal)), 1)

                print("V= " + str(V_baud))
                print("Fd= " + str(F_d))
                print("F1= " + str(F_1))
                print("F2= " + str(F_2))
                print("Amplitude= " + str(Amplitude))
                print("EbNo= " + str(EbNo))
                print("Power noise= " + str(int(PowerNoise)))
                print("Последовательность: " + self.ui.lePosledovatelnost.text())
                self.string_s = self.ui.lePosledovatelnost.text()
                print("Количество отсчетов на посылку: " + str(int(count_sps)))

                fig = plt.figure()
                ax_1 = fig.add_subplot(3, 2, 1)
                ax_1.grid(True, which='both')
                ax_1.axhline(y=0, color='k')
                string_to_axes = 'Последовательность: ' + self.string_s
                ax_1.set(title=(string_to_axes))
                ax_1.stem(t, self.signal, use_line_collection=True)

                pes = []  # Первичный электрический сигнал
                try:
                    for i, sample in enumerate(self.signal):
                        if float(sample) == Amplitude:
                            for j in range(0, int(ot)):
                                pes.append(Amplitude)
                        if float(sample) == 0:
                            for j in range(0, int(ot)):
                                pes.append(0)
                except Exception as e:
                    print(e)

                print("Отсчетов в сигнале:", len(pes))
                ax_2 = fig.add_subplot(3, 2, 2)
                ax_2.set_xlabel('время, t')
                ax_2.grid(True, which='both')
                ax_2.axhline(y=0, color='k')
                ax_2.set(title='Первичный электрический сигнал')
                t_pes = arange(0, float(len(pes)), 1)
                ax_2.plot(t_pes, pes)

                radiosignal = pes  # Радиосигнал

                self.type_sk = ""
                if self.ui.cbTelegraphy.currentIndex() == 0:
                    self.type_sk = "ask"
                    for i, sample in enumerate(self.signal):
                        for j in range(0, int(ot)):
                            if sample == Amplitude:
                                radiosignal[int(j + i * ot)] = Amplitude * math.sin(2 * math.pi * F_2 * j / F_d)
                            else:
                                radiosignal[int(j + i * ot)] = 0
                elif self.ui.cbTelegraphy.currentIndex() == 1:
                    self.type_sk = "fsk"
                    for i, sample in enumerate(self.signal):
                        for j in range(0, int(ot)):
                            if sample == Amplitude:
                                radiosignal[int(j + i * ot)] = Amplitude * math.sin(2 * math.pi * F_2 * j / F_d)
                            else:
                                radiosignal[int(j + i * ot)] = Amplitude * math.sin(2 * math.pi * F_1 * j / F_d)
                elif self.ui.cbTelegraphy.currentIndex() == 2:
                    self.type_sk = "psk"
                    for i, sample in enumerate(self.signal):
                        for j in range(0, int(ot)):
                            if sample == Amplitude:
                                radiosignal[int(j + i * ot)] = Amplitude * math.sin(2 * math.pi * F_2 * j / F_d)
                            else:
                                radiosignal[int(j + i * ot)] = Amplitude * math.cos(2 * math.pi * F_2 * j / F_d)

                ax_3 = fig.add_subplot(3, 2, 3)
                ax_3.set_xlabel('время, t')
                ax_3.grid(True, which='both')
                ax_3.axhline(y=0, color='k')
                ax_3.set(title='Радиосигнал')
                t_rs = arange(0, float(len(radiosignal)), 1)
                ax_3.plot(t_rs, radiosignal, lw=0.3)

                Y = fftn(radiosignal)
                spectrum = Y[:int(len(Y) / 2)]

                ax_4 = fig.add_subplot(3, 2, 4)
                ax_4.set_xlabel('частота, f')
                ax_4.grid(True, which='both')
                ax_4.axhline(y=0, color='k')
                ax_4.set(title='Спектр сигнала')
                t_spec = arange(0, float(len(spectrum)) * 4, 4)
                ax_4.plot(t_spec, abs(spectrum), lw=0.7)

                noised_rsignal = []  # Зашумленный сигнал

                mode_noise = self.ui.comboBox.currentIndex()
                if mode_noise is 0:
                    noise = np.random.normal(0, PowerNoise, int(len(radiosignal)))
                    for i in range(0, int(len(radiosignal))):
                        sample_ = radiosignal[i] + noise[i]
                        noised_rsignal.append(sample_)
                elif mode_noise is 1:
                    rand_index = np.random.randint(len(radiosignal))
                    radiosignal[rand_index - 2] = Amplitude * 2
                    radiosignal[rand_index - 1] = Amplitude * 3
                    radiosignal[rand_index] = Amplitude * 4
                    radiosignal[rand_index + 1] = Amplitude * 3
                    radiosignal[rand_index + 2] = Amplitude * 2
                    noised_rsignal = radiosignal
                elif mode_noise is 2:
                    rand_frequency = np.random.randint(int(F_d / 2))
                    for i in range(len(radiosignal)):
                        noised_rsignal.append(
                            radiosignal[i] + (Amplitude * math.sin(2 * math.pi * rand_frequency * i / F_d)))

                ax_5 = fig.add_subplot(3, 2, 5)
                ax_5.set_xlabel('время, t')
                ax_5.grid(True, which='both')
                ax_5.axhline(y=0, color='k')
                ax_5.set(title='Зашумленный сигнал')
                t_rs = arange(0, float(len(noised_rsignal)), 1)
                ax_5.plot(t_rs, noised_rsignal, lw=0.3)

                Y_noise = fftn(noised_rsignal)
                noised_spectrum = Y_noise[:int(len(Y_noise) / 2)]
                ax_4 = fig.add_subplot(3, 2, 6)
                ax_4.set_xlabel('частота, f')
                ax_4.grid(True, which='both')
                ax_4.axhline(y=0, color='k')
                ax_4.set(title='Спектр сигнала')
                t_spec = arange(0, float(len(noised_spectrum)) * 4, 4)
                ax_4.plot(t_spec, abs(noised_spectrum), lw=0.7)
                
                try:

                    fname_signal = "signal_" + self.type_sk + ".pcm"
                    fname_noised_signal = "noised_signal_" + self.type_sk + ".pcm"
                    mmm = 1000  # множитель

                    ###
                    with open(fname_signal, "wt") as f:
                        f.write("")
                    with open(fname_signal, "ab") as fb:
                        for sample in radiosignal:
                            fb.write(np.short(sample * mmm))

                    ###
                    with open(fname_noised_signal, "wt") as nf:
                        nf.write("")
                    with open(fname_noised_signal, "ab") as fb:
                        for sample in noised_rsignal:
                            fb.write(np.short(sample * mmm))

                except Exception as e:
                    print(e)


                plt.show()
            except Exception as e:
                print(e)



def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = MyWin()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
