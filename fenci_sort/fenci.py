import time

def fen_ci(input_str, short=2, long=5):
    results = []
    str_len = len(input_str)
    if not input_str:
        return results
    if long > str_len:
        long = str_len
    if str_len <= short:
        return [input_str]
    x = short
    while x <= long:
        for i in range(str_len + 1 - x):
            results.append(input_str[i:i + x])
        x += 1
    return results

def check():
    print("start check")
    assert fen_ci('人民共和国') == ['人民', '民共', '共和', '和国', '人民共', '民共和', '共和国', '人民共和', '民共和国', '人民共和国']
    assert fen_ci('   ') == ['  ','  ','   ']
    assert fen_ci('中国') == ['中国']
    assert fen_ci('中') == ['中']
    assert fen_ci('') == []
    assert fen_ci(' ') == [' ']
    assert fen_ci(' 中1') == [' 中', '中1', ' 中1']
    assert fen_ci('123456') == ['12', '23', '34', '45', '56', '123', '234', '345', '456', '1234', '2345', '3456', '12345', '23456']
    print("check pass")

if __name__ == '__main__':
    print(fen_ci('河北卓兴金属丝网制品有限公司'))
