import os, sys
sys.path.append(os.path.abspath("./src/modules/minecraft/"))
import blacklist
import playercount
import players
import whitelist

class Module:
    module_id = 1
    module_name = "minecraft"

    def get_commands(self):
        return [whitelist.Command]