from pynter import *
_ = pynter_op_perfix()

li = var(BYTE, 0x1000, [5, 5])

v = struct(0x1000, a1=BYTE, a2=DWORD+[5, 10])
v.a1 == 12
v.a2[0][1] == 0x12345678

print((_&v.a1)[5])