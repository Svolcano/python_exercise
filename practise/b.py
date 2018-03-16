# -*- coding:utf-8 -*-
class Car(object):
    def __init__(self, make, model, year):
        self.make = make
        self.model = model
        self.year = year
        self.odometer_reading = 0  # 属性默认值

    def get_descriptive_name(self):
        long_name = str(self.year) + ' ' + self.make + ' ' + self.model
        return long_name.title()

    def read_odometer(self):
        print('the car ' + str(self.odometer_reading))

    # 通过方法修改属性值
    def udpate_odometer(self, mileage):
        if mileage >= self.odometer_reading:
            self.odometer_reading = mileage
        else:
            print('you can not roll back an odometer!')

    # 通过方法对属性值进行递增
    def increment_odometer(self, mile):
        self.odometer_reading += mile


class Battery(object):
    def __init__(self, battery_size=70):
        self.battery_size = battery_size

    def describe_battery(self):
        print('battery:' + str(self.battery_size))


class ElectricCar(Car):
    def __init__(self, make, model, year):
        super(ElectricCar, self).__init__(make, model, year)
        self.ba = Battery()

    def show(self):
        print(123)
        self.ba.describe_battery()

if __name__ == '__main__':
    my_tesla = ElectricCar('tesla', 'models', 2016)
    print(my_tesla.get_descriptive_name() + ' ' + str(my_tesla.odometer_reading))
    my_tesla.show()

