import math

def cab (a, b):
    return int(math.ceil(a/float(b)))

if __name__ == "__main__":
    IC = 8
    OC = 8
    N = 8
    M = 8
    imax = cab(IC, N) + N - 1
    jmax = cab(OC, M)
    for i in range(imax):
        for ii in range(N):
            print '{:<8}'.format((i-ii)*N + i),
        print
