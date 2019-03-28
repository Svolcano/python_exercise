import random
# 求最长等差数列
demo_input = [random.randint(1, 100) for i in range(20)]

demo_input.sort()
total_len = len(demo_input)

c = 0
mc = 0
ml = []
for i in range(0, total_len):
    a0 = demo_input[i]
    c = 1
    l = [a0]
    if c > mc:
        mc = c
        ml = [kk for kk in l]
    for j in range(i + 1, total_len):
        a1 = demo_input[j]
        sub = a1 - a0
        c2 = c + 1
        l2 = [a0, a1]
        if c2 > mc:
            mc = c2
            ml = [kk for kk in l2]
        for k in range(j + 1, total_len):
            m = demo_input[k]
            if m - a1 == sub:
                c2 += 1
                l2.append(m)
                if c2 > mc:
                    mc = c2
                    ml = [kk for kk in l2]
                a1 = m
print(demo_input)
print(mc, ml)
