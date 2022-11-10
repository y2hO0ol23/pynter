BYTESIZE = 8

class memory:
    def __init__(self):
        self.space = dict()
        self.set_bit(64)

    def set_bit(self, value):
        self.bit = value
        self.addr_size = value // BYTESIZE

    def check_addr(self, address, type):
        addr_end = (1 << (self.addr_size * BYTESIZE)) - 1
        if address < 0 or addr_end < address + type:
            raise ValueError('address must be 0 to ' + hex(addr_end) + ' with ' + str(self.bit) + ' bit memory')
    
    def addr_lookup(self, address):
        if not self.space.get(address):
            self.space[address] = 0

mem = memory()
