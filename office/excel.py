import xlrd
import xlwt
import time
from xlutils.copy import  copy
from openpyxl import load_workbook, workbook





def write_excel():
    b = xlwt.Workbook()
    s1 = b.add_sheet('hello world')
    n = 100
    for i in range(1, n):
        for j in range(1, n):
            if j>=i:
                s1.write(j, i, "%d*%d=%d" % (i, j, i*j))
    b.save('demo.xls')


def read_excel1(name_ph):
    st = time.time()
    b = xlrd.open_workbook('C:/Users/dd/Desktop/task/截至4月17日8点会员数据.xlsx')
    et = time.time()
    print("open file cost: %.3f" % (et - st))
    s1 = b.sheet_by_index(0)
    i = 1
    name_col = 1
    ph_col = 4
    while i < s1.nrows:
        name = s1.cell_value(i, name_col)
        ph = s1.cell_value(i, ph_col)
        name_ph[name] = ph
        i += 1
    print('read_excel1 done')


def read_ttt():
    b = load_workbook('texcel.xlsx')
    bs = b['Sheet1']
    bnr = bs.max_row
    i = 2
    while i < bnr:
        name = bs["B%d" % i].value
        print(i, name)
        bs['U%d' % i].value = 123
        i += 1

    b.save("texcel_done.xlsx")


def read_excel2(name_ph):
    b = load_workbook('C:/Users/dd/Desktop/task/回款/回款日志汇总.xlsx')
    bs = b['Sheet1']
    bnr = bs.max_row
    i = 2
    bs['U1'].value = '手机号'
    while i < bnr:
        name = bs["B%d" % i].value
        ph = name_ph[name]
        bs['U%d' % i].value = ph
        i += 1

    b.save('C:/Users/dd/Desktop/task/回款/回款日志汇总_done.xlsx')


if __name__ == "__main__":
    # name_ph = {}
    # st = time.time()
    # read_excel1(name_ph)
    # et1 = time.time()
    # print("read1 cost : %.3f" % (et1-st))
    # read_excel2(name_ph)
    # et2 = time.time()
    # print("read2 cost : %.3f" % (et2 - et1))
    read_ttt()
