def Eulers_Method(x_len, initial_x, initial_y, h): 
    k = 0.1
    import math
    diff_eq = lambda x, y: (math.log(y) / (y - x)) * (-x**4)
    
    diff = x_len - initial_x
    soln = []
    yval = []
    xval = []
    xval.append(initial_x)
    yval.append(initial_y)

    for i in range(1, h + 1):
        try:
            x0 = ((i - 1) / h) * diff + initial_x
            yprime = diff_eq(x0, initial_y)

            # Check if yprime is a valid number
            if math.isfinite(yprime):
                initial_y += yprime * (diff / h)
                xval.append(x0)
                yval.append(initial_y)
            else:
                break
        except (OverflowError, ZeroDivisionError, ValueError):
            break

    soln.extend([xval, yval])
    return soln
