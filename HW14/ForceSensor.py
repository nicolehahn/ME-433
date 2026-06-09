import serial
import matplotlib.pyplot as plt
import numpy as np

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
    ax13.set_title('Raw vs Filtered Force Sensor')

    ax24.loglog(frq, abs(Y1), 'black')
    ax24.loglog(frq, abs(Y2), 'r', linewidth=2.0)
    ax24.set_xlabel('Freq (Hz)')
    ax24.set_ylabel('|Y(freq)|')

    handles, labels = ax13.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper right')

    plt.show()

def read_force_sensor_samples(port='COM3', baudrate=115200, timeout=1):
    sample_count = int(input('Enter number of samples to take: '))

    sample_numbers = []
    times = []
    raw_data = []
    filtered_data = []

    with serial.Serial(port, baudrate=baudrate, timeout=timeout) as ser:

        ser.write(f"{sample_count}\n".encode('utf-8'))
        ser.flush()

        while len(sample_numbers) < sample_count:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if not line:
                continue

            parts = line.split()
            if len(parts) < 4:
                continue

            try:
                sample_num = int(parts[0])
                current_time = float(parts[1]) /1e6
                raw_value = float(parts[2])
                filtered_value = float(parts[3])
            except ValueError:
                continue

            sample_numbers.append(sample_num)
            times.append(current_time)
            raw_data.append(raw_value)
            filtered_data.append(filtered_value)

    return sample_numbers, times, raw_data, filtered_data


def plot_raw_data(times, raw_data):
    plt.figure()
    plt.plot(times, raw_data, marker='o')
    plt.xlabel('Time')
    plt.ylabel('Raw Data')
    plt.title('Raw Data vs Time')
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    sample_numbers, times, raw_data, filtered_data = read_force_sensor_samples()
    fft_IIR(times, raw_data, times, filtered_data)
