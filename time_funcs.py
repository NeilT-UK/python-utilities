import time
import math

version = '1.0.1 2016 Dec 31'

""" utility functions for working with python time """

def seconds_to_round_time(start_time=None, secs=1):
    """ return the number of seconds to wait to get to the next
    even time, rounded up from the start
    secs = 10 for 10 seconds boundaries, = 7200 for 2 hour boundaries
    secs is intended to subdivide the length of a day
    The results will look odd if it doesn't"""

    if start_time==None:
        start_time = time.time()

    st = list(time.localtime(start_time))
    st[3:6] = (0,0,0) # set hours, mins, secs entries to 0
    sec_zero = time.mktime(tuple(st))

    periods = math.ceil((start_time-sec_zero)/secs)
    ft = sec_zero + periods*secs

    return ft-start_time


if __name__=='__main__':
    for i in range(3):
        print('waiting for next 5 second boundary')
        sw = seconds_to_round_time(secs=10)
        time.sleep(sw)
        for j in range(7):
            print(time.localtime())
            time.sleep(0.2)
        
    
