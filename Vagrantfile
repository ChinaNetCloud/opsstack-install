# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.define "centos7", autostart: false do |centos7|
    centos7.vm.box = "protodype/centos7"
    centos7.vm.hostname = "centos7"
    centos7.vm.provision "shell",
      inline: "ln -s /home/vagrant/sync/src/nc-configure.py /usr/bin/nc-configure"
  end
  config.vm.define "centos6", autostart: false do |centos6|
    centos6.vm.box = "protodype/centos6"
    centos6.vm.hostname = "centos6"
    centos6.vm.provision "shell",
      inline: "ln -s /home/vagrant/sync/src/nc-configure.py /usr/bin/nc-configure"
  end
end