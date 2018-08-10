
import collections
import random
a = [0, 1]


i=0
counter = collections.Counter()
while i < 20:
    k = random.choice(a)
    counter[k] += 1
    i += 1

print(counter)