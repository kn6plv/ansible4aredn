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

root = 'http://downloads.arednmesh.org/'
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

        ret = []
        for version in terms:
            # Look for cached versions to avoid network traffic
            filename = firmware_dir + ("aredn-" + version + "-" + board + "-" + boardtype + "-squashfs-sysupgrade.bin").replace("/", "-").replace(",", "-")
            if version == "release" or version == "nightly" or not os.path.exists(filename):
                if version == 'nightly':
                    # Select the latest if that's what we want
                    base_url = root + "snapshots/targets/" + board
                elif re.match(r"^\d\.\d\.\d\.\d$", version) or version == "release":
                    # Otherwise make sure we have the specific one we asked for
                    resp = requests.get(root + "releases/")
                    releases = []
                    if resp.status_code != 200:
                        raise AnsibleError("cannot not find versions")
                    for m in re.finditer(r'href="(\d+\.\d+\.\d+\.\d+)/"', resp.text):
                        releases.append(m.group(1))
                    if len(releases) == 0:
                        raise AnsibleError("no releases")
                    releases.sort()
                    if version == "release":
                        base_url = root + "releases/" + releases[-1] + "/targets/" + board
                    elif version in releases:
                        base_url = root + "releases/" + version + "/targets/" + board
                    else:
                        raise AnsibleError("version not found: %s" % version)
                else:
                    raise AnsibleError("unknown version: %s" % version)

                # Fetch and parse the profiles for the selected update
                resp = requests.get(base_url + "/profiles.json")
                if resp.status_code != 200:
                    raise AnsibleError("cannot read firmware profiles: %s" % (base_url + "/profiles.json"))
                profiles = resp.json()

                # Actual version number
                version = profiles["version_number"]

                # Have we downloaded this already?
                filename = firmware_dir + ("aredn-" + version + "-" + board + "-" + boardtype + "-squashfs-sysupgrade.bin").replace("/", "-").replace(",", "-")
                if not os.path.exists(filename):
                    # Find matching firmware download
                    firmware = False
                    for pid in profiles["profiles"].keys():
                        profile = profiles["profiles"][pid]
                        if boardtype == pid or boardtype in profile["supported_devices"]:
                            for v in profile["images"]:
                                if v["type"] == "sysupgrade":
                                    firmware = base_url + "/" + v["name"]
                                    sha = v["sha256"]
                                    break
                    if not firmware:
                        raise AnsibleError("firmware not found: " + boardtype)

                    # Fetch and verify firmware
                    resp = requests.get(firmware)
                    if resp.status_code != 200:
                        raise AnsibleError("cannot download firmware")
                    if hashlib.sha256(resp.content).hexdigest() != sha:
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
