class A():
    def __init__(self, limit):
        self.limit = limit
    
    def print(self):
        print(self.limit)

class B(A):
    def __init__(self, limit):
        super().__init__(limit=limit)

class C(B):
    pass

a = A(1)
a.print()
b = B(2)
b.print()
c = C(10)
c.print()

    
    