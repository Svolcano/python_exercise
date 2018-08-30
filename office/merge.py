import xlrd
import xlwt
import os
import csv
import json
from utils.FormatTools import format_telnum_BQC

def get_src_xlsx_data(filename, sheet_index=0):
    src_book = xlrd.open_workbook(filename)#得到Excel文件的book对象，实例化对象
    sheet0 = src_book.sheet_by_index(sheet_index) # 通过sheet索引获得sheet对象
    nrows = sheet0.nrows    # 获取行总数
    ncols = sheet0.ncols    #获取列总数
    #cell_value2 = sheet0.cell_value(0, 1)
    #循环打印每一行的内容
    all_data = []
    all_csv_data = []
    for i in range(nrows):
        yield sheet0.row_values(i)

    
def get_all_csv_data(filename):
    all = {}
    with open(filename, 'r', encoding='utf8') as rh:
        cr = csv.reader(rh)
        for line in cr:
            tel = line[0]
            names = line[2]
            all[tel] = names
    return all

def get_web_name(names):
    if not names:
        return ''
    names = names.split(";")
    first = names[0]
    if "\t" in first:
        return first.split('\t')[0]
    else:
        return first



def deal(src1, src2, result_file):
    new_book = xlwt.Workbook(encoding='utf-8', style_compression=0)
    new_sheet = new_book.add_sheet('test', cell_overwrite_ok=True)
    src1_iter = get_src_xlsx_data(src1)
    all_src1 = {}
    for line in src1_iter:
        all_src1[line[0]] = line[1]
    print(all_src1)
    src2_iter = get_src_xlsx_data(src2)
    header = src2_iter.__next__()
    header.append("webengine")

    col_len = len(header)
    row_num = 0
    for c in range(col_len):
        new_sheet.write(row_num, c, header[c])
    row_num += 1
    m_q = 0
    w_q = 0
    for row in src2_iter:
        tel = row[1]
        f_tel = format_telnum_BQC(tel)[0]
        if f_tel:
            tel = f_tel
        names = all_src1.get(tel, '')
        find_name = get_web_name(names)
        row.append(find_name)
        for c in range(col_len):
            new_sheet.write(row_num, c, row[c])
        row_num += 1
    new_book.save(result_file)
    return m_q, w_q
        

if __name__ == "__main__":
    root = "C:/Users/scw/Desktop/a/ES查询-V3（后缀、地区处理）/"
    src1 = "3998.xlsx"
    src2 = "ES-交通银行-抽样数据10000条.xlsx"
    r_file = "ES-交通银行-抽样数据10000条v1.xls"
    # a = get_all_csv_data(os.path.join(root, csv_file))
    # print(a)

    a = deal(os.path.join(root, src1),
    os.path.join(root, src2),
    os.path.join(root, r_file)
    )
    print(a)

