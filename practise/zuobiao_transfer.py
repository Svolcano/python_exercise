#coding utf8
import math
import csv
g_pi = 3.1415926535897932384626
g_x_pi = 3.14159265358979324 * 3000.0 / 180.0
g_a = 6378245.0
g_ee = 0.00669342162296594323

'''
高德地图、腾讯地图以及谷歌中国区地图使用的是GCJ-02坐标系
百度地图使用的是BD-09坐标系
'''

def gcj02_To_Bd09(long, lat):
    global g_x_pi
    x = long
    y = lat
    z = math.sqrt(x * x + y * y) + 0.00002 * math.sin(y * g_x_pi)
    theta = math.atan2(y, x) + 0.000003 * math.cos(x * g_x_pi)
    tempLon = z * math.cos(theta) + 0.0065
    tempLat = z * math.sin(theta) + 0.006
    return tempLon, tempLat


def bd09_To_Gcj02(long, lat):
    global g_x_pi
    x = long - 0.0065
    y = lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * g_x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * g_x_pi)
    tempLon = z * math.cos(theta)
    tempLat = z * math.sin(theta)
    return tempLon, tempLat


def main():
    long, lat = 116.39419,39.947538
    a, b = gcj02_To_Bd09(long, lat)
    print a,",", b


def transfer_yd(i, o):
    with open(i, 'r') as ih:
        csvh = csv.reader(ih)
        with open(o, 'w') as wh:
            for i in csvh:
                long = float(i[-2].strip())
                lat = float(i[-1].strip())
                t_long, tlat = gcj02_To_Bd09(long, lat)
                i.append(t_long)
                i.append(tlat)
                i = [str(e) for e in i]
                wh.write("%s\n" % ','.join(i))

if __name__ == "__main__":
    i, o = 'D:/python_practise/python_exercise/practise/yx.csv', 'D:/python_practise/python_exercise/practise/yx_deal.csv'
    transfer_yd(i, o)
 

