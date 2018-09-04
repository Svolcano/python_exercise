#coding:utf-8
import numpy as np
import matplotlib.pyplot as plt

def play(step):
    x=np.linspace(0,100,1000)
    y = 0
    b = 1
    for i in range(1000):
        b += 2
        y += 4*np.cos(x*b)/(b*np.pi)
    plt.figure(figsize=(100,80))

    plt.plot(x,y,label="$sin(x)$",color="red",linewidth=2)

    #设置X轴的文字
    plt.xlabel("Time(s)")
    #设置Y轴的文字
    plt.ylabel("Volt")
    #设置图表的标题
    plt.title("PyPlot First Example")
    #设置Y轴的范围
    plt.ylim(-10,10)
    #显示图示
    plt.legend()
    #显示出我们创建的所有绘图对象。
    nstep = int(step*10)
    plt.savefig(f'd:/png/{nstep}.png')
    plt.close('all')

step = 0.1

while step < 10:
    play(step)
    step += 0.1