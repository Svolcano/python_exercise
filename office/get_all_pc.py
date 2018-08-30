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
    all_data = {}
    suffix = ['自治区','自治县','省','镇','区','县','市','乡']
    for i in range(1, nrows):
        row = sheet0.row_values(i)
        area_code = row[6]
        cpl = all_data.get(area_code, [])
        nnn = [row[1],row[3],row[5],]
        for s in suffix:
            nnn = [a.replace(s, '') for a in nnn]
        cpl.extend(nnn)
        all_data[area_code] = list(set(cpl))
    return all_data
    


if __name__ == "__main__":
    root = "e:/input"
    xlsx_name = "dict_district_intl(2)(sanji).xlsx"
    # a = get_all_csv_data(os.path.join(root, csv_file))
    # print(a)
    a = get_src_xlsx_data(os.path.join(root, xlsx_name))
    print(a)


