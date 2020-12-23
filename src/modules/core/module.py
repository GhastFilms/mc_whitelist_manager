import discord
import socket
import redis

from command import CommandDirBuilder

dir = CommandDirBuilder()
    
@dir.command("list")
async def _list(dclient, args, message):
    l = dclient.command_handler.module_map.values()
    db_conn =  redis.Redis(connection_pool=dclient.db.pool)
    enabled_modules = db_conn.smembers(str(message.guild.id) + "_modules")
    r = ''
    for mod in l:
        is_mod_enabled = ((str.encode(str(mod.module_id)) in enabled_modules) or (mod.module_id == 0))
        r = r + (mod.module_name + ", enabled: " + str(is_mod_enabled)) + "\n"
    await message.channel.send(r)

@dir.command("enable")
async def enable(dclient, args, message):
    x = message.content.split(" ")
    if len(x) < 3:
        await message.channel.send("specifiy modules to enable")
        return
    mod_name = x[2]
    mod_id = None
    for x in dclient.command_handler.module_map.values():
        if x.module_name == mod_name:
            mod_id = x.module_id
    if mod_id != None:
        db_conn = redis.Redis(connection_pool=dclient.db.pool)
        ret = db_conn.sadd((str(message.guild.id) + "_modules"), mod_id)
        if ret == 1:
            await message.channel.send("enabled module")
        else:
            await message.channel.send("module is already enabled")

    else:
        await message.channel.send("unknown module")
        return

@dir.command("disable")
async def disable(dclient, args, message):
    x = message.content.split(" ")
    if len(x) < 3:
        await message.channel.send("specifiy modules to enable")
        return
    mod_name = x[2]
    mod_id = None
    for x in dclient.command_handler.module_map.values():
        if x.module_name == mod_name:
            mod_id = x.module_id
    if mod_id != None:
        db_conn = redis.Redis(connection_pool=dclient.db.pool)
        ret = db_conn.srem((str(message.guild.id) + "_modules"), mod_id)
        if ret == 1:
            await message.channel.send("disabled module")
        else:
            await message.channel.send("module is already disabled")

    else:
        await message.channel.send("unknown module")
        return

def get_dir():
    return dir.build()