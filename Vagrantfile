# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.define "centos7", autostart: false do |centos7|
    config.vm.box = "protodype/centos7"
    config.vm.hostname = "centos7"
    config.vm.synced_folder "./", "/home/vagrant/sync", type: "rsync", rsync_auto: true
  end
  config.vm.define "centos6", autostart: false do |centos6|
    config.vm.box = "protodype/centos6"
    config.vm.hostname = "centos6"
    config.vm.provision "shell",
      inline: "ln -s /home/vagrant/sync/src/nc-configure.py /usr/bin/nc-configure"
  end
end
