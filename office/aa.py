
def max_z(x):
    mv = 0
    v_y = 0
    for y in range(1,1000):
        y = float(y)
        k = (5/8) * (x+y)/1000.0 + (3/8) *x/(x+y)
        if k > mv and ((x+y) <= 1000):
            mv = k
            v_y = y
    return (x, v_y, mv)
for x in range(450, 550):
    print(max_z(float(x)))

