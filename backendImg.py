import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import matplotlib
matplotlib.use('Qt5Agg')


def initplot(imgtitle='图像'):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.grid(color='c', linestyle='-')
    ax.set(title=imgtitle)
    return FigureCanvasQTAgg(fig)


def plot_origin(switch, signal_txt=0):
    points = 1024  # 采样点数
    if(switch == 0):
        f0 = f1 = 0
        f0 = 15e3  # 定义信号的频率
        fs = 4*f0
        nTs = np.arange(points)/fs
        signal = np.sin(2*np.pi*f0*nTs)+np.sin(2*np.pi*f1*nTs)  # 单频率信号
    elif(switch == 1):
        f0 = f1 = 0
        f0 = 150e3  # 定义信号的频率
        f1 = 130e3
        fs = 4*f0
        nTs = np.arange(points)/fs
        signal = np.sin(2*np.pi*f0*nTs)+np.sin(2*np.pi*f1*nTs)  # 双频率信号相加
    elif(switch == 2):
        f0 = f1 = 0
        f0 = 150e3  # 定义信号的频率
        f1 = 10e3
        fs = 4*f0
        nTs = np.arange(points)/fs
        signal = np.sin(2*np.pi*f0*nTs)*np.sin(2*np.pi*f1*nTs)  # 双频率信号相乘
    elif(switch == 3):
        f0 = f1 = 0
        f0 = 150e3  # 定义信号的频率
        f1 = 60e3
        fs = 4*f0
        nTs = np.arange(points)/fs
        signal = np.sin(2*np.pi*(f0*nTs+np.sin(2*np.pi*f1*nTs)))  # 双频率信号相位调制
    elif(switch == 5):
        points = len(signal_txt[:, 1])
        signal = signal_txt[:, 1]
        nTs = signal_txt[:, 0]
        fs = (points - 1) / nTs[-1]

    x = 1000 * nTs[0: points // 10]  # 原始信号绘图
    y = signal[0:points//10]
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.grid(color='gray', linestyle='-')
    ax.set(title='Original Signal')
    ax.set_xlabel('t/ms')
    ax.set_ylabel('V')
    ax.plot(x, y)
    return FigureCanvasQTAgg(fig), signal, fs


def noise_plot(switch2, snr, signal, fs, f00=10e2, noise_txt=0):  # 添加噪声和干扰
    points = len(signal)
    nTs = np.arange(points) / fs
    if switch2 == 0:
        noise = nTs * 0
    elif (switch2 == 1):
        noise = 10 ** (-snr / 20) * np.random.randn(1, points)  # 高斯白噪声
    elif (switch2 == 2):
        noise = 10 ** (-snr / 20) * 2 * np.random.rand(1, points) - 1  # 均匀噪声
    elif (switch2 == 3):
        noise = 10 ** (-snr / 20) * np.sin(2 * np.pi * f00 * nTs)  # 同频干扰
    elif(switch2 == 4):
        noise = 10 ** (-snr / 20) * noise_txt  # 读取文件中噪声

    signal_noise = signal + noise  # 噪声信号叠加到信源信号
    signal_noise = np.squeeze(signal_noise)  # 去掉多余维度
    x = 1000 * nTs[0: points // 10]  # 加噪信号绘图
    y = signal_noise[0:points//10]
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.grid(color='gray', linestyle='-')
    ax.set(title='Received Signal')
    ax.set_xlabel('t/ms')
    ax.set_ylabel('V')
    ax.plot(x, y)

    return FigureCanvasQTAgg(fig), signal_noise


def plott(x, y):  # 根据各种方法产生的x，y绘制频谱图
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.grid(color='gray', linestyle='-')
    ax.set(title='Received Frequency Spectrum')
    ax.set_xlabel('KHz')
    ax.set_ylabel('p(k)/dB')
    ax.plot(x, y)
    return FigureCanvasQTAgg(fig)


def plott_origin(signal, fs):  # 绘制原信号频谱图
    points = len(signal)  # 获取信号长度
    Delta_f = np.arange(points)*fs/points
    fft_signal = np.fft.fft(signal)  # 求fft
    squar_fft_signal = fft_signal*np.conj(fft_signal)  # 取幅值平方
    Periodogram_method_Spectrum = squar_fft_signal/points  # 估计功率谱
    max_Periodogram_method_Spectrum = np.max(
        Periodogram_method_Spectrum)  # 求行最大值
    Periodogram_method_Spectrum = Periodogram_method_Spectrum / \
        max_Periodogram_method_Spectrum  # 归一化
    log10_Periodogram_method_Spectrum = 10 * \
        np.log10(Periodogram_method_Spectrum)
    x = Delta_f[0:(points//2)-1:1]/1000
    y = log10_Periodogram_method_Spectrum[0:(points//2)-1:1]
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.grid(color='gray', linestyle='-')
    ax.set(title='Original Frequency Spectrum')
    ax.set_xlabel('KHz')
    ax.set_ylabel('p(k)/dB')
    ax.plot(x, y)
    return FigureCanvasQTAgg(fig)


def method(switch3):  # 方法选择函数，返回方法函数
    # 直接傅里叶法进行频谱估计，首先计算截断的信号的离散傅里叶变换，然后取模值的平方并归一化，最后取以10为底的对数然后乘以10，绘制归一化后的功率谱图。
    def plot1(signal_noise, fs):
        points = len(signal_noise)  # 获取信号长度
        Delta_f = np.arange(points)*fs/points  # 每个采样点位置
        fft_signal_noise = np.fft.fft(signal_noise)  # 求fft
        squar_fft_signal_noise = fft_signal_noise * \
            np.conj(fft_signal_noise)  # 取幅值平方
        Periodogram_method_Spectrum = squar_fft_signal_noise/points  # 估计功率谱
        max_Periodogram_method_Spectrum = np.max(
            Periodogram_method_Spectrum)  # 求行最大值
        Periodogram_method_Spectrum = Periodogram_method_Spectrum / \
            max_Periodogram_method_Spectrum  # 归一化
        log10_Periodogram_method_Spectrum = 10 * \
            np.log10(Periodogram_method_Spectrum)  # 取对数乘10
        x = Delta_f[0:(points//2)-1:1]/1000  # 输出x，y
        y = log10_Periodogram_method_Spectrum[0:(points//2)-1:1]

        med = 'fft'  # 输出字符串
        return med, x, y

    def plot2(signal_noise, fs):  # BT法进行频谱估计，首先计算截断的信号的离散傅里叶变换，然后取模值的平方并归一化，最后取以10为底的对数然后乘以10，绘制归一化后的功率谱图。
        points = len(signal_noise)
        autocorr_signal_noise = np.correlate(
            signal_noise, signal_noise, 'full')  # 求线性自相关
        fft_autocorr_signal_noise = np.fft.fft(
            autocorr_signal_noise)  # 求自相关的fft
        abs_fft_autocorr_signal_noise = np.abs(
            fft_autocorr_signal_noise)/(2*points-1)  # 求幅值
        max_abs_fft_autocorr_signal_noise = np.max(
            abs_fft_autocorr_signal_noise)
        abs_fft_autocorr_signal_noise = abs_fft_autocorr_signal_noise / \
            max_abs_fft_autocorr_signal_noise
        log10_abs_fft_autocorr_signal_noise = 10 * \
            np.log10(abs_fft_autocorr_signal_noise)
        Delta_f1 = np.arange(2*points-2)*fs/(2*points-1)

        x = Delta_f1[0:points]/1000
        y = log10_abs_fft_autocorr_signal_noise[0:points]

        med = 'BT'
        return med, x, y

    def plot3(signal_noise, fs):  # Bartlett法进行频谱估计，首先将截断的信号分成等长的不重叠的若干段，然后计算每一段的离散傅里叶变换，并取模值的平方，然后对应点求和。
        # 所有段计算并求和完成后，归一化处理，并取以10为底的对数然后乘以10，绘制归一化后的功率谱图。
        points = len(signal_noise)
        M = 128  # 每段的点数
        L = points//M  # 段数
        Bartlett_Spectrum = np.zeros((1, points))
        for i in range(1, L+1):
            temp_signal = np.zeros((1, points))
            temp_signal = np.squeeze(temp_signal)
            start_point = (i-1)*M
            temp_signal[0:M] = signal_noise[(
                start_point):(start_point+M)]  # 截取第i段信号
            fft_temp_signal = np.fft.fft(temp_signal)
            squar_fft_temp_signal = fft_temp_signal * \
                np.conj(fft_temp_signal)  # 求当前段的功率谱
            Bartlett_Spectrum = Bartlett_Spectrum + squar_fft_temp_signal  # 累加
        max_Bartlett_Spectrum = np.max(Bartlett_Spectrum)
        Bartlett_Spectrum = Bartlett_Spectrum/max_Bartlett_Spectrum  # 归一化
        log10_Bartlett_Spectrum = 10*np.log10(Bartlett_Spectrum)  # 求对数

        Delta_f2 = np.arange(points)*fs/points
        x = Delta_f2[0:points//2]/1000
        log10_Bartlett_Spectrum = np.squeeze(log10_Bartlett_Spectrum)
        y = log10_Bartlett_Spectrum[0:points//2]

        med = 'Bartlett'
        return med, x, y

    def plot4(signal_noise, fs, n=8):  # Welch法进行频谱估计，首先将截断的信号分成等长的有重叠的若干段，然后计算每一段的离散傅里叶变换，并取模值的平方，然后对应点求和。
        # 所有段计算并求和完成后，归一化处理，并取以10为底的对数然后乘以10，绘制归一化后的功率谱图。
        points = len(signal_noise)
        M = 128  # 每段的点数
        Overlap = M-n  # 每段间隔
        L = (points - Overlap)//(M-Overlap)  # 段数

        Welch_Spectrum = np.zeros((1, points))
        for i in range(1, L+1):
            temp_signal = np.zeros((1, points))
            temp_signal = np.squeeze(temp_signal)
            start_point = (i-1)*(M-Overlap)
            temp_signal[0:M] = signal_noise[(
                start_point):(start_point+M)]  # 截取第i段信号
            fft_temp_signal = np.fft.fft(temp_signal)
            squar_fft_temp_signal = fft_temp_signal * \
                np.conj(fft_temp_signal)  # 求当前段的功率谱
            Welch_Spectrum = Welch_Spectrum + squar_fft_temp_signal  # 累加
        max_Welch_Spectrum = np.max(Welch_Spectrum)
        Welch_Spectrum = Welch_Spectrum/max_Welch_Spectrum  # 归一化
        log10_Welch_Spectrum = 10*np.log10(Welch_Spectrum)  # 求对数

        Delta_f3 = np.arange(points)*fs/points
        x = Delta_f3[0:points//2]/1000
        log10_Welch_Spectrum = np.squeeze(log10_Welch_Spectrum)
        y = log10_Welch_Spectrum[0:points//2]

        med = 'Welch'
        return med, x, y
    if (switch3 == 0):  # 根据switch3选择输出方法函数
        return plot1
    elif (switch3 == 1):
        return plot2
    elif (switch3 == 2):
        return plot3
    elif (switch3 == 3):
        return plot4


def methodd(switch3, fs, signal_noise, n=8):  # 根据switch3选择方法
    a = method(switch3)
    if(switch3 == 3):
        med, x, y = a(signal_noise, fs, n)
        fig = plott(x, y)
        return fig, med  # 根据方法输入相应变量输出频谱图和方法字符串

    else:
        med, x, y = a(signal_noise, fs)
        fig = plott(x, y)
        return fig, med


def errorPlot(switch3, begin=-20, end=0, step=0.2):  # 绘制不同信噪比下的估计误差
    snrs = np.arange(begin, end, step)
    f0 = f1 = 0
    f0 = 15e3  # 定义信号的频率
    fs = 4*f0
    points = 1024
    nTs = np.arange(points)/fs
    signal = np.sin(2*np.pi*f0*nTs)+np.sin(2*np.pi*f1*nTs)
    errors = []
    for snr in snrs:
        errs = []
        for seed in range(100):  # 使用不同的随机数种子进行多次循环
            np.random.seed(seed)
            signal_noise = signal + \
                10**(-snr/20)*np.random.randn(1, points)  # 添加噪声后信号
            signal_noise = np.squeeze(signal_noise)           # #去掉多余维度
            func = method(switch3)
            _, x, y = func(signal_noise, fs)  # 使用直接法的算法
            maxy = np.max(y)  # 计算误差
            pos = x[y == maxy]
            poss = pos[0]
            err = abs(poss*1000-f0)/f0
            errs = errs+[err]
        error = np.average(errs)
        errors = errors+[error]
    x = snrs
    y = errors
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.grid(color='gray', linestyle='-')
    ax.set(title='ERR/SNR Curve')
    ax.set_xlabel('snr/dB')
    ax.set_ylabel('error')
    ax.plot(x, y)
    text = 'ERR/SNR Curve'
    return FigureCanvasQTAgg(fig), text
