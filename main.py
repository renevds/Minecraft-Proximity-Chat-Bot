import discord
import json
import requests
import base64
import mcprofilepic
import math
import asyncio
import dynmapstealer

modID = 754694272627900456

def getinfo():
    url = 'https://api.mcsrvstat.us/2/mc.bavo.life'
    return json.loads(requests.get(url).content)

def serverOnline():
    return getinfo()["online"]

prefix = "mc"
client = discord.Client()

@client.event
async def on_ready():
    print('minecraft bot ready'.format(client))

@client.event
async def on_message(message):
    if not serverOnline() and message.content.startswith(prefix):
        await message.channel.send("Server is offline, no info available")
    if message.content.startswith(prefix):
        #players
        if message.content.startswith(prefix + " players"):
            info = getinfo()
            if "list" in info["players"]:
                players = info["players"]["list"]
                hostname = info["hostname"]
                embed = discord.Embed(title="there are currently " + str(info["players"]["online"]) + " players online", description="", color=0x7a2614)
                writeImage()
                embed.set_thumbnail(url="attachment://server.png")
                txt = ""
                for i in players:
                    txt += "- " + i + "\n"
                embed.add_field(name="Online Players:\n", value=txt)
                with open("server.png", "rb") as image:
                    file = discord.File(image)
                await message.channel.send(embed=embed, file = file)
            else:
                await  message.channel.send("no players online currently")
        #help
        if message.content.startswith(prefix + " help"):
            txt = "**players** to list all players\n"
            txt += "**status** to get a short status\n"
            txt += "**details** to get a detailed status\n"
            txt += "**connect** to connect mc account to discord account\n"
            txt += "**me** to see your connected mc acc\n"
            await writeLongMessage(txt, message.channel)
        #status
        if message.content.startswith(prefix + " status"):
            info = getinfo()
            await message.channel.send("**" + info["hostname"] + "** is " + "online" + " with " + str(info["players"]["online"]) + " players")
        #details
        if message.content.startswith(prefix + " details"):
            info = getinfo()
            txt = "**" + info["hostname"] + "**\n"
            txt += "running @*" + info["ip"] + ":" + str(info["port"]) + "*\n"
            txt += "on version: *" + info["version"] + "*\n"
            try:
                txt += "has " + info["players"]["online"] + "/" + info["players"]["max"]
            except:
                None
            await writeLongMessage(txt, message.channel)
        #connect
        if message.content.startswith(prefix + " connect"):
            parts = message.content.split(" ")
            users = loadUsers()
            todelete = []
            for i in users:
                if users[i] == str(message.author.id):
                    todelete.append(i)
            for i in todelete:
                del(users[i])
            users[parts[2]] = str(message.author.id)
            writeUsers(users)
            embed = discord.Embed(title= "\"" + str(parts[2]) + "\"\nconnected to\n\"" + str(message.author.name) + "\"",
                                  description="", color=0x7a2614)
            mcprofilepic.getMcProfilePic(parts[2])
            embed.set_thumbnail(url="attachment://mc_profile_face.png")
            with open("mc_profile_face.png", "rb") as image:
                file = discord.File(image)
            await message.channel.send(embed=embed, file=file)
        #me
        if message.content.startswith(prefix + " me"):
            users = loadUsers()
            mcname = ""
            for i in users:
                if users[i] == str(message.author.id):
                    mcname = i
            if mcname == "":
                await message.channel.send("you don't have an mc account connected")
            else:
                embed = discord.Embed(title="you are connected to " + str(mcname),
                                      description="", color=0x7a2614)
                mcprofilepic.getMcProfilePic(mcname)
                embed.set_thumbnail(url="attachment://mc_profile_face.png")
                with open("mc_profile_face.png", "rb") as image:
                    file = discord.File(image)
                await message.channel.send(embed=embed, file=file)





        #prx start
        if message.content.startswith(prefix + " prx start") and modID in [i.id for i in message.author.roles]:
            global category
            category = await createProximityChat(message.guild)
        elif message.content.startswith(prefix + " prx start"):
            await message.channel.send("You don't have the right permission")
        #prx connect
        if message.content.startswith(prefix + " prx connect"):
            if message.author in waitChannel.members:
                await addPlayerToProximityChat(message.author, message.channel, message.guild)
            else:
                await message.channel.send("You must be in the \"Wait here before connecting\" channel to start ProximityChat")
        #prx position
        if message.content.startswith(prefix + " prx position"):
            parts = message.content.split(" ")
            users = loadUsers()
            for i in users:
                if users[i] == str(message.author.id):
                    mcName = i
                    break
            else:
                await message.channel.send("your account is not connected to an mc account, use \"mc connect\"")
            if str(message.author.id) not in userX:
                await message.channel.send("you are not connected")
            else:
                userX[str(message.author.id)] = int(parts[3])
                userY[str(message.author.id)] = int(parts[4])

        # prx stop
        if message.content.startswith(prefix + " prx stop") and modID in [i.id for i in message.author.roles]:
            await closeProximityChat(guild)
        elif message.content.startswith(prefix + " prx stop"):
            await message.channel.send("You don't have the right permission")

async def writeLongMessage(txt, channel):
    if len(txt) > 2000:
        txt = txt.split("\n")
        while len(txt) != 0:
            temptxt = ""
            while len(txt) != 0 and len(temptxt) + len(txt[0]) < 2000:
                temptxt += txt[0]
                txt.pop(0)
            await channel.send(temptxt)

    else:
        await channel.send(txt)

def writeImage():
    info = getinfo()
    imgdata = base64.decodebytes(bytes(info["icon"].replace("data:image/png;base64,",""), encoding='utf8'))
    filename = 'server.png'
    with open(filename, 'wb') as f:
        f.write(imgdata)

def loadUsers():
    try:
        users = {}
        users = json.loads(open("users.txt").read())
        return users
    except:
        return {}

def writeUsers(users):
    with open("users.txt", "w") as file:
        json.dump(users, file)






curUsers = []
userX = {}
userY = {}
userZ = {}
usedChannels = []
category = None
guild = None
waitChannel = None

async def createProximityChat(curguild):
    global guild
    global waitChannel
    guild = curguild
    cat = await guild.create_category("minecraft proximity chat")
    waitChannel = await guild.create_voice_channel("Wait here before connecting", category=cat)
    return cat

async def closeProximityChat(guild):
    for i in usedChannels:
        try:
            await i.delete()
        except:
            None
    await waitChannel.delete()
    await category.delete()

async def addPlayerToProximityChat(author, channel, guild):
    users = loadUsers()
    discordID = author.id
    for i in users:
        if users[i] == str(discordID):
            mcName = i
            break
    else:
        await channel.send("your account is not connected to an mc account, use \"mc connect NCNAME\"")
    userX[str(discordID)] = 0
    userY[str(discordID)] = 0
    userZ[str(discordID)] = 2000000
    getPositions()
    curChannel = await guild.create_voice_channel("PC", category=category)
    usedChannels.append(curChannel)
    await author.move_to(curChannel)

distance = 30

async def makeProximityCombsChannels():
    while True:
        print("2" + str(userX))
        global usedChannels
        global distance
        for i in usedChannels:
            currentUsers = [j for j in i.members if str(j.id) in userX]
            toadd = []
            for k in usedChannels:
                if k != i:
                    breakK = False
                    for user in k.members:
                        if str(user.id) in userX:
                            for oriUser in currentUsers:
                                calc = math.sqrt((userX[str(oriUser.id)] - userX[str(user.id)])**2 + (userZ[str(oriUser.id)] - userZ[str(user.id)])**2 + (userY[str(oriUser.id)] - userY[str(user.id)])**2)
                                if calc < distance:
                                    toadd.append(k)
                                    breakK = True
                                    break
                        if breakK:
                            break
            todelete = []
            for n in toadd:
                for k in n.members:
                    await k.move_to(i)
                todelete.append(n)
            for o in todelete:
                usedChannels.remove(o)
                await o.delete()
            if len(toadd) > 0:
                break
        await asyncio.sleep(0.5)

async def splitProximityChannels():
    while True:
        print("x" + str(userX))
        print("y" + str(userY))
        print("z" + str(userZ))
        global usedChannels
        global distance

        toremove = []
        for i in usedChannels:
            if client.get_channel(i.id) == None:
                toremove.append(i)
        for i in toremove:
            usedChannels.remove(i)
        print("channels:            " + str(usedChannels))
        for i in usedChannels:
            validMembers = [o for o in client.get_channel(i.id).members if str(o.id) in userX]
            print(validMembers)
            print(distance)
            for user in validMembers:
                shouldLeave = len(validMembers) > 1
                print(user)
                for otherUser in validMembers:
                    print(otherUser)
                    if user != otherUser:
                        calc = math.sqrt((userX[str(otherUser.id)] - userX[str(user.id)]) ** 2 + (userZ[str(otherUser.id)] - userZ[str(user.id)]) ** 2 + (userY[str(otherUser.id)] - userY[str(user.id)]) ** 2)
                        if calc < distance:
                            shouldLeave = False
                if shouldLeave:
                    curChannel = await guild.create_voice_channel("PC", category=category)
                    usedChannels.append(curChannel)
                    await user.move_to(curChannel)
                    break
        await asyncio.sleep(0.5)

async def clearEmpty():
    while True:
        for i in usedChannels:
            if len(i.members) == 0:
                usedChannels.remove(i)
                await i.delete()
                break
        await asyncio.sleep(1)

def getPositions():
    x, y, z = dynmapstealer.getPos()
    print("xpos: " + str(x))
    for i in userX:
        mcName = discordIdToMCName(i)
        if mcName in x:
            userX[i] = x[mcName]
            userY[i] = y[mcName]
            userZ[i] = z[mcName]
        else:
            userX[i] = 0
            userY[i] = 0
            userZ[i] = 2000000

async def updatePositions():
    while True:
        getPositions()
        await asyncio.sleep(0.5)

def discordIdToMCName(discordid):
    users = loadUsers()
    for i in users:
        if users[i] == str(discordid):
            return i




client.loop.create_task(makeProximityCombsChannels())
client.loop.create_task(splitProximityChannels())
#client.loop.create_task(clearEmpty())
client.loop.create_task(updatePositions())
client.run('NzU5MDE3NDY5MTg3ODUwMjUx.X23YGg.GyxfdntdhhBXNvLSOmCbxQqY11A')
