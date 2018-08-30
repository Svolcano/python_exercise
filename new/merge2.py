import csv

all_i = []
with open("aiii.csv", 'r', encoding='gbk') as fh:
    m = {}
    with open("m.csv", 'r', encoding='utf8') as tfh:
        tcr = csv.reader(tfh)
        for line in tcr:
            m[line[0]] = line[1]
    cr = csv.reader(fh)
    header = cr.__next__()
    header.append("found")
    m_a = [header]
    for line in cr:
        tel = line[1]
        line.append(m[tel])
        m_a.append(line)
    with open("merge.csv", 'w', encoding='utf8', newline='') as wh:
        cw = csv.writer(wh)
        cw.writerows(m_a)
