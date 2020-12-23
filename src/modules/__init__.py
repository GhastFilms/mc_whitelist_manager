import sys, os
sys.path.append(os.path.abspath("./src/modules/"))
import core
import minecraft

import command

def get_modules():
    #return [core.get_module(), minecraft.get_module()]
    return [core.get_module(), minecraft.get_module()]