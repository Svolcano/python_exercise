import time
from openpyxl import load_workbook, Workbook


def get_name_phone(file_path, sheet_name, name_prefix, phone_refix):
    result = {}
    book = load_workbook(file_path, read_only=True)
    sheet = book[sheet_name]
    max_row = sheet.max_row
    i = 2
    while i < max_row:
        name = sheet["%s%d" % (name_prefix, i)]
        phone = sheet["%s%d" % (phone_refix, i)]
        result[name] = phone
        i += 1
    book.close()
    return result



def mix_save(target_file_name, src_file, src_sheet_name, name_phone):
    target_book = Workbook(write_only=True)
    src_file = load_workbook(src_file, read_only=True)
    src_sheet = src_file[src_sheet_name]
    max_row = src_sheet.max_row
    max_column = src_sheet.max_column
    i = 1
    j = 1
    for i in range(1, max_row+1):
        for j in range(1, max_column+1):


    target_book.save(target_file_name)


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
