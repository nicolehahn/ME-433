import csv
import matplotlib.pyplot as plt # for plotting
import numpy as np # for sine function

# function definitions
def fft2(t1, y1, t2, y2):
    Fs = len(t1)/t1[-1] # sample rate

    n = len(y1) # length of the signal
    k = np.arange(n)
    T = n/Fs
    frq = k/T # two sides frequency range
    frq = frq[range(int(n/2))] # one side frequency range
    Y = np.fft.fft(y1)/n # fft computing and normalization
    Y1 = Y[range(int(n/2))]

    n = len(y2) # length of the signal
    k = np.arange(n)
    T = n/Fs
    frq = k/T # two sides frequency range
    frq = frq[range(int(n/2))] # one side frequency range
    Y = np.fft.fft(y2)/n # fft computing and normalization
    Y2 = Y[range(int(n/2))]

    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1)
    ax1.plot(t1,y1,'black')
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Amplitude')
    ax1.set_title('Signal B Raw Data vs Filtered Data (MAF x = ' + str(x) + ')')
    ax2.loglog(frq,abs(Y1),'black') # plotting the fft
    ax2.set_xlabel('Freq (Hz)')
    ax2.set_ylabel('|Y(freq)|')

    ax3.plot(t2,y2,'r')
    ax3.set_xlabel('Time')
    ax3.set_ylabel('Amplitude')
    ax4.loglog(frq,abs(Y2),'r') # plotting the fft
    ax4.set_xlabel('Freq (Hz)')
    ax4.set_ylabel('|Y(freq)|')
    
    plt.show()

def fft_MAF(t1, y1, t2, y2):
    Fs = len(t1)/t1[-1] # sample rate

    n = len(y1) # length of the signal
    k = np.arange(n)
    T = n/Fs
    frq = k/T # two sides frequency range
    frq = frq[range(int(n/2))] # one side frequency range
    Y = np.fft.fft(y1)/n # fft computing and normalization
    Y1 = Y[range(int(n/2))]

    n = len(y2) # length of the signal
    k = np.arange(n)
    T = n/Fs
    frq = k/T # two sides frequency range
    frq = frq[range(int(n/2))] # one side frequency range
    Y = np.fft.fft(y2)/n # fft computing and normalization
    Y2 = Y[range(int(n/2))]

    fig, (ax13, ax24) = plt.subplots(2, 1)

    ax13.plot(t1, y1, 'black', label='Raw data')
    ax13.plot(t2, y2, 'r', label='Filtered data', linewidth=2.0)
    ax13.set_xlabel('Time')
    ax13.set_ylabel('Amplitude')
    ax13.set_title('Signal D Raw Data vs Filtered Data (MAF x = ' + str(x) + ')')

    ax24.loglog(frq, abs(Y1), 'black')
    ax24.loglog(frq, abs(Y2), 'r', linewidth=2.0)
    ax24.set_xlabel('Freq (Hz)')
    ax24.set_ylabel('|Y(freq)|')

    handles, labels = ax13.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper right')

    plt.show()

def fft_IIR(t1, y1, t2, y2):
    Fs = len(t1)/t1[-1] # sample rate

    n = len(y1) # length of the signal
    k = np.arange(n)
    T = n/Fs
    frq = k/T # two sides frequency range
    frq = frq[range(int(n/2))] # one side frequency range
    Y = np.fft.fft(y1)/n # fft computing and normalization
    Y1 = Y[range(int(n/2))]

    n = len(y2) # length of the signal
    k = np.arange(n)
    T = n/Fs
    frq = k/T # two sides frequency range
    frq = frq[range(int(n/2))] # one side frequency range
    Y = np.fft.fft(y2)/n # fft computing and normalization
    Y2 = Y[range(int(n/2))]

    fig, (ax13, ax24) = plt.subplots(2, 1)

    ax13.plot(t1, y1, 'black', label='Raw data')
    ax13.plot(t2, y2, 'r', label='Filtered data', linewidth=2.0)
    ax13.set_xlabel('Time')
    ax13.set_ylabel('Amplitude')
    ax13.set_title('Signal D Raw Data vs Filtered Data (IIR A = ' + str(round(A, 4)) + ', B = ' + str(round(1-A, 4)) + ')')

    ax24.loglog(frq, abs(Y1), 'black')
    ax24.loglog(frq, abs(Y2), 'r', linewidth=2.0)
    ax24.set_xlabel('Freq (Hz)')
    ax24.set_ylabel('|Y(freq)|')

    handles, labels = ax13.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper right')

    plt.show()

def fft_FIR(t1, y1, t2, y2):
    Fs = len(t1)/t1[-1] # sample rate

    n = len(y1) # length of the signal
    k = np.arange(n)
    T = n/Fs
    frq = k/T # two sides frequency range
    frq = frq[range(int(n/2))] # one side frequency range
    Y = np.fft.fft(y1)/n # fft computing and normalization
    Y1 = Y[range(int(n/2))]

    n = len(y2) # length of the signal
    k = np.arange(n)
    T = n/Fs
    frq = k/T # two sides frequency range
    frq = frq[range(int(n/2))] # one side frequency range
    Y = np.fft.fft(y2)/n # fft computing and normalization
    Y2 = Y[range(int(n/2))]

    fig, (ax13, ax24) = plt.subplots(2, 1)

    ax13.plot(t1, y1, 'black', label='Raw data')
    ax13.plot(t2, y2, 'r', label='Filtered data', linewidth=2.0)
    ax13.set_xlabel('Time')
    ax13.set_ylabel('Amplitude')
    ax13.set_title('Signal D Raw Data vs Filtered Data (FIR: 100Hz sampling rate, 1Hz cutoff frequency, 1Hz transition bandwidth, 91 coefficients')

    ax24.loglog(frq, abs(Y1), 'black')
    ax24.loglog(frq, abs(Y2), 'r', linewidth=2.0)
    ax24.set_xlabel('Freq (Hz)')
    ax24.set_ylabel('|Y(freq)|')

    handles, labels = ax13.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper right')

    plt.show()

def MAF(data1, x):
    filtered = []
    for index in range(len(data1)):
        sum = 0
        if index < x: # check if there are enough data points
            for count in range(index):
                sum = sum + data1[index - count]
            average = sum/x
        else:
            for count in range(x):
                sum = sum + data1[index - count]
            average = sum/x
        filtered.append(average)
    return filtered

def IIR(data1, A):
    filtered = []
    average = 0
    for index in range(len(data1)):
        new_average = (average + data1[index])/2

        average = A*new_average + (1 - A)*average
        
        filtered.append(average)
    return filtered

def FIR(data1, h):
    filtered = []
    for index in range(len(data1)):
        num_samples = len(h)
        if index < num_samples: # check if there are enough data points
            samples = [0] * (num_samples - index) # add zeros to replace missing data
            for count in range(index): # add remaining data points to samples
                samples.append(data1[count]) 
        else:
            samples = []
            for count in range(num_samples): # if there are enough data points take the amount needed
                samples.append(data1[index - (num_samples - count)]) 
        average = sum([x * y for x, y in zip(h, samples)]) # multiply h by samples and add them up
        filtered.append(average)
    return filtered

def downsample(data, t, amt):
    new_data = []
    new_t = []
    i = 0
    while i < len(data):
        new_data.append(data[i])
        new_t.append(t[i])
        i = i+amt
    return new_data, new_t

def get_data(file):
    t = [] # column 0
    data1 = [] # column 1
    with open(file) as f:
    # open the csv file
        reader = csv.reader(f)
        for row in reader:
            # read the rows 1 one by one
            t.append(float(row[0])) # leftmost column
            data1.append(float(row[1])) # second column
    return t, data1

# MAF inputs
x = 2000

# IIR inputs
A = 1

# FIR inputs
h = [
    0.001867519746044820,
    0.002275293677911463,
    0.002692845467883248,
    0.003119400211540369,
    0.003554151391578438,
    0.003996262853518041,
    0.004444870878876082,
    0.004899086349965267,
    0.005357997000181999,
    0.005820669743355830,
    0.006286153075466025,
    0.006753479541784039,
    0.007221668262275161,
    0.007689727507889525,
    0.008156657320192493,
    0.008621452166627776,
    0.009083103623574271,
    0.009540603079249766,
    0.009992944448431896,
    0.010439126890909214,
    0.010878157525543523,
    0.011309054131818317,
    0.011730847830767882,
    0.012142585737226980,
    0.012543333575412086,
    0.012932178249941664,
    0.013308230364524597,
    0.013670626680692492,
    0.014018532509122373,
    0.014351144026291085,
    0.014667690509420725,
    0.014967436482914990,
    0.015249683769748768,
    0.015513773441556675,
    0.015759087661469738,
    0.015985051414072162,
    0.016191134117190663,
    0.016376851110586923,
    0.016541765016997088,
    0.016685486971350718,
    0.016807677714403370,
    0.016908048547430839,
    0.016986362145057821,
    0.017042433223728004,
    0.017076129063764694,
    0.017087369883420026,
    0.017076129063764694,
    0.017042433223728004,
    0.016986362145057821,
    0.016908048547430839,
    0.016807677714403370,
    0.016685486971350718,
    0.016541765016997088,
    0.016376851110586923,
    0.016191134117190663,
    0.015985051414072162,
    0.015759087661469738,
    0.015513773441556675,
    0.015249683769748768,
    0.014967436482914990,
    0.014667690509420725,
    0.014351144026291085,
    0.014018532509122373,
    0.013670626680692492,
    0.013308230364524597,
    0.012932178249941664,
    0.012543333575412086,
    0.012142585737226980,
    0.011730847830767882,
    0.011309054131818317,
    0.010878157525543523,
    0.010439126890909214,
    0.009992944448431896,
    0.009540603079249766,
    0.009083103623574271,
    0.008621452166627776,
    0.008156657320192493,
    0.007689727507889525,
    0.007221668262275161,
    0.006753479541784039,
    0.006286153075466025,
    0.005820669743355830,
    0.005357997000181999,
    0.004899086349965267,
    0.004444870878876082,
    0.003996262853518041,
    0.003554151391578438,
    0.003119400211540369,
    0.002692845467883248,
    0.002275293677911463,
    0.001867519746044820,
]

t, data1 = get_data('sigD.csv')

data1, t = downsample(data1, t, 4)

filtered_FIR = FIR(data1, h)


fft_FIR(t, data1, t, filtered_FIR)


    

sampling_rate = len(t)/t[-1]
print("Sampling rate: " + str(int(sampling_rate)) + " samples per second")


