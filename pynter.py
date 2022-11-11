
class var(): ...
class pynter_op_perfix(): ...
class var_type(): ...
class struct(): ...

def memcpy(dest, src, count: int): ...
def sizeof(v): ...

import memory

def _change_to_int(v):
    try: 
        return int(v)
    except: 
        raise TypeError("can't exchange " + type(v).__name__ + " to 'int'")

class use_int_for_compare():
    def __bool__(self):
        raise TypeError("'var' use == operator for modifying value")

OPER_ADDR_TO_ADDR = 1 << 0
OPER_ADDR_TO_INT = 1 << 1
OPER_INT_TO_ADDR = 1 << 2
class var():
    def __init__(self, vtype: var_type, address: int, size: list = []): ...
    def __getattribute__(self, item): ...
    def __int__(self): ...
    def __getitem__(self, offset: int): ...
    def __setitem__(self, offset, value: int): ...   
    def __repr__(self): ... 

    def is_ptr(self): ...
    def value(self): ...
    def bitmask(self): ...
    def set(self, other: int): ...
    def oper(self, oper: str, other, option: int = 0): ...
    def roper(self, oper: str, other, option: int = 0): ...


    def __init__(self, vtype: var_type, address: int, size: list = []):
        # about type
        if type(vtype) == var_type:
            self.type = vtype.type
        else:
            self.type = _change_to_int(vtype)

            if self.type < 0:
                raise TypeError("type must bigger than 0")

        # about address
        address = _change_to_int(address)

        memory.mem.check_addr(address, self.type)
        self.addr = address
        
        # about size
        if type(size) != list:
            raise IndexError('size must be list not '+str(type(size))+"")

        self.addr_interval = self.type
        self.size = size

        if len(size) == 0:
            pass
        else:
            for i in range(len(size)):
                size[i] = _change_to_int(size[i])
                if size[i] < 1: 
                        raise IndexError('size of array must bigger than 0.')
                if i != 0: 
                    self.addr_interval *= size[i]
                    
    
    def __getattribute__(self, item):
        if super().__getattribute__('type') == 0:
            raise ValueError("need type conversion")
        
        return super().__getattribute__(item)


    def is_ptr(self):
        return len(self.size) != 0


    def value(self):
        value = 0
        for i in reversed(range(self.type)):
            value *= 0x100
            memory.mem.addr_lookup(self.addr + i)
            value += memory.mem.space[self.addr + i]
        return value


    def __int__(self):
        if len(self.size) != 0:
            return self.addr
        return self.value()
        
    
    def __getitem__(self, offset: int):
        offset = _change_to_int(offset)

        if not self.is_ptr():
            addr = self.val() + offset * self.addr_interval
            memory.mem.check_addr(addr,self.type)
            return var(0, addr)
        else:
            addr = self.addr + offset * self.addr_interval
            memory.mem.check_addr(addr,self.type)
            return var(self.type, addr, self.size[1:])
    

    def bitmask(self):
        return (1 << (memory.BYTESIZE * self.type)) - 1


    def __setitem__(self, offset, value: int):
        offset = _change_to_int(offset)

        if len(self.size) == 1:
            value = _change_to_int(value) & self.bitmask()
            value = value.to_bytes(self.type,'little')
            addr = self.addr + offset * self.type
            
            for i in range(self.type):
                memory.mem.space[addr + i] = value[i]

        else:
            raise TypeError("is not a modifiable value")

    def set(self, other: int):
        if not self.is_ptr():
            value = _change_to_int(other) & self.bitmask()
            value = value.to_bytes(self.type,'little')

            for i in range(self.type):
                memory.mem.space[self.addr + i] = value[i]
            
        else:
            raise TypeError("is not a modifiable value")
        
        return use_int_for_compare()
    __eq__ = lambda self, other: self.set(other)


    def __repr__(self):
        if not self.is_ptr():
            return "var(value=" + hex(int(self)) + ")"
        else:
            return "var(address=" + hex(int(self)) + ")"

    def oper(self, oper: str, other, option: int = 0):
        if type(other) == pynter_op_perfix:
            return pynter_op_perfix(True, self, oper)

        def error(type):
            if type == 0: raise ValueError("operation for address should match type and size for " + oper)
            if type == 1: raise ValueError("unsupported operation : " + self.__repr__() + " " + oper + " " + other.__repr__())

        if self.is_ptr():
            if type(other) == var and other.is_ptr():
                if not option & OPER_ADDR_TO_ADDR:
                    error(0)
                if not (self.size == other.size and self.size == other.size):
                    error(1)
                return eval("int(self)" + oper + "int(other)") // self.type

            if not option & OPER_ADDR_TO_INT:
                error(0)
            other = _change_to_int(other)
            return var(self.type, eval("self.addr" + oper + "self.addr_interval * other"), self.size)
        
        else:
            if type(other) == var and other.is_ptr():
                return eval('int(self)' + oper + 'other')
            
            other = _change_to_int(other)
            return eval('int(self)' + oper + 'other')
                
    __add__     = lambda self, other: self.oper("+", other, OPER_ADDR_TO_INT | OPER_INT_TO_ADDR)
    __sub__     = lambda self, other: self.oper("-", other, OPER_ADDR_TO_ADDR | OPER_ADDR_TO_INT)
    __mul__     = lambda self, other: self.oper("*", other)
    __pow__     = lambda self, other: self.oper("**",other)
    __truediv__ = lambda self, other: self.oper("/", other)
    __floordiv__= lambda self, other: self.oper("//",other)
    __mod__     = lambda self, other: self.oper("%", other)
    __lshift__  = lambda self, other: self.oper("<<",other)
    __rshift__  = lambda self, other: self.oper(">>",other)
    __and__     = lambda self, other: self.oper("&", other)
    __or__      = lambda self, other: self.oper("|", other)
    __xor__     = lambda self, other: self.oper("^", other)
    __invert__  = lambda self, other: self.oper("~", other)


    def roper(self, oper: str, other, option: int = 0):
        if self.is_ptr():
            if not option & OPER_INT_TO_ADDR:
                raise ValueError("unsupported operation : " + other.__repr__() + " " + oper + " " + self.__repr__())
                
            other = _change_to_int(other)
            return var(self.type, eval("self.addr_interval * other"  + oper + "self.addr"), self.size)
        else:
            other = _change_to_int(other)
            return eval('int(self)' + oper + 'other')

    __radd__     = lambda self, other: self.roper("+", other, OPER_ADDR_TO_INT | OPER_INT_TO_ADDR)
    __rsub__     = lambda self, other: self.roper("-", other, OPER_ADDR_TO_ADDR | OPER_ADDR_TO_INT)
    __rmul__     = lambda self, other: self.roper("*", other)
    __rpow__     = lambda self, other: self.roper("**",other)
    __rtruediv__ = lambda self, other: self.roper("/", other)
    __rfloordiv__= lambda self, other: self.roper("//",other)
    __rmod__     = lambda self, other: self.roper("%", other)
    __rlshift__  = lambda self, other: self.roper("<<",other)
    __rrshift__  = lambda self, other: self.roper(">>",other)
    __rand__     = lambda self, other: self.roper("&", other)
    __ror__      = lambda self, other: self.roper("|", other)
    __rxor__     = lambda self, other: self.roper("^", other)
    __rinvert__  = lambda self, other: self.roper("~", other)


    def __next__(self):
        return self.addr + sizeof(self)


# for * and & 
class pynter_op_perfix():
    def __init__(self, operation=False, value=None, operator=None):
        self.run = operation
        self.val = value
        self.oper = operator
        
    # _*()
    def __mul__(self, other: var):
        if type(other) == var:
            if other.is_ptr():
                ret = var(other.type, int(other), other.size[1:])
            else:
                ret = var(other.type, int(other), [1])
        else:
            raise TypeError("x type must be 'var' in _*x operation not "+str(type(other)))

        if self.run:
            ret = eval("self.val "+self.oper+" ret")

        return ret


    # _&()
    def __and__(self, other):
        # when _&a + _&b
        # 1. a + _
        # 2. _& (a + _)
        # 3. (_& (a + _)) & b
        # so if perfix & perfix self.val = _&a
        # 1
        if type(other) == pynter_op_perfix:
            if other.run:
                value = var(other.val.type, other.val.addr, [1])
                operator = other.oper
                return pynter_op_perfix(True, value, operator)
            else:
                raise TypeError("unsupported operand type(s) for &: 'pynter_op_perfix' and 'pynter_op_perfix'")
        else:
            ret = var(other.type, other.addr, [1])
            if self.run:
                ret = eval("self.val "+self.oper+" ret")

            return ret

    def __call__(self, dat):
        return dat
        

# types ()
class var_type:
    def __init__(self, vtype):
        if type(vtype) == int:
            self.type = vtype
        else:
            self.type = vtype()

    # BYTE*_(asdf)
    def __mul__(self, dat: int):
        return var(self.type, int(dat), [1])

    def __add__(self, dat: list):
        if type(dat) != list:
            raise TypeError("'dat' must be 'list' type")
        return (self, dat)
    
    def __call__(self, dat):
        if type(dat) != var and not dat.is_ptr():
            return var(self.type, dat.addr)
        else:
            return int(dat) & var(self.type,0).bitmask()
            

BYTE =  var_type(1)
WORD =  var_type(2)
DWORD = var_type(4)
QWORD = var_type(8)

class struct:
    def __init__(self, address: int, **items):
        self.size = 0
        if len(items) == 0:
            raise TypeError('no items found')
        for key in items.keys():
            if type(items[key]) == tuple:
                vtype = items[key][0]
                arg3  = items[key][1]
            else:
                vtype = items[key]
                arg3 = []

            newaddr = address + self.size
            memory.mem.check_addr(newaddr, vtype.type)
            newattr = var(vtype, newaddr, arg3)
            setattr(self, key, newattr)
            self.size += sizeof(newattr)
    
    def __repr__(self):
        return "struct(size=" + str(self.size) + ")"


def memcpy(dest, src, count: int):
    dest = var(BYTE,int(dest),[count])
    try:
        src = var(BYTE,int(src),[count])
    except: 
        if len(src) < count:
            raise IndexError("'len(src)' must greater than or equal to 'count'")

    for i in range(count):
        dest[i] = src[i]


def sizeof(v):
    if type(v) == var:
        if len(v.size) == 0:
            return v.type
        else:
            return v.type * v.addr_interval * v.size[0]
    elif type(v) == var_type:
        return v.type
    elif type(v) == struct:
        return v.size
    else:
        return len(v)
