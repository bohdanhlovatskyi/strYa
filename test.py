class A:

    def set_atr(sefl, atr, value):
        try:
            getattr(A, atr)
        except AttributeError:
            setattr(A, atr, value)

if __name__ == '__main__':
    a = A()
    a.set_atr('buf', 10)
    print(A.buf)