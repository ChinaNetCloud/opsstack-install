# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "centos/7"
  config.vm.provision "shell",
    inline: "ln -s /home/vagrant/sync/src/nc-configure.py /usr/bin/nc-configure"
end
