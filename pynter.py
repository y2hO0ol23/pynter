
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
    def __bitmask(self): ...
    def set(self, other: int): ...
    def __oper(self, oper: str, other, option: int = 0): ...
    def __roper(self, oper: str, other, option: int = 0): ...


    def __init__(self, vtype: var_type, address: int, size: list = []):
        # about type
        if type(vtype) == var_type:
            self.__type = vtype._var_type__type
        else:
            self.__type = _change_to_int(vtype)

            if self.__type < 0:
                raise TypeError("type must bigger than 0")

        # about address
        address = _change_to_int(address)

        memory.mem.check_addr(address, self.__type)
        self.__addr = address
        
        # about size
        if type(size) != list:
            raise IndexError('size must be list not '+str(type(size))+"")

        self.__addr_interval = self.__type
        self.__size = size

        if len(size) == 0:
            pass
        else:
            for i in range(len(size)):
                size[i] = _change_to_int(size[i])
                if size[i] < 1: 
                        raise IndexError('size of array must bigger than 0.')
                if i != 0: 
                    self.__addr_interval *= size[i]
                    
    
    def __getattribute__(self, item):
        if super().__getattribute__('_var__type') == 0:
            raise ValueError("need type conversion")
        
        return super().__getattribute__(item)


    def is_ptr(self):
        return len(self.__size) != 0


    def __int__(self):
        if len(self.__size) != 0: return self.__addr

        value = 0
        for i in reversed(range(self.__type)):
            value *= 0x100
            memory.mem.addr_lookup(self.__addr + i)
            value += memory.mem.space[self.__addr + i]

        return value
        
    
    def __getitem__(self, offset: int):
        offset = _change_to_int(offset)

        if not self.is_ptr():
            addr = self.val() + offset * self.__addr_interval
            memory.mem.check_addr(addr,self.__type)
            return var(0, addr)
        else:
            addr = self.__addr + offset * self.__addr_interval
            memory.mem.check_addr(addr,self.__type)
            return var(self.__type, addr, self.__size[1:])
    

    def __bitmask(self):
        return (1 << (memory.BYTESIZE * self.__type)) - 1


    def __setitem__(self, offset, value: int):
        if len(self.__size) != 1:
            raise TypeError("is not a modifiable value")

        offset = _change_to_int(offset)
        value = _change_to_int(value) & self.__bitmask()
        value = value.to_bytes(self.__type,'little')
        addr = self.__addr + offset * self.__type
        memory.mem.check_addr(addr, self.__type)

        for i in range(self.__type):
            memory.mem.space[addr + i] = value[i]


    def set(self, other: int):
        if self.is_ptr():
            raise TypeError("unable to set or compare address data")

        value = _change_to_int(other) & self.__bitmask()
        value = value.to_bytes(self.__type,'little')

        for i in range(self.__type):
            memory.mem.space[self.__addr + i] = value[i]
        
        return int(self)
    
    __eq__ = lambda self, other: self.set(other)


    def __repr__(self):
        if not self.is_ptr():
            return "var(value=" + hex(int(self)) + ")"
        else:
            return "var(address=" + hex(int(self)) + ")"

    def __oper(self, oper: str, other, option: int = 0):
        if type(other) == pynter_op_perfix:
            return pynter_op_perfix(True, self, oper)

        def error(type):
            if type == 0: raise ValueError("operation for address should match type and size for " + oper)
            if type == 1: raise ValueError("unsupported operation : " + self.__repr__() + " " + oper + " " + other.__repr__())

        if self.is_ptr():
            if type(other) == var and other.is_ptr():
                if not option & OPER_ADDR_TO_ADDR:
                    error(0)
                if not (self.__size == other.__size and self.__size == other.__size):
                    error(1)
                return eval("int(self)" + oper + "int(other)") // self.__type

            if not option & OPER_ADDR_TO_INT:
                error(0)
            other = _change_to_int(other)
            return var(self.__type, eval("self._var__addr" + oper + "self._var__addr_interval * other"), self.__size)
        
        else:
            if type(other) == var and other.is_ptr():
                return eval('int(self)' + oper + 'other')
            
            other = _change_to_int(other)
            return eval('int(self)' + oper + 'other')
                
    __add__     = lambda self, other: self.__oper("+", other, OPER_ADDR_TO_INT | OPER_INT_TO_ADDR)
    __sub__     = lambda self, other: self.__oper("-", other, OPER_ADDR_TO_ADDR | OPER_ADDR_TO_INT)
    __mul__     = lambda self, other: self.__oper("*", other)
    __pow__     = lambda self, other: self.__oper("**",other)
    __truediv__ = lambda self, other: self.__oper("/", other)
    __floordiv__= lambda self, other: self.__oper("//",other)
    __mod__     = lambda self, other: self.__oper("%", other)
    __lshift__  = lambda self, other: self.__oper("<<",other)
    __rshift__  = lambda self, other: self.__oper(">>",other)
    __and__     = lambda self, other: self.__oper("&", other)
    __or__      = lambda self, other: self.__oper("|", other)
    __xor__     = lambda self, other: self.__oper("^", other)
    __invert__  = lambda self, other: self.__oper("~", other)


    def __roper(self, oper: str, other, option: int = 0):
        if self.is_ptr():
            if not option & OPER_INT_TO_ADDR:
                raise ValueError("unsupported operation : " + other.__repr__() + " " + oper + " " + self.__repr__())
                
            other = _change_to_int(other)
            return var(self.__type, eval("self._var__addr_interval * other"  + oper + "self._var__addr"), self.__size)
        else:
            other = _change_to_int(other)
            return eval('int(self)' + oper + 'other')

    __radd__     = lambda self, other: self.__roper("+", other, OPER_ADDR_TO_INT | OPER_INT_TO_ADDR)
    __rsub__     = lambda self, other: self.__roper("-", other, OPER_ADDR_TO_ADDR | OPER_ADDR_TO_INT)
    __rmul__     = lambda self, other: self.__roper("*", other)
    __rpow__     = lambda self, other: self.__roper("**",other)
    __rtruediv__ = lambda self, other: self.__roper("/", other)
    __rfloordiv__= lambda self, other: self.__roper("//",other)
    __rmod__     = lambda self, other: self.__roper("%", other)
    __rlshift__  = lambda self, other: self.__roper("<<",other)
    __rrshift__  = lambda self, other: self.__roper(">>",other)
    __rand__     = lambda self, other: self.__roper("&", other)
    __ror__      = lambda self, other: self.__roper("|", other)
    __rxor__     = lambda self, other: self.__roper("^", other)
    __rinvert__  = lambda self, other: self.__roper("~", other)


    def __next__(self):
        return self.__addr + sizeof(self)


# for * and & 
class pynter_op_perfix():
    def __init__(self, operation=False, value=None, operator=None): ...
    def __mul__(self, other: var): ...
    def __and__(self, other): ...
    def __call__(self, dat): ...


    def __init__(self, operation=False, value=None, operator=None):
        self.__run = operation
        self.__val = value
        self.__oper = operator
        
    # _*()
    def __mul__(self, other: var):
        if type(other) == var:
            if other.is_ptr():
                ret = var(other._var__type, int(other), other._var__size[1:])
            else:
                ret = var(other._var__type, int(other), [1])
        else:
            raise TypeError("x type must be 'var' in _*x operation not "+str(type(other)))

        if self.__run:
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
            if other.__run:
                value = var(other.__val._var__type, other.__val._var__addr, [1])
                operator = other.__oper
                return pynter_op_perfix(True, value, operator)
            else:
                raise TypeError("unsupported operand type(s) for &: 'pynter_op_perfix' and 'pynter_op_perfix'")
        
        if type(other) == struct:
            ret = var(memory.mem.addr_size, other._struct__addr, [1])
        else:
            ret = var(other._var__type, other._var__addr, [1])

        if self.__run:
            ret = eval("self._pynter_op_perfix__val "+self.__oper+" ret")

        return ret


    def __call__(self, dat):
        return dat
        

# types ()
class var_type:
    def __init__(self, vtype): ...
    def __mul__(self, dat: int): ...
    def __add__(self, dat: list): ...
    def __call__(self, dat): ...


    def __init__(self, vtype):
        if type(vtype) == var_type:
            self.__type = vtype()
        else:
            self.__type = _change_to_int(vtype)

    # BYTE*_(asdf)
    def __mul__(self, dat: int):
        return var(self.__type, int(dat), [1])

    def __add__(self, dat: list):
        if type(dat) != list:
            raise TypeError("'dat' must be 'list' type")
        return (self, dat)
    
    def __call__(self, dat):
        if type(dat) != var and not dat.is_ptr():
            return var(self.__type, dat._var__addr)
        else:
            return int(dat) & var(self.__type,0)._var__bitmask()
            

BYTE =  var_type(1)
WORD =  var_type(2)
DWORD = var_type(4)
QWORD = var_type(8)

class struct:
    def __init__(self, address: int, **items): ...
    def __repr__(self): ...
    def __next__(self): ...
    def item(self): ...


    def __init__(self, address: int, **items):
        self.__addr = _change_to_int(address)
        self.__size = 0
        self.__items = items

        if len(items) == 0:
            raise TypeError('no items found')
        for key in items.keys():
            if type(items[key]) == tuple:
                vtype = items[key][0]
                arg3  = items[key][1]
            else:
                vtype = items[key]
                arg3 = []

            newaddr = address + self.__size
            memory.mem.check_addr(newaddr, vtype._var_type__type)
            newattr = var(vtype, newaddr, arg3)
            setattr(self, key, newattr)
            self.__size += sizeof(newattr)
    

    def __repr__(self):
        return "struct(size=" + str(self.__size) + ")"


    def __next__(self):
        return self.__addr + sizeof(self)

        
    def item(self):
        return self.__items


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
        if len(v._var__size) == 0:
            return v._var__type
        else:
            return v._var__type * v._var__addr_interval * v._var__size[0]
    elif type(v) == var_type:
        return v._var_type__type
    elif type(v) == struct:
        return v._struct__size
    else:
        return len(v)
