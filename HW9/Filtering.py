import csv
import matplotlib.pyplot as plt # for plotting
import numpy as np # for sine function

t = [] # column 0
data1 = [] # column 1

with open('sigA.csv') as f:
    # open the csv file
    reader = csv.reader(f)
    for row in reader:
        # read the rows 1 one by one
        t.append(float(row[0])) # leftmost column
        data1.append(float(row[1])) # second column

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
    # print(average)


plt.figure(1)
plt.plot(t,data1,'b-*')
plt.xlabel('Time [s]')
plt.ylabel('Signal')
plt.title('Signal vs Time')


plt.figure(2)
plt.plot(t,filtered,'r-*')
plt.xlabel('Time [s]')
plt.ylabel('Signal')
plt.title('Signal vs Time')

plt.show()

sampling_rate = len(t)/t[-1]
print("Sampling rate: " + str(int(sampling_rate)) + " samples per second")