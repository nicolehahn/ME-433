import csv
import matplotlib.pyplot as plt # for plotting
import numpy as np # for sine function

def fft2(t1, y1, t2, y2):
    Fs = 10000 # sample rate

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
    ax1.plot(t1,y1,'b')
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Amplitude')
    ax1.set_title('Raw Data vs Filtered Data (MAF)')
    ax2.loglog(frq,abs(Y1),'b') # plotting the fft
    ax2.set_xlabel('Freq (Hz)')
    ax2.set_ylabel('|Y(freq)|')

    ax3.plot(t2,y2,'r')
    ax3.set_xlabel('Time')
    ax3.set_ylabel('Amplitude')
    ax4.loglog(frq,abs(Y2),'r') # plotting the fft
    ax4.set_xlabel('Freq (Hz)')
    ax4.set_ylabel('|Y(freq)|')
    
    plt.show()

def MAF(data1, x):
    x = 1000
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

t, data1 = get_data('sigA.csv')

filtered_MAF = MAF(data1, 5000)


fft2(t, data1, t, filtered_MAF)


    

sampling_rate = len(t)/t[-1]
print("Sampling rate: " + str(int(sampling_rate)) + " samples per second")


