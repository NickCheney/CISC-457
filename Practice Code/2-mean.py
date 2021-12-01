import random

def two_mean(hist,e,maxI):
    Tp = random.randint(0,maxI)
    T = maxI*2
    while abs(T - Tp) > e:
        T = Tp
        np1 = 0
        sum1 = 0
        i = 0
        while i < T:
            np1 += hist[i]
            sum1 += hist[i] * i
            i += 1
        mean1 = sum1 / np1
        np2 = 0
        sum2 = 0
        while i < len(hist):
            np2 += hist[i]
            sum2 += hist[i] * i
            i += 1
        mean2 = sum2 / np2
        Tp = (mean1 + mean2) / 2
    return Tp

h = [i+1 for i in range(256)]

def k_means(k,hist,e,maxI):
    mean1 = 0
    mean2 = 255
    Tp = 127.5
    T = maxI*2
    while abs(T - Tp) > e:
        T = Tp
        np1 = 0
        sum1 = 0
        i = 0
        while abs(mean1 - i) < abs(mean2 - i):
            np1 += hist[i]
            sum1 += hist[i] * i
            i += 1
        mean1 = sum1 / np1
        np2 = 0
        sum2 = 0
        while i < len(hist):
            np2 += hist[i]
            sum2 += hist[i] * i
            i += 1
        mean2 = sum2 / np2
        Tp = (mean1 + mean2) / 2
    return Tp

print(k_means(2,h,0.01,255))
