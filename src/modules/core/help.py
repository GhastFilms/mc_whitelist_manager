import discord
import socket
from mcipc.rcon import Client

class Command:

    name = 'help'

    required_permissions = 0

    dclient = None

    help_string = ''

    def __init__(self, dclient):
        self.dclient = dclient

    def update_help_command(self, cmds):
        k = list(cmds)
        r = "commands: " + k[0]
        for i in k[1:]:
            r = r + ", " + i
        self.help_string = r

    async def run(self, message):
        await message.channel.send(self.help_string)