""" export qXXX quantiser functions, and general make_quant function

use function closures to return the following pre-defined qXXX functions
qE3 to qE192, the standard resistor ranges
qE2  [1, 3, 10]
qE5  [1, 1.6, 2.5, 4, 6.3, 10]
qE10 [1, 1.25, 1.6, 2, 2.5, 3.2, 4, 5, 6.3, 8, 10]

return a function that quantises according to the tuple basis
make_quant(basis)"""

"""
Copyright (c) <2016>, <Neil Thomas>, <NeilT-UK>, <dc_fm@hotmail.com>
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer. 
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those
of the authors and should not be interpreted as representing official policies, 
either expressed or implied, of the FreeBSD Project.
"""

# there are several different ways this function may be approached
# this uses closures (because I could, and wanted to try it)
# alternatively I could make a class with a __call__ method
# or simply create functions manually that do it
# not sure which is the best

version = '1.0     December 2016'

import math

def make_quant(basis):
    """ return the quant function, preconfigured with the basis

    basis starts with a 1, is monotonically increasing,
    it defines a geometrically extendable range with a ratio of the last/first numbers    
    
    >>> qE12(1.6)
    1.5

    >>> qE12(1.6,1)
    1.8

    >>> qE12(8.3, offset=4)
    18.0
    
    >>> qE12(17)
    18.0
    
    >>> '{:.4f}'.format(qE12(0.17))
    '0.1800'


    """
    def quant(x, nearest=0, offset=0):
        """ Quantise x

        nearest = 0 (default) return the geometrically nearest number
        nearest = -1          return the lower number (floor)
        nearest = 1           return the higher number (ceil)
        offset = 0 (default)  return the number as is
        offset = n            return the nth higher or lower quantisation step"""

        # sanitise the input args (slightly, should I float() it?)
        x_test = abs(x)
        if x_test<1e-100:  # or whatever small test number
            return 0
        if x<0:
            sign = -1
        else:
            sign = 1

        # get the basis range 
        base0 = basis[0]
        base1 = basis[-1]
        lbm1 = len(basis)-1

        # bring our test number into the basis range, exp is the range power required
        exp = math.floor(math.log(x_test)/math.log(base1))
        x_test *= base1**(-exp)

        # binary search for the upper and lower bounds around ranged x
        ilow = 0
        ihigh = lbm1
        while ihigh-ilow > 1:
            imid = int((ilow+ihigh)/2)
            if x_test> basis[imid]:
                ilow = imid
            else:
                ihigh = imid

        # do we want to use the lower or upper bound?
        s = int(nearest)
        if s==0:   # find nearest number, geometrically
            highrat = basis[ihigh]/x_test
            lowrat = x_test/basis[ilow]
            if lowrat<highrat:
                index = ilow
            else:
                index = ihigh

        elif s>0: # we want the upper
            index = ihigh

        else:  # the lower
            index = ilow

        index += offset
        while index<0:     # handle the potential wrapping into the previous range
            index += lbm1
            exp -= 1 
        while index>=lbm1:  # handle the potential wrapping into the next range
            index -= lbm1
            exp += 1
            
        return(sign*basis[index]*(base1**exp))

    return quant




q125 = make_quant([1, 2, 5, 10])   # nice oscilloscope and graph increments

qE2 = make_quant([1, 3, 10])    # roughly 10dB steps, beloved of RF attenuators

qE3 = make_quant([1.0, 2.2, 4.7, 10.0]) # very coarse resistor steps

qE5 = make_quant([1.0, 1.6, 2.5, 4.0, 6.3, 10.0]) # often seen as capacitor voltages

qE6 = make_quant([1.0, 1.5, 2.2, 3.3, 4.7, 6.8, 10.0]) # coarse resistor steps

qE10 = make_quant([1.0, 1.25, 1.6, 2.0, 2.5,
                    3.2, 4.0, 5.0, 6.3, 8.0, 10.0]) # log10 approxmimation
                                                    # I'm trying to learn these
                                                    # for mental arithmetic

qE12 = make_quant([1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3,
                         3.9, 4.7, 5.6, 6.8, 8.2, 10.0])  # common resistor steps

qE24 = make_quant([1.0, 1.1, 1.2, 1.3, 1.5, 1.6,           # common professional resistor steps
                         1.8, 2.0, 2.2, 2.4, 2.7, 3.0,     # E12 superset
                         3.3, 3.6, 3.9, 4.3, 4.7, 5.1,
                         5.6, 6.2, 6.8, 7.5, 8.2, 9.1, 10.0]) 

qE48 = make_quant([1.00, 1.05, 1.10, 1.15, 1.21, 1.27,       # fine resistor steps
                        1.33, 1.40, 1.47, 1.54, 1.62, 1.69,  # NOT an E24 superset
                        1.78, 1.87, 1.96, 2.05, 2.15, 2.26,
                        2.37, 2.49, 2.61, 2.74, 2.87, 3.01,
                        3.16, 3.32, 3.48, 3.65, 3.83, 4.02,
                        4.22, 4.42, 4.64, 4.87, 5.11, 5.36,
                        5.62, 5.90, 6.19, 6.49, 6.81, 7.15,
                        7.50, 7.87, 8.25, 8.66, 9.09, 9.53, 10.0])

qE96 = make_quant([1.00, 1.02, 1.05, 1.07, 1.10, 1.13,        # very fine resistor steps
                        1.15, 1.18, 1.21, 1.24, 1.27, 1.30,   # E48 superset
                        1.33, 1.37, 1.40, 1.43, 1.47, 1.50,
                        1.54, 1.58, 1.62, 1.65, 1.69, 1.74,
                        1.78, 1.82, 1.87, 1.91, 1.96, 2.00,
                        2.05, 2.10, 2.16, 2.21, 2.36, 2.32,
                        2.37, 2.43, 2.49, 2.55, 2.61, 2.67,
                        2.74, 2.80, 2.87, 2.94, 3.01, 3.09,
                        3.16, 3.24, 3.32, 3.40, 3.48, 3.57,
                        3.65, 3.74, 3.83, 3.92, 4.02, 4.12,
                        4.22, 4.32, 4.42, 4.53, 4.64, 4.75,
                        4.87, 4.91, 5.11, 5.23, 5.36, 5.49,
                        5.62, 5.76, 5.90, 6.04, 6.19, 6.34,
                        6.49, 6.65, 6.81, 6.98, 7.15, 7.32,
                        7.50, 7.68, 7.87, 8.06, 8.25, 8.45,
                        8.66, 8.87, 9.09, 9.31, 9.59, 9.76, 10.0])


           
if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
