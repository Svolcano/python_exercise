import xlrd
import xlwt
import os
import csv
import json


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


def deal(src_file_name, save_path, csv_file):
    new_book = xlwt.Workbook(encoding='utf-8', style_compression=0)
    new_sheet = new_book.add_sheet('test', cell_overwrite_ok=True)
    src_iter = get_src_xlsx_data(src_file_name)
    header = src_iter.__next__()
    header.append("web_tel4name")
    col_len = len(header)
    row_num = 0
    for c in range(col_len):
        new_sheet.write(row_num, c, header[c])
    row_num += 1
    m_q = 0
    w_q = 0
    all_csv_data = get_all_csv_data(csv_file)
    for row in src_iter:
        tel = row[0]
        wns = all_csv_data.get(tel, '')
        md = row[4]
        if not md and wns:
            m_q += 1 
        if md and not wns:
            w_q += 1
        row.append(wns)
        for c in range(col_len):
            new_sheet.write(row_num, c, row[c])
        row_num += 1
    new_book.save(save_path)
    return m_q, w_q
        

if __name__ == "__main__":
    root = "e:/input"
    csv_file = "tel_4_name_out.csv"
    xlsx_name = "a.xlsx"
    r_file = "result.xls"
    # a = get_all_csv_data(os.path.join(root, csv_file))
    # print(a)

    a = deal(os.path.join(root, xlsx_name), 
    os.path.join(root, r_file),
    os.path.join(root, csv_file)
    )
    print(a)

