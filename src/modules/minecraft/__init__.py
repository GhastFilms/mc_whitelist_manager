import os, sys
sys.path.append(os.path.abspath("./src/modules/minecraft/"))
import blacklist
import playercount
import players
import whitelist

from command import ModuleBuilder

def get_module():
    return ModuleBuilder("minecraft", 2).add_command("whitelist", whitelist.get_dir()).build()