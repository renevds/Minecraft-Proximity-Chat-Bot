import requests
import json
import time
import math


def getPos():
    jsontxt = requests.get("https://map.theonly.xyz/up/world/world/{}".format(math.floor(time.time()))).text
    print(jsontxt)
    players = json.loads(jsontxt)["players"]
    posX = {}
    posY = {}
    posZ = {}
    for i in players:
        name = i["name"]
        posX[name] = i["x"]
        posY[name] = i["y"]
        posZ[name] = i["z"]

    print(jsontxt)

    for i in posX:
        print("{} is at {}, {}, {}".format(i, posX[i], posY[i], posZ[i]))

    return posX, posY, posZ

getPos()