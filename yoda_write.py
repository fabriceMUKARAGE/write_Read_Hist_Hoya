import numpy as np
import yoda

h = yoda.Histo1D(9, 1, 10, "/zeros_1d")
yoda.write(h, "zeros.yoda")

h2 = yoda.Histo1D(9, 1, 10, "/filled_1d")
for i in np.linspace(1,10,100):
    h.fill(i)
yoda.write(h, "filled_1d.yoda")
