import os


def rename_jpg(path, i):
    for root, dirs, files in os.walk(path):
        for f in files:
            suffix = f[-5:]
            if suffix not in ['.jpeg']:
                continue
            f_w_p = os.path.join(root, f)
            n_f_n = os.path.join(root,'s%d%s' % (i, suffix))
            i += 1
            os.rename(f_w_p, n_f_n)
    return i


if __name__ == '__main__':
    ps = ['D:\\luntuan_girls_thread']
    index = 0
    for p in ps:
        index = rename_jpg(p, index)
        print(index)



