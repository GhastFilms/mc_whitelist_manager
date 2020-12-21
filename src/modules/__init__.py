import sys, os
sys.path.append(os.path.abspath("./src/modules/"))
import core
import minecraft

def get_modules():
    return [core.Module, minecraft.Module]