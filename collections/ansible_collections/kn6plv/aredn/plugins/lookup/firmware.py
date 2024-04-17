#! /usr/bin/python
# python 3 headers, required if submitting to Ansible
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import requests
import re
import hashlib
import os
from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from distutils.version import LooseVersion

DOCUMENTATION = """
  lookup: firmware
  author: Tim Wilkinson KN6PLV <tim.j.wilkinson@gmail.com>
  version_added: "0.1"
  short_description: fetch AREDN firmware
  description:
    - This lookup fetch and cache AREDN firmware for specific device
      and version. It returns a filename containing the appropriate firmware.
  options:
    _terms:
      description: Firmware versions
      required: True
  notes:
    - Uses device facts as part of selecting the appropriate firmware.
"""

root = 'http://downloads.arednmesh.org/afs/www/'
firmware_dir = "/tmp/aredn-firmware/"

os.makedirs(firmware_dir, exist_ok=True)


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):

        self.set_options(var_options=variables, direct=kwargs)

        board = variables["ansible_board"]
        if not board:
            raise AnsibleError("no board")
        boardtype = variables["ansible_hardware_type"]
        if not boardtype:
            raise AnsibleError("no hardware type")

        # Board type naming inconsistencies
        if re.match(r"^cpe", boardtype):
            boardtype = boardtype = "tplink," + boardtype
        if re.match(r"^rocket-m-xw", boardtype):
            boardtype = boardtype = "ubnt-" + boardtype
        if boardtype == "qemu-standard-pc-i440fx-piix-1996":
            boardtype = "generic"

        ret = []
        for version in terms:
            # Look for cached versions to avoid network traffic
            filename = firmware_dir + ("aredn-" + version + "-" + board + "-" + boardtype + "-squashfs-sysupgrade.bin").replace("/", "-").replace(",", "-")
            if version == "release" or version == "nightly" or not os.path.exists(filename):
                if re.match(r"^\d\.\d\.\d\.\d$", version) or version == "release" or version == "nightly":
                    resp = requests.get(root + "config.js")
                    releases = []
                    if resp.status_code != 200:
                        raise AnsibleError("cannot not find versions")
                    for v in re.finditer(r'versions: ({.+}),', resp.text):
                        for m in re.finditer(r'\'(.+?)\': \'data/.+?\',', v.group(1)):
                            releases.append(m.group(1))
                    if len(releases) == 0:
                        raise AnsibleError("no releases")
                    releases.sort(key=LooseVersion)
                    if version == "release":
                        version = releases[-1]
                    elif version == "nightly":
                        version = releases[0]
                    elif version in releases:
                        pass
                    else:
                        raise AnsibleError("version not found: %s" % version)
                else:
                    raise AnsibleError("unknown version: %s" % version)

                resp = requests.get(root + "data/" + version + "/overview.json")
                if resp.status_code != 200:
                    raise AnsibleError("cannot read firmware overviews: %s" % (root + "data/" + version + "/overview.json"))
                overview = resp.json()
                target = False
                firmware_url = False
                for profile in overview["profiles"]:
                    if profile["id"] == boardtype:
                        target = overview["image_url"].replace("{target}", profile["target"])
                        resp = requests.get(root + "data/" + version + "/" + profile["target"] + "/" + profile["id"] + ".json")
                        if resp.status_code != 200:
                            raise AnsibleError("cannot read firmware profile: %s" % (root + "data/" + version + "/" + profile["target"] + "/" + profile["id"] + ".json"))
                        profile = resp.json()
                        for image in profile["images"]:
                            if image["type"] == "sysupgrade" or image["type"] == "nand-sysupgrade" or image["type"] == "combined":
                                firmware_url = target + "/" + image["name"]
                                firmware_sha = image["sha256"]
                                break
                        break
                if not firmware_url:
                    raise AnsibleError("firmware not found: " + boardtype)

                # Fetch and verify firmware
                resp = requests.get(firmware_url)
                if resp.status_code != 200:
                    raise AnsibleError("cannot download firmware")
                if hashlib.sha256(resp.content).hexdigest() != firmware_sha:
                    raise AnsibleError("firmware checksum failed")

                # Store content in a file
                f = open(filename, mode="w+b")
                f.write(resp.content)
                f.close()

            f = open(filename, mode="r+b")
            sha = hashlib.sha256(f.read()).hexdigest()
            f.close()

            ret.append({"version": version, "file": filename, "sha256": sha, "size": os.path.getsize(filename)})

        return ret
