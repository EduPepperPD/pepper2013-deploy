Quick Start
-----------

    $ virtualenv .
    $ bin/pip install fabric==1.8

Preparing a brand new server
----------------------------

Create a new cloud server in Rackspace (Ubuntu 12.04, 8GB standard instance,
DFW region, Auto disk config)

Log in as root using supplied password.  Add a new user, 'pepperpd'::

    $ adduser pepperpd 

Enter a random password.  Leave personal data blank.

We need to update the sudoers file so that pepperpd has full sudo rights
without entering a password::

    echo 'pepperpd    ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers

Switch to the new `pepperpd` user::

    $ sudo -i -u pepperpd

Add your public ssh key to the pepperpd user so you can log in without a 
password (required for the deployment script, and recommended best practice in 
general)::

    $ mkdir .ssh
    $ chmod 700 .ssh

Using `scp` or equivalent, copy your public ssh key to `.ssh/authorized_keys`.
The command to do this from your local box may vary.  This is the command I 
used to copy my public key to staging::
    
    crossi@spirit:~$ scp .ssh/id_rsa.pub pepperpd@198.101.238.239:.ssh/authorized_keys
    pepperpd@198.101.238.239's password: 
    id_rsa.pub                         100%  394     0.4KB/s   00:00    
    crossi@spirit:~$ 

Back on your new server::

    $ chmod 600 .ssh/authorized_keys

Now test that you are able to `ssh` in as `pepperpd` to the new server without
entering a password.  Do not proceed until you have verified you can do this.

Verify now that the `pepperpd` user can use sudo without entering a password. 
Now that we can log in and gain root priveleges without a password, we can 
safely forget the passwords for `root` and `pepperpd`.  It's more secure if we
don't record these passwords anywhere.  This also the minimum sufficent manual
configuration to make a server usable by the deployment script.  In order to
allow a new person to access the server, just add their public ssh key to 
`~pepperpd/.ssh/authorized_keys`.

Unfortunately, MySQL must be set up and configured manually.  First install
mysql::

    $ sudo apt-get install mysql-server mysql-client

Enter `lebbeb` for the root MySQL user password.
    

