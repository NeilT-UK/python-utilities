__all__ = ['eng_str', 'eng_float']

subs = { 0: u'',
         3: u'k',  -3: u'm',
         6: u'M',  -6: u'u',
         9: u'G',  -9: u'n',
        12: u'T', -12: u'p',
        15: u'P', -15: u'f',
        18: u'E', -18: u'a',   # what f*kwit at the BIPM thought up E?
        21: u'Z', -21: u'z',
        24: u'Y', -24: u'y'}

# invert the dict for parsing eng formats easily, leave out the 0, add the mu
subs_inv = {subs[i]:i for i in subs if i!=0}   
subs_inv[u'\u00b5'] = -6

def eng_str(x, digits=None, limits=(-12, 9), greek=False):
    """ return an engineering formatted unicode string representation

    That's basically an exponential format
    with the exponent a multiple of 3,
    replaced with a standard multiplier suffix when possible

    use at most 'digits', though some roundings may produce fewer  
    limits allows a restricted range of letter replacement (either order)
    the default limit (-12, 9) is pico to Giga
    if greek is true, use a unicode micro, otherwise use 'u'

    This version only creates the suffix version, no option for infix
    This version always produces the shortest number,
    removing trailing zeros and a bare decimal point when possible

    >>> eng_str(1.2345, 3)
    '1.23'
    >>> eng_str(123.45, 3)
    '123'
    >>> eng_str(1234.5e4, 3)
    '12.3M'
    >>> eng_str(0.0003, 3)
    '300u'
    >>> eng_str(0.0003, 3, greek=True)
    '300\u00b5'
    >>> eng_str(31.2345e-15, 5)
    '31.235e-15'
    >>> eng_str(3e-14, 3, limits=(-24,24))
    '30f'
    >>> eng_str(314.15927e-22)
    '31.415927e-21'
    >>> eng_str(314.15927)
    '314.15927'
    >>> eng_str(3141.5927)
    '3.1415927k'
    >>> eng_str(0.00234)
    '2.34m'
    
    """

    # capture the sign
    if x<0:
        sign = u'-'
    else:
        sign = u''
    # and lose it from the number
    absx = abs(x)

    if digits:
        # if number of digits specified, use e format
        # it always produces one digit before the point, and dp digits after
        # use int to be very accepting about how digits is specified
        dp = max((0, int(digits)-1))
        x_str = u'{:.{dp}e}'.format(absx, dp=dp)
        (mant, exp) = x_str.split(u'e')
        # drop the dp from the mantissa and pad with zeroes to simplify scaling
        mant = mant.replace(u'.', u'')+u'00'
        exp = int(exp)
        dp_pos = 1
    else:
        # use str() to get all the digits it thinks are relevant
        # unfortunately it has a variable format for numbers close to unity
        #print(absx)
        x_str = str(absx)
        #print(x_str)
        if 'e' in x_str:      # it's normalised like e format
            (mant, exp) = x_str.split(u'e')    # so we can pull it apart like e
            mant = mant.replace(u'.', u'')+u'00'
            exp = int(exp)
            dp_pos = 1
        else:      # it's non-normalised, with an exponent of 0
            mant = x_str
            exp = 0
            dp_pos = x_str.index('.')
            mant = mant.replace(u'.', u'')+u'00'
            while mant[0]=='0':     # if we have leading zeros
                exp -= 1
                mant = mant[1:]

            


    # find out how far we are from a multiple of 3, sn = shift_needed
    sn = exp%3      # modulus works in the correct direction for -ve as well
    # re-insert the dp, and adjust the exponent, to the shift_needed
    m_str = mant[:(dp_pos+sn)]+'.'+mant[(dp_pos+sn):]
    exp -= sn

    # now trim the trailing zeros, then the trailing point if remaining
    # use seperate steps because we don't want to trim any 0s from the integer
    m_str = m_str.rstrip(u'0')
    m_str = m_str.rstrip(u'.')

    # can we make a substitution (exp within limits, and defined)
    if (exp in subs) and (min(limits) <= exp <= max(limits)):
        exp_str = subs[exp]
    else:
        exp_str = u'e{:+03d}'.format(exp)

    if greek and exp_str == u'u':
        exp_str = u'\u00b5'

    return sign+m_str+exp_str

def eng_float(x):
    """ parse a string in engineering format into a float

    accept suffix or infix, and all defined multipliers, including greek micro

    >>> eng_float('2k7')
    2700.0
    >>> eng_float('2.7k')
    2700.0
    
    >>> eng_float('k7')
    700.0
    
    >>> eng_float('270u')
    0.00027
    >>> eng_float('270\u00b5')
    0.00027
        
    >>> eng_float('2k7m') # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValueError

    """

    # let float() to do the heavy lifting
    
    # is it a straight float?
    try:
        return float(x)
    except ValueError:
        pass

    # OK, so it just choked on trying the string as is
    # does it have a suffix, this will be the last character
    # make sure there's no whitespace to clog things up
    x = x.strip()
    if x[-1] in subs_inv:
        # yay, it's found one, replace it with exx
        x_try = x[:-1]+'e{}'.format(subs_inv[x[-1]])
        try:
            return float(x_try)
        except ValueError:
            # if replacing the suffix with exx didn't work, that's fatal
            raise ValueError('float() could not parse {} or {}'.format(x, x_try))

    # the only thing left to try is an infix multiplier
    # this replaces the decimal point
    # so if we have a decimal point at this stage, that's fatal
    if '.' in x:
        raise ValueError('{} is not a float, has no valid suffix, but has a decimal point'.format(x))

    # no decimal point huh! try looking for an infix multiplier
    for key in subs_inv:
        if key in x:
            # we have an infix candidate
            # replace it with a decimal point and append exx
            x_try = x.replace(key, u'.')
            x_try += 'e{}'.format(subs_inv[key])
            try:
                return float(x_try)
            except ValueError:
                # if replacing an infix multiplier wouldn't work, that's fatal
                raise ValueError('float() could not parse {} or {}'.format(x, x_try))

    # if we get here, we've tried everything
    raise ValueError('float() could not parse {} or any substitution'.format(x))
        


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)


