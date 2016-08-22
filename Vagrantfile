# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.define "centos7" do |centos7|
    centos7.vm.box = "protodype/centos7"
    centos7.vm.hostname = "centos7"
    centos7.vm.provision "shell",
      inline: "ln -s /vagrant/src/opsstack-configure.py /usr/bin/opsstack-configure"
  end
  config.vm.define "centos6" do |centos6|
    centos6.vm.box = "protodype/centos6"
    centos6.vm.hostname = "centos6"
    centos6.vm.provision "shell",
      inline: "ln -s /vagrant/src/opsstack-configure.py /usr/bin/opsstack-configure"
  end
  config.vm.define "debian8" do |debian8|
    debian8.vm.box = "colynn/debian8"
    debian8.vm.hostname = "debian8.example.com"
    debian8.ssh.shell = "bash -c 'BASH_ENV=/etc/profile exec bash'"
    debian8.vm.provision "shell",
      inline: "ln -s /home/vagrant/sync/src/opsstack-configure.py /usr/bin/opsstack-configure"
  end
end
