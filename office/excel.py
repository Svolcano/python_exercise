import xlrd
import xlwt

def write_excel():
    b = xlwt.Workbook()
    s1 = b.add_sheet('hello world')
    n = 100
    for i in range(1, n):
        for j in range(1, n):
            if j>=i:
                s1.write(j, i, "%d*%d=%d" % (i, j, i*j))
    b.save('demo.xls')


def read_excel():
    b = xlrd.open_workbook('texcel.xlsx')
    print(b.sheet_names())
    s1 = b.sheet_by_index(0)
    print(s1.name, s1.nrows, s1.ncols)
    nr = s1.nrows
    nc = s1.ncols
    for i in range(nr):
        for j in range(nc):
            print(i, j, s1.cell(i, j))


if __name__ == "__main__":
    write_excel()