# AREDN Configuration

This collection provides Roles, Modules and Playbooks to configure AREDN nodes.

## Tested with Ansible

Tested with Ansible 2.8 and ansible-core 2.12.

## External requirements

None

## Included content

### Roles

* kn6plv.aredn.advanced
* kn6plv.aredn.advertise
* kn6plv.aredn.dns_alias
* kn6plv.aredn.dhcp_address
* kn6plv.aredn.firmware
* kn6plv.aredn.packages
* kn6plv.aredn.port_forward
* kn6plv.aredn.reboot
* kn6plv.aredn.setup
* kn6plv.aredn.tunnels

### Modules

* kn6plv.aredn.advconfig
* kn6plv.aredn.advertise
* kn6plv.aredn.basics
* kn6plv.aredn.dhcpaddress
* kn6plv.aredn.dnsalias
* kn6plv.aredn.firmware
* kn6plv.aredn.lan
* kn6plv.aredn.meshrf
* kn6plv.aredn.opkg
* kn6plv.aredn.portforward
* kn6plv.aredn.tunnelclient
* kn6plv.aredn.tunnelserver
* kn6plv.aredn.wan

### Plugins

* kn6plv.aredn.firmware

### Playbooks

* kn6plv.aredn.base

## Using this collection

Before using the ```kn6plv.aredn``` collection, you need to install with the ```ansible-galaxy``` CLI:
```
ansible-galaxy collection install kn6plv.aredn
```
## Release notes

None

## Releasing

We release new versions with new feature and bug fixes often as this collection is still maturing.

## Contributing

Please create and report problems or request features via GitHub's Issue Tracker and PR system.

## Licensing

GNU General Public License v2.0 or later.
