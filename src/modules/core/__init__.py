import sys
import os
sys.path.append(os.path.abspath("./src/modules/core/"))
import help
import module

class Module:
    module_id = 0
    module_name = "core"

    def get_commands(self):
        return [help.Command, module.Command]