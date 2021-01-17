import requests
import json
import time
import math

def getPos():
    jsontxt = requests.get("http://onl.lorreyne.be:8123/up/world/world/{}".format(math.floor(time.time()))).text
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


    return posX, posY, posZ

print(getPos())