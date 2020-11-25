import discord
import socket
from mcipc.rcon import Client
from datetime import date
import logging
import json
import requests
import re

class Command:

    name = 'whitelist'

    required_permissions = 1

    dclient = None

    def __init__(self, dclient):
        self.dclient = dclient

    async def run(self, message):
        
        x = message.content.split(" ")

        #if len(x) >= 4:
        #    end = re.search("as <(@\![1-9]*)>", x[-2] + " " + x[-1])
        #    print(x[-2] + " " + x[-1])
        #    print(x[:-2][2:])

        
    #async def add(self, message, player, disc_id):

        if len(x) < 2:
            await message.channel.send("provide a username to whitelist")
            return

        y = mc_name_to_uuid(player)
        
        if y is None:
            await message.channel.send("%s is not a valid minecraft username" % x[1]) 
            return
        
        player_uuid = y[0]
        player_name = y[1]            

        try:
            conn = self.dclient.db.pool.getconn()

            ret_msg = ''
        
            if conn:
                
                cur = conn.cursor()

                w = mc_uuids(conn, cur,message.author.id)

                if w is not None:
                    id = w[0]
                    uuid = w[1]

                    if player_uuid not in uuid:
                        uuid_str = ''
                        if len(uuid) == 1:
                            uuid_str = uuid[0] + "," + player_uuid
                        else:
                            uuid_str = uuid[0]
                            for x in uuid[1:]:
                                uuid_str = uuid_str + "," + x
                            uuid_str = uuid_str + "," + player_uuid

                            print(uuid_str)

                        cur.execute("UPDATE users SET mc_uuid = '{0}' WHERE id = {1};".format(uuid_str, str(id)))

                        ret_msg = "Added {0} to the whitelist"
                    else:
                        ret_msg = "{0} is already on the whitelist"
                    
                else:
                    cur.execute("INSERT INTO Users(discord_id, mc_uuid) VALUES ({0}, {1});".format(str(message.author.id), player_uuid))
                    ret_msg = "Added {0} to the whitelist"
                        
                conn.commit() 
            else:
                raise Exception("failed to get db connection from pool")

        except Exception as err:
            logging.error("Error occured while attemping to whitelist {0}, error: {1}".format(player_name, err))
            ret_msg = "An error occured while trying to whitelist {0}, try again later"
        finally:
            cur.close()
            self.dclient.db.pool.putconn(conn)
            await message.channel.send(ret_msg.format(player_name))
        
        #try:
        #    with Client(conf.RCON_HOST, conf.RCON_PORT) as c:
        #        if not c.login(conf.RCON_PASSWORD):
        #            print("Failed to login to the minecraft server")
        #            await message.channel.send("Failed to login to the minecraft , try again later")
        #        else:
        #            r = c.run("whitelist add " + player)
        #            await message.channel.send(r)
        #except socket.timeout:
        #    print("Connection to the minecraft server timed out after")
        #    await message.channel.send("Connection to the minecraft server timed out")

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