#! /usr/bin/python3
# python 3 headers, required if submitting to Ansible
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import requests
import re
import tempfile
from hashlib import sha256
import os

DOCUMENTATION = """
  lookup: firmware
  author: Tim Wilkinson KN6PLV <tim.j.wilkinson@gmail.com>
  version_added: "0.1"
  short_description: fetch firmware for specific device and version
  description:
      - ...
  options:
"""
from ansible.errors import AnsibleError, AnsibleParserError
from ansible.plugins.lookup import LookupBase

root = 'http://downloads.arednmesh.org/'

class LookupModule(LookupBase):

    def run(self, versions, variables=None, **kwargs):

        self.set_options(var_options=variables, direct=kwargs)

        board = variables["ansible_board"]
        if not board:
            raise AnsibleError("no board")
        boardtype = variables["ansible_hardware_type"]
        if not boardtype:
            raise AnsibleError("no hardware type")
        cversion = variables["ansible_distribution_version"]
        if not cversion:
            raise AnsibleError("unknown current version")

        ret = []
        for version in versions:
            temp = tempfile.NamedTemporaryFile(prefix="aredn-firmware-", delete=False)
            sha = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" # sha265 of an empty file
            if version != cversion:
                if version == 'nightly':
                    # Select the latest if that's what we want
                    base_url = root + "snapshots/targets/" + board
                else:
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
                    else:
                        if not re.match(r"^\d\.\d\.\d\.\d$", version):
                            raise AnsibleError("unknown version: %s" % version)
                        if not version in releases:
                            raise AnsibleError("version not found: %s" % version)
                        base_url = root + "releases/" + version + "/targets/" + board
            
                # Feetch and parse the profiles for the selected update
                resp = requests.get(base_url + "/profiles.json")
                if resp.status_code != 200:
                    raise AnsibleError("cannot read firmware profiles")
                profiles = resp.json()

                # If we're on the correct version, nothing to do
                if profiles["version_number"] == cversion:
                    version = cversion
                else:
                    version = profiles["version_number"]
                    # Board type naming inconsistencies
                    if re.match(r"^cpe", boardtype):
                        boardtype = boardtype = "tplink," + boardtype

                    # Find matching firmware download
                    for profile in profiles["profiles"].values():
                        for id in profile["supported_devices"]:
                            if id == boardtype:
                                for v in profile["images"]:
                                    if v["type"] == "sysupgrade":
                                        firmware = base_url + "/" + v["name"]
                                        sha = v["sha256"]
                                        break
                                break
                    if not firmware:
                        raise AnsibleError("firmware not found")

                    # Fetch and verify firmware
                    resp = requests.get(firmware)
                    if resp.status_code != 200:
                        raise AnsibleError("cannot download firmware")
                    if sha256(resp.content).hexdigest() != sha:
                        raise AnsibleError("firmware checksum failed")

                    # Store content in a file
                    temp.write(resp.content)
                    temp.close()
                    
            ret.append({ "version": version, "old_version": cversion, "file": temp.name, "sha256": sha, "size": os.path.getsize(temp.name) })

        return ret
