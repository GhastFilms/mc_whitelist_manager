class CommandDir:

    command_map = {}
    def __init__(self, command_map):
        self.command_map = command_map

        return

    def get_command(self, name):
        return self.command_map.get(name)

class Module:
    module_id = None
    module_name = None
    commands = []

    def __init__(self, id, name, commands):
        self.module_id = id
        self.module_name = name
        self.commands = commands
        pass

    def get_commands(self):
        return self.commands

# builders

class ModuleBuilder:
    commands = []

    def __init__(self, name, id):
        self.name = name
        self.id = id

    def add_command(self, name, cmd):
        setattr(cmd, 'module_id', self.id)
        self.commands.append((name, cmd))
        return self

    def build(self):
        return Module(self.id, self.name, self.commands)


class CommandHandler:
    # command_map is a dict which contains nodes, each node is either a command or a dir. 
    dclient = None
    command_map = {}
    module_map = {}

    def __init__(self, dclient, command_map, module_map):
        self.dclient = dclient
        self.command_map = command_map
        self.module_map = module_map

    def get_command(self, msg):
        sp = msg.split(" ")
        sp[0] = sp[0][1:]
        
        command = None
        dep = 1
        cmd_map = self.command_map
        mod_id = None

        for x in sp:
            c = cmd_map.get(x)
            if c is not None:
                if mod_id is None:
                    mod_id = c.module_id
                #command = c
                #print(type(c))
                if isinstance(c, CommandDir):
                    dep = dep + 1
                    cmd_map = c.command_map
                    continue
                if callable(c):
                    command = c
        #print("--------------")
        #print(sp)
        #print(dep)
        #print()
        return (command, sp[dep:], mod_id)


# CommandDir
class CommandDirBuilder:
    command_map = {}

    def __init__(self):
        pass
    
    def add_command(self, name, cmd):
        self.command_map[name] = cmd
        return self
    
    def add_dir(self, cmd_dir):
        self.command_map[cmd_dir]
        return self
    def command(self, name):
        def decorator(f):
            self.command_map[name] = f
        return decorator

    def build(self):
        return CommandDir(self.command_map)

    #def get_commands(self):
    #    return self.command_map
    

class CommandHandlerBuilder:
    dclient = None
    command_map = {}
    module_map = {}

    def __init__(self, dclient):
        self.dclient = dclient
    

    def add_module(self, module):
        self.module_map[module.module_id] = module
        module_commands = module.get_commands()
        mod_id = module.module_id
        for (n,c) in module_commands:
            c.module_id = mod_id
            self.command_map[n] = c
        return self


    def build(self):
        return CommandHandler(self.dclient, self.command_map, self.module_map)
