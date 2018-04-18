from PIL import Image, ImageFilter, ImageDraw
import time
from pylab import *


def blend_two_images(img1_path, img2_path, img3_path='blend.png'):
    img_mode = 'RGBA'
    i1 = Image.open(img1_path)
    i1.convert(img_mode)
    print(i1.size)
    i2 = Image.open(img2_path)
    i2.convert(img_mode)
    print(i2.size)
    i2 = i2.resize(i1.size)
    print(i2.size)
    i3 = Image.blend(i1, i2, 0.3)
    i3.show()
    i3.save(img3_path)


def cover(base_img, x, y, kuan, gao):
    box = (x, y, x + kuan, y + gao)
    region_size = (kuan, gao)
    region = Image.new('RGBA', region_size, (100, 0, 0, 20))
    #region.filter(ImageFilter.BLUR)
    base_img.paste(region, box)


def lines(base_img, x, y, kuan, gao):
    draw = ImageDraw.Draw(base_img)
    a = x
    x_e = x + kuan + 1
    y_e = y + gao + 1
    while a < x_e:
        b = y
        while b < y_e:
            draw.line((a, b, a+2, b+2), fill=(200, 200, 200), width=4)
            b += 5
        a += 3


def points(base_img, x, y, kuan, gao):
    box = (x, y, x + kuan, y + gao)
    region_size = (kuan, gao)
    draw = ImageDraw.Draw(base_img)
    c = 0
    # for a in range(x, x+kuan+1, 1):
    #     for b in range(y, y+gao+1, 2):
    #         c+=1
    #         draw.point((a, b), 10)
    a = x
    b = y
    x_e = x + kuan + 1
    y_e = y + gao + 1
    while a < x_e:
        b = y
        while b < y_e:
            c += 1
            draw.point((a, b), (0, 0, 0))
            b += 0.1
        a += 2
    print(c)


def part_operate(p1, mask=None):
    base_img = Image.open(p1)
    target = Image.new('RGBA', base_img.size, (0, 0, 0, 0))
    x, y = 270, 124
    kuan, gao = 131, 64
    # cover(base_img, x, y, kuan, gao)
    # cover(base_img, 238, 238, 120, 120)
    # cover(base_img, 272, 192, 87, 44)
    lines(base_img, x, y, kuan, gao)
    lines(base_img, 238, 238, 120, 120)
    lines(base_img, 272, 192, 87, 44)
    #target.show()
    #base_img.filter()
    #base_img.paste(target, (0, 0), target)
    #base_img.filter(ImageFilter.BoxBlur(10))
    base_img.show()
    name, suffix = p1.split('.')
    base_img.save("%s.%s" % (name+str(time.time()), suffix))


def gs(p1, x=270, y=124, kuan=131, gao=64):
    box = (x, y , x+kuan, y+gao)
    base_img = Image.open(p1)
    target = Image.new('RGBA', base_img.size, (0, 0, 0, 0))
    target.paste(base_img, (0, 0))

    mask_img = base_img.crop(box)
    print(mask_img.size)

    mask_img = mask_img.filter(ImageFilter.BoxBlur(20))
    #mask_img.show()
    target.paste(mask_img, (x, y))

    target.show()
    #name, suffix = p1.split('.')
    #target.save("%s.%s" % (name+str(time.time()), suffix))


def get_hit(p1):
    im = array(Image.open(p1))
    imshow(im)
    print('Please click 3 points')
    x = ginput(3)
    print('you clicked:', x)
    show()


if __name__ =='__main__':
    p1 = '2.png'
    p2 = '1.jpg'
    p3 = '身份证背面.jpg'
    # blend_two_images(p1, p2, '3.jpg')
    #gs(p3, 1434, 1825, 755, 82)
    get_hit(p1)
