from pynter import *
_ = pynter_op_perfix()
# pynter_op_perfix is for using pointer operating
# use as _*A, _&A

# WORD v = var (&v = 0x1000)
v = var(BYTE, 0x1000)
v == 20
print("_&v :", _&v)
print("v :", v)
print()

# BYTE li[3][5] (li = 0x2000)
li = var(BYTE, 0x2000, [3, 5])
for i in range(3):
    for j in range(5):
        li[i][j] = i*5 + j

print("li[2][4] :", li[2][4])
print("_*(_*(li + 2) + 4):", _*(_*(li + 2) + 4))
print()
print("li[2] :", li[2])
print("_*(li + 2) :",_*(li + 2))
print()
print("li :", li)
print()

# struct s1 {
#   BYTE a1;
#   DWORD a2[5][10];
# } (&s1 = 0x3000)
s = struct(0x3000, a1=BYTE, a2=DWORD+[5, 10])
s.a1 == 12
for i in range(5):
    for j in range(10):
        s.a2[i][j] = i*10 + j

print("s :", s)
print("s.a1 :", s.a1)
print("s.a2 :", s.a2)
print("s.a2[2][7] :", s.a2[2][7])

# DWORD v1 = 0
#
v1 = var(DWORD,0x4000)
v2 = var(DWORD,next(v1))
v1 == 0x1234
v2 == 0x9876

print("_&v1 :", _&v1)
print("_&v2 :", _&v2)
print("v1 + v2 :", hex(v1 + v2))
print("_&v2 - _&v1 :", _&v2 - _&v1)
