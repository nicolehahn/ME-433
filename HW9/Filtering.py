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
A = 0.004

t, data1 = get_data('sigD.csv')

filtered_IIR = IIR(data1, A)


fft_IIR(t, data1, t, filtered_IIR)


    

sampling_rate = len(t)/t[-1]
print("Sampling rate: " + str(int(sampling_rate)) + " samples per second")


