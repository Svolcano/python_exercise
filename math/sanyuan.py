import numpy
from scipy.linalg import solve
k=[321 ,323, 324, ]
v =[71902, 76505,80248]
a = []
for i in k:
    a.append([i**2, i, 1])

a1 = numpy.array(a)
print(a1)
b = numpy.array(v)
print(b)
res = solve(a1,b)
ma, mb, mc = res
for i in range(321, 341):
    print(i, int(ma*i**2+mb*i+mc))

    