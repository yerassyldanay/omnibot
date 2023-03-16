class A:
    def __init__(self) -> None:
        print("it is running...")
        self.a = list()

    def methodA(self):
        print("calling method A in class A")


class B:
    def methodB(self):
        print("calling method B in class B")

class C:
    def methodC(self):
        print("calling method C in class C")


class General(A, B, C):
    def __init__(self) -> None:
        super().__init__()
        
    def call(self):
        self.methodA()
        self.methodB()
        self.methodC()
        print(self.a)

general = General()
# general.call()
