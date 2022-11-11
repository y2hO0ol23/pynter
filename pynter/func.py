function_to_address = dict()
address_to_function = dict()

class func():
    def __init__(self, function, address):
        self.func = function
        pass

    def __call__(self, *args, **kwds):
        parameter = "".join(["args[%d],"%i for i in range(len(args))])
        keys = kwds.keys()
        parameter += "".join(["%s=kwds[%s],"%(key,key) for key in kwds.keys()])
        
        return eval("self.func("+parameter+")")
