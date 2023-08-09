import numpy as np
import yoda

h = yoda.Histo1D(9, 1, 10, "/zeros_1d")
yoda.write(h, "zeros.yoda")

h2 = yoda.Histo1D(9, 1, 10, "/filled_1d")
for i in np.linspace(1,10,100):
    h.fill(i)
yoda.write(h, "filled_1d.yoda")

#Generate pairs of data for both x and y axes
np.random.seed(42)
x_data = np.random.uniform(1,5,100)
y_data = np.random.uniform(5,10,100)

h2d = yoda.Histo2D(4,1,5,4,6,10, "/some_h2d")
for x, y in zip(x_data,y_data):
    h2d.fill(x,y)
yoda.write(h2d, "filled_2d.yoda")