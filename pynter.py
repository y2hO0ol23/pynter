
class var(): ...
class pynter_op_perfix(): ...
class var_type(): ...
class struct(): ...

import memory

def _change_to_int(v):
    try: 
        return int(v)
    except: 
        raise TypeError("can't exchange", type(v), "to 'int'")

class use_int_for_compare():
    def __bool__(self):
        raise TypeError("'var' use == operator for modifying value")

class var():
    def __init__(self, vtype, address, size: list = []):
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
            ValueError("need type conversion")
        
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
        
    
    def __getitem__(self, offset):
        offset = _change_to_int(offset)

        if not self.is_ptr():
            addr = self.value() + offset * self.addr_interval
            memory.mem.check_addr(addr,self.type)
            return var(0, addr)
        else:
            addr = self.addr + offset * self.addr_interval
            memory.mem.check_addr(addr,self.type)
            return var(self.type, addr, self.size[1:])
    

    def bitmask(self):
        return (1 << (memory.BYTESIZE * self.type)) - 1


    def __setitem__(self, offset, value):
        offset = _change_to_int(offset)

        if len(self.size) == 1:
            value = _change_to_int(value) & self.bitmask()
            value = value.to_bytes(self.type,'little')
            addr = self.addr + offset * self.type
            
            for i in range(self.type):
                memory.mem.space[addr + i] = value[i]

        else:
            raise TypeError("is not a modifiable value")

    def set(self, other):
        if not self.is_ptr():
            value = _change_to_int(other) & self.bitmask()
            value = value.to_bytes(self.type,'little')

            for i in range(self.type):
                memory.mem.space[self.addr + i] = value[i]
            
        else:
            raise TypeError("is not a modifiable value")
        
        return use_int_for_compare()
    __eq__ = lambda self, other: self.set(other)
    
    def __add__(self, other):
        other = _change_to_int(other)
        if not self.is_ptr():
            return int(self) + other
        else:
            return var(self.type, self.addr + self.addr_interval * other, self.size)
    __radd__ = lambda self, other: self.__add__(other)

    def __repr__(self):
        if not self.is_ptr():
            return "var(value=" + hex(int(self)) + ")"
        else:
            return "var(address=" + hex(int(self)) + ")"


# for * and & 
class pynter_op_perfix():
    def __init__(self):
        self.reset()
    

    def reset(self):
        self.value = 0
        self.last_operator = "+"
        
    # _*()
    def __mul__(self, other: var):
        if type(other) == var:
            if other.is_ptr():
                newvar = var(other.type, int(other))
            else:
                newvar = var(other.type, int(other), [1])
        else:
            raise TypeError("x type must be 'var' in _*x operation")
        ret = eval("self.value "+self.last_operator+" newvar")
        self.reset()
        return ret


    # _&()
    def __and__(self,other: var):
        newvar = var(other.type, other.addr, [1])
        ret = eval("self.value "+self.last_operator+" newvar")
        self.reset()
        return ret


    def set(self, other, operator):
        self.value = other
        self.last_operator = operator
        return self

    # when 10 * _*a1 => 10 * _ will calculate first
    __rmul__        = lambda self, other: self.set(other, "*")
    __rmatmul__     = lambda self, other: self.set(other, "@")
    __rtruediv__    = lambda self, other: self.set(other, "/")
    __rfloordiv__   = lambda self, other: self.set(other, "//")
    __rmod__        = lambda self, other: self.set(other, "%")
    __rpow__        = lambda self, other: self.set(other, "**")

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
    def __mul__(self, dat):
        return var(self.type, int(dat), [1])

    def __add__(self, dat):
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

def memcpy(dest, src, count):
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
    else:
        return len(v)


class struct:
    def __init__(self, address, **items):
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