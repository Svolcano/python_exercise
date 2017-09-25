import global_module
global_module.global_b = 2000
if __name__ == "__main__":
    a = ((1,),(2,),(3,),(4,),(5,),(6,),)
    b = [i[0] for i in a]
    print(b)


    print (type('ll'))
    if isinstance('ll', str):
        print (123)
    else:
        print (456)