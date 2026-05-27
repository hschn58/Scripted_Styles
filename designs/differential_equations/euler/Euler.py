

def Eulers_Method(x_len, initial_x, initial_y, h): 
    import math

    def diff_eq(x,y):

        # scaler=lambda y,x:2*((1/(1+math.exp(-x)))-1)*(y-1.5)

        # y=scaler(y,x)

        # return (math.log(4.5-y)) * (1.5*(math.sin((math.pi/4)*initial_y)**2))*beta-y*math.cosh(x)+0.5*y*math.sin(y)+3*(math.sin(2*math.pi*x))**2

        return (x-1)/(math.log(y**6)-x)
    

    #diff_eq = lambda x, y,beta: (math.log(3-y)) * (1.5*(math.sin((math.pi/4)*initial_y)**2))*beta-y*math.cosh(x)+0.5*y*math.sin(y)+3*(math.sin(2*math.pi*x))**2
    
    diff = x_len - initial_x
    xval = [initial_x]
    yval = [initial_y]

    slope=[0]
    for i in range(1, h + 1):
        try:
            x0 = ((i - 1) / h) * diff + initial_x
            yprime = diff_eq(x0, initial_y)

            slope.append(yprime)   

            if not math.isfinite(yprime):
                break

            initial_y += yprime * (diff / h)

            xval.append(x0)
            yval.append(initial_y)

        except (OverflowError, ZeroDivisionError, ValueError):
            break

    return [[xval,yval], slope]
