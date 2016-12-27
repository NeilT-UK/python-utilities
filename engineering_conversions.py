""" The engineering_conversions module

This provides two functions
eng_float() which behaves like float()
eng_str() which behaves like str()
but use engineering powers of 1000, and BIPM text multipliers like k and G

In the spirit of 'talk exact, listen forgiving', eng_float() understands all prefixes
defined by BIPM, both unicode micro characters, and strings like meg and Mega used by SPICE

>>> eng_float('12u6')
1.26e-05
>>> eng_str(1e7)
'10M'

"""

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

version = '2.0.1   Dec 2016'

MICRO_SIGN = '\u00B5'
GREEK_MU = '\u03BC'

# define the multipliers for making floats into strings
# this happens at load time, so the time taken is 'lost' in the overall program load time

ms = {+3:'k', +6:'M', +9:'G', +12:'T', +15:'P', +18:'E', +21:'Z', +24:'Y',
      -3:'m', -6:'u', -9:'n', -12:'p', -15:'f', -18:'a', -21:'z', -24:'y'}

# define the weights for decoding strings to floats
# invert the multipliers that we have
weights = {}
for m in ms:
    weights[ms[m]] = m
    
weights[MICRO_SIGN] = -6     # add both micros
weights[GREEK_MU] = -6

longest_weights = {}         # add the meg variations
longest_weights['mega'] = 6  # in size order
longest_weights['MEGA'] = 6
longest_weights['Mega'] = 6  # these need to be longer due to the trailing a != atto

long_weights = {}
long_weights['meg'] = 6          
long_weights['MEG'] = 6           
long_weights['Meg'] = 6

long_weights['da'] = 1       # trailing a != atto, so put it in longer
weights['d'] = -1             # add the non-3 BIPM SI prefixes, because we can
weights['c'] = -2             # and it makes listening more forgiving
weights['h'] = 2

        

# what *ck-wit at BIPM thought Exa would make a good multiplier
# when 'e' was already in use for exponents???
# this means that '34E3' will be interpretted as 34000, rather than 34.3 Exa
# but 34E will get interpretted as Exa, as float() doesn't like it

def eng_str(x, digits=6, limits=(-12,9), micro='u', mega='M',
           infix=False, show_plus=False, show_trailing_zeros=False):
    """Return a formatted string, using powers of 1000, and BIPM engineering multipliers

    digits      integer, defaults to 6
                <1 corrected to 1, large values honoured

    limits      tuple of integers, defaults to (-12,9), the electronics range pico to Giga
                restricts the substitution range to more common prefixes
                order can be (low, high) or (high, low)

    micro       string for -6 substitution, defaults to 'u'
                unicode MICRO_SIGN and GREEK_MU available as module constants
    
    mega        string for +6, defaults to 'M', meg is used by most SPICEs

    infix       defaults to False, use decimal point and suffix, if True, replace decimal with symbol

    show_plus   defaults to False, minus is always shown regardless of this switch

    show_trailing_zeros   defaults to False, zeros truncated as far as possible             
            
    check a few simple random numbers with defaults
    >>> [eng_str(n) for n in (3, 1.2e3, 30e3, -0.007)]
    ['3', '1.2k', '30k', '-7m']

    check some 'normal' big numbers, and the default limits behaviour
    >>> [eng_str(4*pow(10,n)) for n in range(4, 13)]
    ['40k', '400k', '4M', '40M', '400M', '4G', '40G', '400G', '4e+12']
    
    check all the large multipliers, and excess limit behaviour
    >>> [eng_str(3*pow(10,n), limits=(100,-100)) for n in range(3, 28, 3)]
    ['3k', '3M', '3G', '3T', '3P', '3E', '3Z', '3Y', '3e+27']

    check some 'normal' small numbers, and the limits behaviour    
    >>> [eng_str(4*pow(10,-n)) for n in range(4, 18, 2)]    
    ['400u', '4u', '40n', '400p', '4p', '40e-15', '400e-18']
    
    check all the small multipliers
    >>> [eng_str(3*pow(10,n), limits=(100,-100)) for n in range(-3, -28, -3)]
    ['3m', '3u', '3n', '3p', '3f', '3a', '3z', '3y', '3e-27']

    check the digits parameter and trailing zeros, which defaults to false
    >>> [eng_str(314159, digits=n) for n in range(8)]
    ['300k', '300k', '310k', '314k', '314.2k', '314.16k', '314.159k', '314.159k']

    check trailing zeros on
    >>> [eng_str(314159, digits=8, show_trailing_zeros=stz) for stz in (True, False)] 
    ['314.15900k', '314.159k']

    demonstrate infix (ugly, isn't it)
    >>> [eng_str(314159, infix=infx) for infx in (True, False)]
    ['314k159', '314.159k']
    
    check the sign control is working
    >>> [eng_str(n, show_plus=sp) for (n, sp) in ((1, False), (1, True), (-1, False), (-1, True))]
    ['1', '+1', '-1', '-1']

    huge numbers of digits?
    >>> eng_str(314159, digits=30, show_trailing_zeros=True)
    '314.159000000000000000000000000k'
    
    fractional digits?
    >>> eng_str(314159, digits=5.5)
    '314.16k'
    
    extreme number sizes (within the range of float)
    >>> [eng_str(3*pow(10,n)) for n in range(-306, 307, 102)]
    ['3e-306', '3e-204', '3e-102', '3', '3e+102', '3e+204', '3e+306']

    check the e+06 substitutions, normal and bizarre (I can't think of a good reason to trap) 
    >>> [eng_str(4e8, mega=n) for n in ('M', 'meg', 'Mega', 'foo')]       
    ['400M', '400meg', '400Mega', '400foo']

    check the e-06 substitutions, normal and bizarre (I still can't think of a good reason to trap) 
    >>> [eng_str(4e-5, micro=n) for n in ('u', MICRO_SIGN, GREEK_MU, 'z')]       
    ['40u', '40µ', '40μ', '40z']
    
    """



    # don't be silly
    digits = int(digits)      # is this defensive? are we going to get a float?
    if digits<1:
        digits=1

    # let the e format do the heavy lifting
    # force a + sign to regularise the format
    # though we still have to look for the e as the exp field width can vary

    e_str = '{:+.{fdigits}e}'.format(x, fdigits=digits-1)

    # now pull the fields apart
    sign = e_str[0]
    ipart = e_str[1]
    dp = '.'
    fpart = e_str[3:(digits+2)]
    exp = int(e_str[e_str.find('e')+1:])

    # print('raw e format    ', sign, ipart, dp, fpart, exp)

    # find whether exp is a factor of 3, and adjust if not
    adjustment = exp%3
    # beef up length of fpart if it needs it
    while len(fpart)<adjustment:
        fpart += '0'
    # transfer digits from fpart to ipart
    ipart += fpart[:adjustment]
    fpart = fpart[adjustment:]
    # and fix the exponent
    exp -= adjustment

    # print('normed to 3     ', sign, ipart, dp, fpart, exp)

    # optionally take off the trailing zeros
    if not show_trailing_zeros:
        fpart = fpart.rstrip('0')
    # and kill the decimal point if the fractional part has gone
    if not(fpart):
        dp = ''


    # print('removed zeros   ', sign, ipart, dp, fpart, exp)

    # now we have to figure out exactly how to format this puppy
    # I am going to try to minimise if then else try except special cases
    # and just make it run a standard process

    # find the limits that we are going to use, and shield the dict
    hilim = min(max(limits), 24)
    lolim = max(min(limits), -24)

    # deal with the +6 and -6 special cases by putting them into the dict
    ms[6] = mega
    ms[-6] = micro

    # deal with the special case of 0 for infix/postfix use by putting into dict
    # print('infix is ', infix)
    if infix:
        ms[0] = '.'
    else:
        ms[0] = ''

    # is substitution possible?
    can_subs = lolim <= exp <= hilim
    # print('can we substitute?', can_subs)
    if not can_subs:
        mult = 'e{:+}'.format(exp)

    # remove the plus if we don't need it
    if (not show_plus) and (sign=='+'):
        sign = ''

    # finally
    # if we can make an infix substitution
    if infix and can_subs:
        # print('doing infix subs')
        return '{}{}{}{}'.format(sign, ipart, ms[exp], fpart)

    # if we can make a postfix substitution
    if can_subs:
        # print('doing postfix subs')
        return '{}{}{}{}{}'.format(sign, ipart, dp, fpart, ms[exp])

    # we can't make any substitution, return numeric
    # print('doing the default formatting')
    return '{}{}{}{}{}'.format(sign, ipart, dp, fpart, mult)



def eng_float(x_org):
    """[eng_f]Return a float, interpretting BIPM engineering prefixes[end_help]

    identify and substitute all prefix symbols defined by the BIPM
    and various versions of 'meg' used by most SPICE programs

    raise ValueError if the string is empty or cannot be interpretted as an engineering float

    check the simple >1 multipliers
    >>> [eng_float(s) for s in ('1', '1da', '1h', '1k', '1M', '1meg', '1Mega', '1G')]
    [1.0, 10.0, 100.0, 1000.0, 1000000.0, 1000000.0, 1000000.0, 1000000000.0]
    
    >>> [eng_float(s) for s in ('1T', '1P', '1E', '1Z', '1Y')]
    [1000000000000.0, 1000000000000000.0, 1e+18, 1e+21, 1e+24]

    check the simple <1 multipliers
    >>> [eng_float(s) for s in ('1', '1d', '1c', '1m', '1u', '1'+MICRO_SIGN, '1'+GREEK_MU)]
    [1.0, 0.1, 0.01, 0.001, 1e-06, 1e-06, 1e-06]
    
    >>> [eng_float(s) for s in ('1p', '1f', '1a', '1z', '1y')]
    [1e-12, 1e-15, 1e-18, 1e-21, 1e-24]

    check infix and suffix forms
    >>> [eng_float(s) for s in ('1.3k', '1k3', '1u3', '1.3u')]
    [1300.0, 1300.0, 1.3e-06, 1.3e-06]

    check negative numbers
    >>> [eng_float(s) for s in ('-1.3k', '-1k3', '-1u3', '-1.3u')]
    [-1300.0, -1300.0, -1.3e-06, -1.3e-06]

    empty input
    >>> eng_float('')
    Traceback (most recent call last):
        ...
    ValueError: no input, nothing to do

    illegal format with infix
    >>> eng_float('1.2m3')    
    Traceback (most recent call last):
        ...
    ValueError: "1.2m3" found infix "m" but "1.2.3e-3" not parsed

    illegal format with suffix
    >>> eng_float('14.3mm')    
    Traceback (most recent call last):
        ...
    ValueError: "14.3mm" found suffix "m" but "14.3me-3" not parsed

    unrecognised suffix
    >>> eng_float('1t')    
    Traceback (most recent call last):
        ...  
    ValueError: could not parse "1t" as float, no multiplier found

    bare suffix
    >>> eng_float('m')    
    Traceback (most recent call last):
        ... 
    ValueError: "m" found suffix "m" but "e-3" not parsed
    
    we let float() do the heavy lifting    
    """

    if len(x_org)==0:
        raise ValueError('no input, nothing to do')

    try:
        return float(x_org)
    except ValueError:
        pass

    # so float() couldn't make sense of it
    # let's whip off any non-printing characters before we start
    x = x_org.strip()
  
    # does it end in any of our pre-defined multipliers, check long to short?
    cand = None
    for search_in in (longest_weights, long_weights, weights):
        if cand:
            break
        for suffix in search_in:
            if cand:
                break
            if x.endswith(suffix):
                cand = suffix
                cand_weight = search_in[suffix]

    if cand:
        # got one! remove it
        x = x[:(-len(cand))]
        # and replace it with an exponent
        x += 'e'+str(cand_weight)
        # and now see whether float can make sense of it
        # use this two-step process as it delivers clean ValueErrors

        try:
            thing = float(x)
        except ValueError:
            thing = None

        if thing==None:  
            raise ValueError('"{}" found suffix "{}" but "{}" not parsed'.format(x_org, cand, x))
        else:
            return thing
        
    # nope, if we get here, float choked on the substitution
    # so does it have an infix embedded in it?
    # need to check in the order longest to shortest
    # to avoid existing prematurely with 'm', when there's a 'mega'
        
    cand = None
    for search_in in (longest_weights, long_weights, weights):
        if cand:
            break
        for infix in search_in:
            if cand:
                break
            pos = x.find(infix)
            if pos >= 0:
                cand = infix
                cand_weight = search_in[infix]

    if cand:
        # got one! remove it
        first = x[:pos]
        last = x[(pos+len(cand)):]
        # replace with decimal point and add a numeric exponent
        x = first+'.'+last+'e'+str(cand_weight)
        # and now can float() chow down on it?

        try:
            thing = float(x)
        except ValueError:
            thing = None

        if thing==None:
            raise ValueError('"{}" found infix "{}" but "{}" not parsed'.format(x_org, cand, x))
        else:
            return thing

    raise ValueError('could not parse "{}" as float, no multiplier found'.format(x_org))




if __name__ == '__main__':
    import doctest
    print('running doctest')
    print('nothing else below here means everything has passed')
    doctest.testmod()



"""
if __name__ == '__main__':
    import tkinter as tki
    import GUI_IO_widget as giw

    def execute_func():
        ps = panel.get()
        # print(ps)
        n = ps['number']
        ds = ps['digits']
        zeros = ps['trailing zeros']
        infix = ps['infix']
        mustr = ps['micro_str']
        Mstr = ps['mega_str']

        
        rep = eng_str(n, ds, show_trailing_zeros=zeros, infix=infix, micro=mustr, mega=Mstr)
        panel.set_data('output', rep)

    def exec_float_func():
        fs = fanel.get()
        num = fs['eng_float func']
        fanel.set_data('output', str(num))
        
    root = tki.Tk()
    panel = giw.GUI_inputs(root, execute=execute_func, text='Test eng_str()')
    panel.pack()
    panel.add('number', conv=float)
    panel.add('digits', conv=int)
    panel.add('trailing zeros', conv=bool)
    panel.add('infix', conv=bool)
    panel.add('micro_str', data='u')
    panel.add('mega_str', data='M')
    panel.add('output', output_only=True)

    fanel = giw.GUI_inputs(root, execute=exec_float_func, text='Test eng_float()')
    fanel.pack()
    fanel.add('eng_float func', conv=eng_float, data=1)
    fanel.add('output', output_only=True)
    
    root.mainloop()
"""



"""
if __name__ == '__main__':
    a = 2
    while a:          
        a = input('test string - ')
        try:
            print(eng_float(a))
        except ValueError as ve:
            print('threw value error')
            print(ve)
"""

          
          
    

        





    
    
    
