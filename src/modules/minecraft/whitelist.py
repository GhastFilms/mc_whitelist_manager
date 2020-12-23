import discord
import socket
import logging
import json
import requests
import re
import redis
from redisgraph import Node, Edge, Graph, Path
from mcipc.rcon import Client
from datetime import date
import time

from command import CommandDirBuilder

dir = CommandDirBuilder()
    
# %whitelist add {} as {@}
@dir.command("add")
async def add(dclient, args, message):
    disc_id_search = re.search(r" as <\@\![0-9]*>", message.content)
    uname_search = re.search(r"\b\ add\ \w+\ as\b ", message.content)

    disc_id = None
    player = None
    
    if disc_id_search is not None:
        disc_id = disc_id_search.group()[7:][:-1]
    else:
        await message.channel.send("could not find the discord id in the message")
        return
    
    if uname_search is not None:
        player = uname_search.group()[5:][:-4]
    else:
        await message.channel.send("could not find the username in the message")
        return
        
    # get the uuid of the given username and stop if its not a valid username
    y = mc_name_to_uuid(player)
        
    if y is None:
        await message.channel.send("%s is not a valid minecraft username" % player) 
        return
        
    player_uuid = y[0]
    player_name = y[1]            

    try:
        conn = redis.Redis(connection_pool=dclient.db.pool)
            
        ret_msg = ''
        
        if conn:
            g = Graph('Users', conn)

            params = {'mc_uuid': player_uuid, 'discord_id': str(disc_id), 'mc_name': player_name}


            ret = g.query("""
                OPTIONAL MATCH (m:McAccount {uuid:$mc_uuid})
                OPTIONAL MATCH (u:User {id:$discord_id})
                OPTIONAL MATCH (u)-[o:owns]->(m)
                RETURN u, m, o
            """, params)

            x = ret.result_set[0]
            u = x[0]
            m = x[1]
            i = x[2]
            db_query = ''

            if u is not None:
                db_query = db_query + 'MATCH (u:User {id:$discord_id})\n'
            if m is not None:
                db_query = db_query + 'MATCH (m:McAccount {uuid:$mc_uuid, name:$mc_name})\n'

            if u is None:
                db_query = db_query + 'CREATE (u:User {id:$discord_id})\n'
            if m is None:
                db_query = db_query + 'CREATE (m:McAccount {uuid:$mc_uuid, name:$mc_name})\n'
                
                
            if i is not None:
                if (u is None) or (m is None):
                    g.query(db_query, params)
                    g.commit()
                ret_msg = "{0} is on the whitelist"
            else: 
                db_query = db_query + 'CREATE (u)-[:owns]->(m)'
                g.query(db_query, params)
                g.commit()
                ret_msg = "Added {0} to the whitelist"
                
            if (m is None) or (m is None) or (i is None):
                conn.set("last_whitelist_update", str(time.time()))
                
        else:
            raise Exception("failed to get db connection from pool")

    except Exception as err:
        logging.error("Error occured while attemping to whitelist {0}, error: {1}".format(player_name, err))
        ret_msg = "An error occured while trying to whitelist {0}, try again later"
    finally:
        conn.close()
        await message.channel.send(ret_msg.format(player_name))
        
        
# ^ whitelist remove
@dir.command("remove")
async def remove(dclient, args, message):
    uname_search = message.content[18:]

    player = None

    if uname_search is not None:
        player = uname_search
    else:
        await message.channel.send("could not find the username in the message")
        return

    y = mc_name_to_uuid(player)
        
    if y is None:
        await message.channel.send("%s is not a valid minecraft username" % player) 
        return

    player_uuid = y[0]
    player_name = y[1]
        
    try:
        conn = redis.Redis(connection_pool=dclient.db.pool)
            
        ret_msg = ''
        
        if conn:
            g = Graph('Users', conn)
            params = {'mc_uuid': player_uuid}

            ret = g.query("MATCH (:User)-[o:owns]->(:McAccount {uuid:$mc_uuid}) DELETE o", params)

            if len(ret.result_set):
                ret_msg = "eee"
                    
            else:
                ret_msg = "Removed {0} from the whitelist"
                
            g.commit()
            conn.set("last_whitelist_update", str(time.time()))
                
        else:
            raise Exception("failed to get db connection from pool")

    except Exception as err:
        logging.error("Error occured while attemping to remove {0} from the whitelist, error: {1}".format(player_name, err))
        ret_msg = "An error occured while trying to remove {0} from the whitelist, try again later"
    finally:
        conn.close()
        await message.channel.send(ret_msg.format(player_name))

# returns None if there are no uuids, returns an tuple  of type (int, []) where the int is the users id and the list is a list of strings which are the uuids
def mc_uuids(conn, cur, disc_id):
    cur.execute("SELECT id, mc_uuid FROM users WHERE discord_id = '{0}';".format(str(disc_id)))
    res = cur.fetchall()
    if len(res) == 0:
        return None
    else:
        unames = res[0][1]
        x = unames.split(",")
        return (res[0][0], x)

# returns None if there is no match or a uuid as a string
def mc_name_to_uuid(name): 
    r = requests.get( url = ("https://api.mojang.com/users/profiles/minecraft/{0}".format(name)))
    if r.status_code == 200:
        return (r.json()["id"], r.json()["name"])
    else:
        return None

# returns None if there is no match if there is a match as tuple with the first element being the uuid and the second being the username
def mc_uuid_to_name(uuid):
    r = requests.get(url = ("https://api.mojang.com/user/profiles/{0}/names".format(uuid)))
    if r.status_code == 200:
        return (uuid, r.json()[-1]["name"])
    else:
        return None

def get_dir():
    return dir.build()