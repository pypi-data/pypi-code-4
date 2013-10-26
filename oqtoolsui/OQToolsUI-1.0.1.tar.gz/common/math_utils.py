from math import exp, log


def find_interpolated_val(x_vals, y_vals, y):
    if y_vals[len(y_vals)-1] >= y:
        res = x_vals[len(x_vals)-1]
    elif y_vals[0] <= y:
        res = x_vals[0]
    else:
        y1 = 0
        y2 = 0
        found = False
        imlInd = 0
        for i in xrange(0, len(y_vals) - 1):
            y1 = y_vals[i]
            y2 = y_vals[i+1]
            imlInd = i
            if y2 <= y <= y1 or y1 <= y <= y2:
                found = True
                break
        if not found:
            raise Exception('y value (%(y)d) is invalid (y1: %(y1)d - y2: %(y2)d)' % {'y': y, 'y1': y1, 'y2': y2})

        x1 = c_log(x_vals[imlInd])
        x2 = c_log(x_vals[imlInd+1])
        y1 = c_log(y1)
        y2 = c_log(y2)
        y = log(y)

        res = exp((((y - y1) * (x2 - x1)) / (y2 - y1)) + x1)

    return res


def c_log(val):
    if val == 0:
        return 0.0

    return log(val)


def poe_to_return_period(poe):
    return round((-50.0/log(1-poe)))