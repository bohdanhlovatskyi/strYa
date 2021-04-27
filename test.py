from dataclasses import dataclass

@dataclass
class A:

    a: int
    b: int

a = A()
print(a)