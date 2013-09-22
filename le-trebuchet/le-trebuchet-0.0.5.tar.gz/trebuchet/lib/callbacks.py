import json
import requests

def jsonfy_pkg(pkg):
    """
    Transform the package in a correct json string for callback.
    """
    return {"name": pkg.full_package_name, "version": pkg.version, "file_name": pkg.final_deb_name}

def do_web_callback(web_callback_url, pkg):
    """
    Make a POST HTTP request to callback url for each package.
    Body of the request should be json data:
    {"name": "foo", "version": "0.0.0", "file_name": "foo-0.0.0-all.deb"}
    """
    payload = jsonfy_pkg(pkg)
    r = requests.post(web_callback_url, data=json.dumps(payload), headers={'content-type': 'application/json'})
    return r.status_code==200
