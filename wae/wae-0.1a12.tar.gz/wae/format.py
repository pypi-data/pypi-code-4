#coding: utf-8
__docformat__="epytext"

import datetime
from decimal import Decimal

def format_date(d, fmt='y-m-d'):
    assert isinstance(d, (datetime.date, datetime.datetime)) or d==None, d
    if d==None: return ""

    fmt = fmt \
            .replace("hh", "%(hh).2?") \
            .replace("mm", "%(nn).2?") \
            .replace("ss", "%(ss).2?") \
            .replace("y", "%(y).2?") \
            .replace("Y", "%(Y).4?") \
            .replace("m", "%(m).2?") \
            .replace("d", "%(d).2?") \
            .replace("?", "d")

    v = {
            'y': d.year-2000,
            'Y': d.year,
            'm': d.month,
            'd': d.day,
            'hh': 0,
            'nn': 0,
            'ss': 0,
    }
    if isinstance(d, datetime.datetime):
         v.update({'hh': d.hour, 'nn': d.minute, 'ss': d.second})
    return fmt % v 


def _moneyfmt(value, places=2, curr='', sep=',', dp='.', pos='', neg='-', trailneg=''):
    """Convert Decimal to a money formatted string.

       places:  required number of places after the decimal point
       curr:    optional currency symbol before the sign (may be blank)
       sep:     optional grouping separator (comma, period, space, or blank)
       dp:      decimal point indicator (comma or period)
                only specify as blank when places is zero
       pos:     optional sign for positive numbers: '+', space or blank
       neg:     optional sign for negative numbers: '-', '(', space or blank
       trailneg:optional trailing minus indicator:  '-', ')', space or blank

       >>> d = Decimal('-1234567.8901')
       >>> moneyfmt(d, curr='$')
       '-$1,234,567.89'
       >>> moneyfmt(d, places=0, sep='.', dp='', neg='', trailneg='-')
       '1.234.568-'
       >>> moneyfmt(d, curr='$', neg='(', trailneg=')')
       '($1,234,567.89)'
       >>> moneyfmt(Decimal(123456789), sep=' ')
       '123 456 789.00'
       >>> moneyfmt(Decimal('-0.02'), neg='<', trailneg='>')
      '<0.02>'
    """
    q = Decimal(10) ** -places      # 2 places --> '0.01'
    sign, digits, exp = value.quantize(q).as_tuple()
    result = []
    digits = map(str, digits)
    build, next = result.append, digits.pop
    if sign:
        build(trailneg)
    for i in range(places):
        build(next() if digits else '0')
    build(dp)
    if not digits:
        build('0')
    i = 0
    while digits:
        build(next())
        i += 1
        if i == 3 and digits:
            i = 0
            build(sep)
    if curr!=None: build(curr)
    build(neg if sign else pos)
    return ''.join(reversed(result))

def format_number(val, decimal=2, comma=True, cur="", verbose=None):
    if val==None: return ""

    if verbose=='zh':
        return _format_number_verbose_zh(val)
    elif verbose=='en':
        return _format_number_verbose_en(val)

    fmt = "%%.%df" % decimal
    lst = []

    if comma:
        sep = ','
    else:
        sep = ''
    return _moneyfmt(Decimal(str(val)), places=decimal, sep=sep, curr=cur)


def _format_number_verbose_zh(amount):
    "金额转换到汉字大写"
    amount = float(amount)
    
    digits = ["零","壹","贰","叁","肆","伍","陆","柒","捌","玖","拾"]
    radices = ["", "拾", "佰", "仟"]
    bigRadices = ["", "万", "亿"]
    decimals = ["角", "分"]

    CN_DOLLAR = "元"
    CN_INTEGER = "整"

    # Assert the number is not greater than the maximum number.
    if amount > 99999999999.99: raise Exception("Too large a number to convert!")
    if amount < 0.0: 
        amount = abs(amount)
        MINUS = 0
    else:
        MINUS = 1

    # Process the coversion from currency digits to characters:
    # Separate integral and decimal parts before processing coversion:
    amt = "%.2f" % amount
    parts = amt.split(".");
    if len(parts)>1:
        integral = parts[0];
        decimal = parts[1];
    else:
        integral = parts[0];
        decimal = "";

    # The output result.
    out = [] 
    
    # Process integral part if it is larger than 0:
    if int(integral)>0:
        zeroCount = 0;
        
        for i in range(len(integral)):
            p = len(integral)-i-1
            d = integral[i]
            quotient = p/4;
            modulus = p%4;
            
            if d=="0": 
                zeroCount+=1;
            else:
                if zeroCount>0: out.append(digits[0])
                zeroCount = 0
                out.append(digits[int(d)])
                out.append(radices[modulus])
        
            if modulus==0 and zeroCount<4: out.append(bigRadices[quotient])
            
        out.append(CN_DOLLAR)

    # Process decimal part if there is:
    if int(decimal)!=0:
        for i in range(len(decimal)):
            d = decimal[i]
            if d!="0":
                out.append(digits[int(d)])
                out.append(decimals[i])

    # Confirm and return the final output string:
    if out==[]: out = [digits[0], CN_DOLLAR]
    if int(decimal) == 0: out.append(CN_INTEGER)

    if MINUS==1:
        return "".join(out)
    elif MINUS==0:
        return "(%s)" % "".join(out)

    
def _format_number_verbose_en(sz):
    "数字大写(EN)"
    def _conv_3(je):
        w2 = {2: "TWENTY", 3: "THIRTY", 4: "FORTY", 5: "FIFTY", 6: "SIXTY", 7: "SEVENTY", 8: "EIGHTY", 9: "NINETY"}
        w1 = {
                1: "ONE", 2: "TWO", 3: "THREE", 4: "FOUR", 5: "FIVE", 6: "SIX", 7: "SEVEN", 8: "EIGHT", 9: "NINE", 10: "TEN", 11: "ELEVEN", 12: "TWELVE",
                13: "THIRTEEN", 14: "FOURTEEN", 15: "FIFTEEN", 16: "SIXTEEN", 17: "SEVENTEEN", 18: "EIGHTEEN", 19: "NINETEEN"
        }

        if je<=0: return []

        je1 = je % 10
        je = int(je/10)

        if je==0:  # 判断数字位数（1-3）并把3位数字分别存放在je1、je2、je3中
            jews = 1
        else:
            je2 = je % 10
            je = int(je/10)
            
            if je==0:
                jews=2
            else:                
                je3= je % 10
                jews=3

        lst = []

        if jews==1:
            return [w1[je1]]   #如果位数为1，直接转换
    
        else: # jews = 2, 3
            if 0<je1+10*je2<20:  #转换20以下数字
                lst.append(w1[je1+10*je2])
            elif je1+10*je2>=20:
                if je1==0:         # 转换20-99数字
                    lst.append(w2[je2])
                else:
                    lst = [w2[je2], w1[je1]]

        if jews==3:     # 转换百位数字
            if je1+10*je2 == 0:
                lst = [w1[je3], "HUNDRED"]
            elif je1+10*je2<20:
                lst = [w1[je3], "HUNDRED", "AND"] + lst
            else:
                lst = [w1[je3], "HUNDRED", "AND"] + lst

        return lst
    
    # begin of main
    sz = float(sz)
    if sz > 1000000000: raise Exception("Invalid number: too big")

    sz = int(sz*100+0.5)/100.0        # 小数超过两位四舍五入
    xs = int(((sz-int(sz))*100) % 100)   # 取小数点后两位有效数字

    if xs>0:
        cha = ["AND"] + _conv_3(xs) + ["CENTS"]   # 转换小数
    else:
        cha = ["ONLY"]

    sz1 = int(sz % 1000)       # sz1为百、十、个3位数字
    cha = _conv_3(sz1) + cha   # 转换（sz1）

    sz = int(sz/1000)          # sz为千位以上数字（含千位）
    if sz>0:        
        sz2 = sz % 1000        # sz2为十万、万、千3位数字
        if sz2 == 0:
            if sz1 != 0: cha = ["AND"]+cha       # （sz2）如果为'0'，判断在百位之前是否加'AND'
        else:
            cha = _conv_3(sz2) + ["THOUSAND"] + cha   # 如果不为'0'转换（sz2）
       
        sz = int(sz/1000)        # sz为百万位以上数字（含百万位）
        if sz>0:
            sz3 = sz % 1000      # sz3为亿、千万、百万3位数字
            cha = _conv_3(sz3) + ["MILLION"] + cha  # 转换（sz3）

    return " ".join(cha)

