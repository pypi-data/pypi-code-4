import sys
import os
import json

__version__ = "0.0.3"
userhome = os.environ["HOME"]
confpath = ".config" + os.sep + "proj.py.conf"
fullpath = userhome + os.sep + confpath


def get_conf():
    with open(fullpath, 'r') as f:
        conf = json.loads(f.read())
        return conf


def save_conf(conf):
    if(not os.path.exists(os.sep.join(fullpath.split(os.sep)[:-1]))):
        os.mkdir(os.sep.join(fullpath.split(os.sep)[:-1]))

    with open(fullpath, 'w+') as f:
        f.write(json.dumps(conf))


def main():
    if(not len(sys.argv) > 1):
        raise Exception("Not enough parameters given")
    try:
        conf = get_conf()
    except IOError:
        print("No conf file found, making one...")
        conf = {"projects": []}
    if(sys.argv[1] == "add"):
        conf["projects"].append({"name": sys.argv[2], "dir": sys.argv[3]})
    elif(sys.argv[1] == "rm"):
        for proj in conf["projects"]:
            if(proj["name"] == sys.argv[2]):
                conf["projects"].remove(proj)
                break
    elif(sys.argv[1] == "ls"):
        for proj in conf["projects"]:
            print("%s: %s" % (proj["name"], proj["dir"]))
    else:
        for proj in conf["projects"]:
            if(proj["name"] == sys.argv[1]):
                # then cd to this dir
                os.chdir(proj["dir"])
    save_conf(conf)


if __name__ == '__main__':
    main()
