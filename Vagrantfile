# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.define "centos7" do |centos7|
    centos7.vm.box = "protodype/centos7"
    centos7.vm.hostname = "centos7"
    centos7.vm.provision "shell",
      inline: "rpm -ivh http://repo.service.chinanetcloud.com/yum/el7/base/x86_64/nc-repo-1.0.0-1.el7.noarch.rpm; yum install opsstack-common -y;ln -s /vagrant/src/opsstack-install.py /var/lib/opsstack/common/env/bin/opsstack-install; ln -s /vagrant/src/opsstack-install.sh /usr/bin/opsstack-install"
  end
  config.vm.define "centos6" do |centos6|
    centos6.vm.box = "protodype/centos6"
    centos6.vm.hostname = "centos6"
    centos6.vm.provision "shell",
      inline: "rpm -ivh http://repo.service.chinanetcloud.com/yum/el6/base/x86_64/nc-repo-1.0.0-1.el6.noarch.rpm; yum install opsstack-common -y;ln -s /vagrant/src/opsstack-install.py /var/lib/opsstack/common/env/bin/opsstack-install; ln -s /vagrant/src/opsstack-install.sh /usr/bin/opsstack-install"
  end
  config.vm.define "debian8" do |debian8|
    debian8.vm.box = "colynn/debian8"
    debian8.vm.hostname = "debian8.example.com"
    debian8.ssh.shell = "bash -c 'BASH_ENV=/etc/profile exec bash'"
    debian8.vm.provision "shell",
      inline: "ln -s /home/vagrant/sync/src/opsstack-configure.py /usr/bin/opsstack-configure"
  end
  config.vm.define "ubuntu1604" do |ubuntu1604|
    ubuntu1604.vm.box = "ubuntu/xenial64"
    ubuntu1604.vm.hostname = "ubuntu1604.example.com"
    ubuntu1604.ssh.shell = "bash -c 'BASH_ENV=/etc/profile exec bash'"
    ubuntu1604.vm.provision "shell",
      inline: "ln -s /home/vagrant/sync/src/opsstack-configure.py /usr/bin/opsstack-configure"
  end
  config.vm.define "ubuntu1204" do |ubuntu1204|
    ubuntu1204.vm.box = "ubuntu/precise64"
    ubuntu1204.vm.hostname = "ubuntu1204.example.com"
    ubuntu1204.ssh.shell = "bash -c 'BASH_ENV=/etc/profile exec bash'"
    ubuntu1204.vm.provision "shell",
       inline: "wget http://repo.service.chinanetcloud.com/apt/ubuntu/pool/precise/main/nc-repo_1.0.0-1.ubuntu+precise_all.deb && dpkg -i nc-repo_1.0.0-1.ubuntu+precise_all.deb; apt-get install opsstack-common -y;ln -s /vagrant/src/opsstack-configure.py /var/lib/opsstack/common/env/bin/opsstack-configure; ln -s /vagrant/src/opsstack-configure.sh /usr/bin/opsstack-configure"
  end
  config.trigger.reject [:destroy]
end
