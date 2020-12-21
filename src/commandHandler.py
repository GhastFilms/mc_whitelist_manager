import redis
import redisgraph
import asyncio

import modules.core

from modules import get_modules

class CommandHandler:
    command_map = {}
    module_map = {}
    
    dclient = None

    def __init__(self, dclient):
        self.dclient = dclient

        modules = get_modules()

        for x in modules:
            self.add_module(x)

        h = self.command_map.get('help')
        if h is None:
            print("help command is missing")
            exit(0)
        h.update_help_command(self.command_map)

    def add_module(self, mod):
        mm = mod()
        self.module_map[mm.module_id] = mm
        module_commands = mm.get_commands()
        mod_id = mod.module_id
        for c in module_commands:
            cm = c(self.dclient)
            cm.module_id = mod_id

            self.add_command(c.name, cm)

    def add_command(self, name, com):
        if self.is_command(com):
            if self.command_map.get(name) is None:
                self.command_map[name] = com
            else:
                print("failed to load command " + name + " command already exists")
        else: 
            print("failed to load command " + name + " because it does not have the required attributes to be a command")
    
    def is_command(self, cmd):
        has_run = hasattr(cmd, "run")
        has_name = hasattr(cmd, "name")
        has_permissions  = hasattr(cmd, "required_permissions")

        if has_run and has_name and has_permissions:
            return True
        else: 
            return False

    def get_command(self, command_name, message):
        return ""
    
    async def run_command(self, command_name, message):
        cmd_class = self.command_map.get(command_name)
        if cmd_class is None:
            return 0
        module_enabled = False
        command_module_id = cmd_class.module_id

        if command_module_id == 0:
            module_enabled = True
        
        module_set_name = (str(message.guild.id) +  "_modules")

        db_conn = redis.Redis(connection_pool=self.dclient.db.pool)
        
        pipe = db_conn.pipeline().get("owner_id").exists(module_set_name)

        if command_module_id != 0:
            pipe.sismember(module_set_name, str(command_module_id))

        p = pipe.execute()
        if p[1] == 0:
            default_module_ids = [1,2]
            pipe = db_conn.pipeline()
            for x in default_module_ids:
                pipe.sadd(module_set_name, x)
            pipe.execute()

        owner_id = p[0]

        if command_module_id != 0:
            module_enabled = p[2]


        is_owner = False
        if owner_id is not None:
            if int(owner_id.decode()) == message.author.id:
                is_owner = True
            
        # this is static to administrator permissions as of rn but later most of this will be changed
        
        req_perms = cmd_class.required_permissions

        if is_owner == True:
            await cmd_class.run(message)
            return

        if module_enabled == False:
            await message.channel.send("module is disabled")
            return
        
        if not (((req_perms == 1) and (message.author.guild_permissions.administrator is True)) or (req_perms == 0)):
            await message.channel.send("you dont have perms lol")
            return

        await cmd_class.run(message)