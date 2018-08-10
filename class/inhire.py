
class A():
    name = 'A'

    def __init__(self, a):
        print("A's a:", a)

    @staticmethod
    def sfun():
        print("i am static")

    @classmethod
    def cfun(cls):
        print("my name is ", cls)
    

class AA(A):
    name = "AA"

    def __init__(self, a):
        super().__init__('456')


k = AA('123')
AA.sfun()
AA.cfun()