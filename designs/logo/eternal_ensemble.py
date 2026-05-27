



import matplotlib.pyplot as plt
import numpy as np



#2*2 grid

#E1

let_width=0.25
branch_space=0.5
tot_length=0.75
tot_height=1.75

x_start=0
y_start=0

E1 = [[x_start,y_start],[tot_length+x_start,y_start],[tot_length+x_start,let_width+y_start],[let_width+x_start,let_width+y_start],[let_width+x_start,let_width+branch_space+y_start],
            [tot_length+x_start,let_width+branch_space+y_start],[tot_length+x_start,2*let_width+branch_space+y_start],[let_width+x_start,2*let_width+branch_space+y_start],
            [let_width+x_start,2*let_width+2*branch_space+y_start],[tot_length+x_start,2*let_width+2*branch_space+y_start],[tot_length+x_start,3*let_width+2*branch_space+y_start],
            [x_start,3*let_width+2*branch_space+y_start]]




E1.append(E1[0])

x, y = zip(*E1)  # Unzipping the points

plt.plot(x, y, '-', linewidth=2, color='black')


#E2

x_start=1
y_start=0

E2 = [[x_start,y_start],[tot_length+x_start,y_start],[tot_length+x_start,let_width+y_start],[let_width+x_start,let_width+y_start],[let_width+x_start,let_width+branch_space+y_start],
            [tot_length+x_start,let_width+branch_space+y_start],[tot_length+x_start,2*let_width+branch_space+y_start],[let_width+x_start,2*let_width+branch_space+y_start],
            [let_width+x_start,2*let_width+2*branch_space+y_start],[tot_length+x_start,2*let_width+2*branch_space+y_start],[tot_length+x_start,3*let_width+2*branch_space+y_start],
            [x_start,3*let_width+2*branch_space+y_start]]




E2.append(E2[0])

x, y = zip(*E2)  # Unzipping the points

plt.plot(x, y, '-', linewidth=2, color='black')

output_path = "bubble_double_E_matplotlib.png"

#plt.axis('off')
plt.savefig("bubble_double_E_matplotlib.png")
print(f"Image saved to: {output_path}")

plt.show()