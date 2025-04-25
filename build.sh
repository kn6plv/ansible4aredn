#! /bin/sh
rm -f kn6plv-aredn-0.1.*.tar.gz
ansible-galaxy collection build collections/ansible_collections/kn6plv/aredn
ansible-galaxy collection publish kn6plv-aredn-0.1.*.tar.gz
rm -f kn6plv-aredn-0.1.*.tar.gz
