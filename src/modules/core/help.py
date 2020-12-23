import discord
import socket
from mcipc.rcon import Client

def get_help_str(self, cmds):
    k = list(cmds)
    r = "commands: " + k[0]
    for i in k[1:]:
        r = r + ", " + i
    return r

async def help(dclient, args, message):
    await message.channel.send(dclient.command_handler.command_map.keys())