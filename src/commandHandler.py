

import os
import sys

# command imports
sys.path.append(os.path.abspath("./src/commands/"))
import blacklist
import help
import playercount
import players
import whitelist
import redis

class CommandHandler:
    command_map = {}
    
    dclient = None

    def __init__(self, dclient):
        self.dclient = dclient


    def load_commands(self):
        x = [
              ("blacklist", blacklist.Command),
              ("help", help.Command),
              ("playercount", playercount.Command),
              ("players", players.Command),
              ("whitelist", whitelist.Command)
            ]
        for y in x:
            self.add_command(y[0], y[1], self.dclient)

    def add_command(self, name, com, dclient):
        if self.is_command(com):
            if self.command_map.get(name) is None:
                self.command_map[name] = com(dclient)
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
    
    async def run_command(self, command_name, message):
        db_conn = redis.Redis(connection_pool=self.dclient.db.pool)
        id = db_conn.get("owner_id")
        is_owner = False
        if id is not None:
            if int(id.decode()) == message.author.id:
                is_owner = True
            

        #db_conn.set("x", 3)

        cmd_class = self.command_map.get(command_name)
        if cmd_class is None:
            return 0
        # this is static to administrator permissions as of rn but later most of this will be changed
        
        req_perms = cmd_class.required_permissions

        if (((req_perms == 1) and (message.author.guild_permissions.administrator is True)) or (req_perms == 0)) or is_owner == True:
            await cmd_class.run(message)
'''
command:
    module_id: string
    name: string
    default permission: enum
    

'''