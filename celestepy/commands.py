class Commands:
    def __init__(self, prefix):
        self.prefix = prefix
        self.commands = {}
    def _init(self,instance):
        funcs = dir(self)
        for func in funcs:
            if (func.startswith("__") == True) and (func.endswith("__") == True):
                pass
            else:
                f = getattr(self, func)
                
                self.commands[func] = {"name":func,"function":f,"instance":instance}
