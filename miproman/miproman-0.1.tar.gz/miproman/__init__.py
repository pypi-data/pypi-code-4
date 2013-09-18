import shutil
import uuid
import biplist
from miproman.settings import get_settings

__title__ = "miproman"
__version__ = "0.1"
__author__ = "Jatin Nagpal"
__license__ = "Apache License 2.0"
__copyright__ = "Copyright 2013 Jatin Nagpal"


def generate_profile(name, command, tags, template):
    profile = dict()
    profile.update(template)
    profile.update({
        "Guid": str(uuid.uuid4()),
        "Command": command,
        "Tags": tags,
        "Name": name,
        "Default Bookmark": "No",
        "Custom Command": "Yes",
    })
    return profile


def main():
    settings = get_settings()

    if settings["verbose"]:
        def vprint(*args):
            for arg in args:
                print arg,
            print
    else:
        def vprint(*args):
            pass

    print """
    WARNING: Ensure iTerm2 is not running. If you ran this with iTerm2 open,
             profiles will not be added even though it will process the request.
    """

    if not shutil.os.path.exists(settings["profile"]):
        print "%s does not exist." % settings["profile"]
        return

    if not shutil.os.path.isfile(settings["profile"]):
        print "%s is not a valid file." % settings["profile"]
        return

    backup = "%s.bak" % settings["profile"]
    shutil.copy(settings["profile"], backup)
    vprint("Profile backup created at %s." % backup)

    try:
        plist = biplist.readPlist(backup)
    except biplist.InvalidPlistException:
        print "%s is not a valid plist file." % settings["profile"]
        return

    profiles = dict((x.get("Name").lower(), x) for x in plist["New Bookmarks"])
    template = profiles.get(settings["template_name"].lower(), None)

    if not template:
        print "No profile named '%s' found." % settings["template_name"]
        return

    new_profiles = []
    def add_profile(name):
        if not profiles.get(name, None):
            new_profiles.append(generate_profile(
                name=name,
                command=settings["command"].format(name),
                tags=settings["tags"],
                template=template)
            )
            vprint("Profile '%s' added." % name)
        else:
            vprint("Profile '%s' already exists." % name)

    for server in settings["servers"]:
        if settings["range"] and server.format(1) != server:
            for i in xrange(*settings["range"]):
                add_profile(server.format(i))
        else:
            add_profile(server)

    plist["New Bookmarks"] = plist["New Bookmarks"] + new_profiles

    try:
        biplist.writePlist(plist, settings["profile"])
    except (biplist.InvalidPlistException,
            biplist.NotBinaryPlistException) as error:
        vprint(error)
        import traceback
        vprint(traceback.format_exc(15))
        print "Failed to update profiles."
        return

    print "Added %s new profiles." % len(new_profiles)

if __name__ == "__main__":
    main()
