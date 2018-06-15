# -*- coding: utf-8 -*-

import csv
import sys

FRAME = '# -*- coding: utf-8 -*-\n\n' \
        'STATUS_CODE={{\n{}\n}}'
ONE_LINE = '       \'{}\':{{\'status\':{}, \'message\':\'{}\'}},\n'

f = open(sys.argv[1])

lines = []
csv_reader = csv.DictReader(f)

for row in csv_reader:
    tmp_line = ONE_LINE.format(row['key'], row['status'], row['message'])
    lines.append(tmp_line)

fout = open(sys.argv[2], 'w')
result = FRAME.format(''.join(lines))
fout.write(result)
