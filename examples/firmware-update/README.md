Simple Ansible playbook to upgrade node firmware
===

Install Ansible (Debian)
---
First make sure you have all the necessary dependencies installed:
```
sudo apt install python3 python3-pip sshpass -y
```
Then install Ansible itself:

```
sudo pip3 install ansible
```

Install this example
---
Install this example using the following:
```
git clone https://github.com/kn6plv/ansible4aredn.git
cd ansible4aredn/examples/firmware-update
```
And now install the AREDN support:
```
ansible-galaxy collection install kn6plv.aredn
```
These pieces need only be done once.

Update the node:
---

Type the following command:
```
ansible-playbook update.yml
```
This will update the ```localnode``` to the currently release firmware. You can add nodes to the list in ```inventory``` and this command will then update all nodes. If a node is already on the correct firmware, nothing will be changed.
