import requests
from base64 import b64decode
import json
from PIL import Image

def getMcProfilePic(mcName):
    id = requests.get(url="https://api.mojang.com/users/profiles/minecraft/" + mcName)
    id = json.loads(id.text)
    print(id)
    textureURL = "https://sessionserver.mojang.com/session/minecraft/profile/" + id["id"]
    base64info = json.loads(requests.get(url=textureURL).text)["properties"][0]["value"]
    print(base64info)
    textureInfo = json.loads(b64decode(base64info, validate=True).decode('utf-8'))
    print(textureInfo["textures"]["SKIN"]["url"])
    texture = requests.get(textureInfo["textures"]["SKIN"]["url"])
    with open("mc_profile.png", "wb") as file:
        file.write(texture.content)
        file.close()
    im = Image.open("mc_profile.png")
    crop_rectangle = (8, 8, 16, 16)
    cropped_im = im.crop(crop_rectangle)
    cropped_im = cropped_im.resize((700, 700), resample=Image.BOX)
    cropped_im.save("mc_profile_face.png")
