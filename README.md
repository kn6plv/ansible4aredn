# ansible4aredn

Ansible collection for configuring AREDN nodes

See [README](https://github.com/kn6plv/ansible4aredn/blob/master/collections/ansible_collections/kn6plv/aredn)

## Example

This simple example makes sure all our nodes are running on the latest firmware, and are configured on the same channel.

__update.yml__
```
- import_playbook: kn6plv.aredn.base

- hosts: all
  serial: 1
  roles:
    # Update firmware
    - role: firmware
      version: nightly

    # Essentials
    - role: setup
      description: "{{ My AREDN node (' + ansible_hardware_model + ')') }}"
      location: 37.0, -122.0
      timezone: America/Los_Angeles
      ntp_server: pool.ntp.org
      mesh:
        enable: true
        ssid: AREDN
        channel: -2
        channel_width: 10
        tx_power: max
```
