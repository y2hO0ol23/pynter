from pynter import *
_ = pynter_op_perfix()

v = var(BYTE, 0x1000, [5, 5])

for i in range(5):
    for j in range(5):
        v[i][j] = (i * 5 + j ) *  4

p = var(DWORD,0x2000)
p == 0x1000
print(_*p)
print(_*(BYTE*(_*p) + 1))
print(_*(BYTE*(_*(BYTE*(_*(BYTE*(_*p) + 1)) + p)) + p))