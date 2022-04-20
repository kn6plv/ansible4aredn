Simple Ansible playbook to upgrade node firmware
===

Install Ansible (Debian)
---
You only need to follow these steps if you've not already installed Ansible.
```
sudo apt install python3 python3-pip -y
sudo pip install ansible
```

Install AREDN support for Ansible
---
You only need to follow these steps if you've not already installed AREDN support for Ansible.
```
ansible-galaxy collection install kn6plv.aredn
```

Update the node
---

Type the following command:
```
ansible-playbook update.yml
```
This will update the ```localnode``` to the currently release firmware. You can add nodes to the list in ```inventory``` and this command will then update all nodes. If a node is already on the correct firmware, nothing will be changed.


