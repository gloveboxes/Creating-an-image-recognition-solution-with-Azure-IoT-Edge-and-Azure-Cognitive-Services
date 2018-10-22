
import json
import random
from pprint import pprint
import os.path
from os.path import isdir
from os import listdir
# from os.path import *
modulesFileBase = "modules/"

def updateModule(moduleName, version):
    filename = modulesFileBase + moduleName + "/module.json"
    if not os.path.exists(filename):
        return False

    with open(filename) as f:
        data = json.load(f)

    data["image"]["tag"]["version"] = version

    with open(filename, 'w') as outfile:
        json.dump(data, outfile, indent=4)

    return True

def updateDeployment(moduleName, version):
    print(moduleName)
    with open('deployment.template.json') as f:
        data = json.load(f)

    try:
        v = data["moduleContent"]["$edgeAgent"]["properties.desired"]["modules"][moduleName]["settings"]["image"]
    except:
        return

    baseIdx = v.find(":")
    suffixIdx = v.find("-")

    base = v[0:baseIdx]
    suffix = v[suffixIdx:None]

    newImage = base + ":" + version + suffix

    data["moduleContent"]["$edgeAgent"]["properties.desired"]["modules"][moduleName]["settings"]["image"] = newImage

    with open('deployment.template.json', 'w') as outfile:
        json.dump(data, outfile, indent=4)

    print(moduleName + " updated")



def updateVersion(moduleName):
    print(moduleName)
    version = "0.1." + str(random.randint(1, 10000))
   
    if not updateModule(moduleName, version):
        return

    # updateDeployment(moduleName, version)


dirs = listdir("modules")

# updateVersion("FakeFlowers")

for d in dirs:
    updateVersion(d)