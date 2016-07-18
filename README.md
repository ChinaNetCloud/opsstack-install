## Development and Testing

Follow the steps below to setup a development environment.

### Install prerequisites

Install the following (someone please fill in the details):
1. Vagrant
2. VirtualBox

### Clone the repository

Open a terminal window and execute the following to clone the repository into a new `nc-configure` directory:


```Bash
cd ~/Projects/
git clone https://gitlab.service.chinanetcloud.com/nc-scripts/nc-configure.git
cd nc-configure/
```

### Start the Vagrant box

In the existing terminal window, execute the following:


```Bash
vagrant up
```

_Note_: If you don't already have the vagrant box, this will download the image. This may take some time.

### Connect to the image via SSH

In the existing termianl window, execute the following:

```Bash
vagrant ssh centos7
```

You are now connected to the virtual machine

### Run the configure script

```Bash
sudo nc-configure
```



