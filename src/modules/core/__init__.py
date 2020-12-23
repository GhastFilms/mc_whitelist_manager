import sys
import os
sys.path.append(os.path.abspath("./src/modules/core/"))
import help
import module

from command import ModuleBuilder

def get_module():
    return ModuleBuilder("core", 0).add_command("module", module.get_dir()).add_command("help", help.help).build()