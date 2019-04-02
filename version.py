
import json
import random
from pprint import pprint
import os.path
from os.path import isdir
from os import listdir
from packaging import version
# from os.path import *
modulesFileBase = "modules/"


def updateModule(moduleName, versionX):
    filename = modulesFileBase + moduleName + "/module.json"
    if not os.path.exists(filename):
        return False

    with open(filename) as f:
        data = json.load(f)

    # todo increment micro release
    # major.minor.micro
    # https://www.python.org/dev/peps/pep-0440/

    v = data["image"]["tag"]["version"]

    ver =  tuple(map(int, (v.split("."))))
    micro = ver[2:3][0]
    micro = micro + 1
    new_ver = f"{ver[0:1][0]}.{ver[1:2][0]}.{micro}"

    data["image"]["tag"]["version"] = new_ver

    with open(filename, 'w') as outfile:
        json.dump(data, outfile, indent=4)

    return True


def updateVersion(moduleName):
    print(moduleName)
    version = "0.1." + str(random.randint(1, 10000))

    if not updateModule(moduleName, version):
        return

    # updateDeployment(moduleName, version)


dirs = listdir("modules")

for d in dirs:
    updateVersion(d)
