import numpy as np
import matplotlib.pyplot as plt

MyVar = 100000

startbee=-0.0001
stopbee=0.00051
bee = np.arange(startbee,stopbee,((stopbee-startbee)/MyVar))

def weierstrass(x,Nvar):
    we=np.zeros(MyVar)

    for n in range(0,Nvar):
        we=we+np.cos(3**n*np.pi*x)/2**n
    return we

plt.plot(bee,np.reshape(weierstrass(bee, 500),(MyVar,)))

plt.show()