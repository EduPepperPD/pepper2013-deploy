import os
from fabric import api as fab

ENV = os.environ.get('PEPPERPD_ENV', 'staging')
envs = {
    'staging': {
        'fabric_env': {
            'hosts': ['pepperpd@198.101.238.239']
        },
        'git_url': 'git@github.com:EduPepperPD/pepper2013.git',
        #'git_commit': '2013-12-03'
        'git_commit': 'deploy'
    }
}

OPT = '/opt/edx'
DEPLOY = os.path.join(OPT, 'edx-platform')

REQUIRED_PACKAGES = ['git', 'mysql-server', 'mysql-client']


class Config(object):

    def __init__(self, data):
        self.__dict__.update(data)


config = Config(envs[ENV])

for name, value in config.fabric_env.items():
    setattr(fab.env, name, value)


def host_type():
    fab.run('uname -s')


def gen_deploy_key():
    key = os.path.join('/home', fab.env.user, '.ssh', 'id_rsa')
    pubkey = key + '.pub'
    if not exists(pubkey):
        fab.run('ssh-keygen -f %s -N ""' % key)
        print "Please install the following public key as a 'Deployment Key' "
        print "for the repository on GitHub:"
        print
        with fab.hide('everything'):
            print fab.run('cat %s' % pubkey)
        print
        fab.abort("Please run again after deployment key is installed.")


def install_prereqs():
    fab.sudo("echo 'mysql-server-5.5 mysql-server/root_password password "
             "lebbeb' | debconf-set-selections")
    fab.sudo("echo 'mysql-server-5.5 mysql-server/root_password_again password "
             "lebbeb' | debconf-set-selections")
    fab.sudo('apt-get update --yes')
    fab.sudo('apt-get upgrade --yes')
    fab.sudo('apt-get install %s --yes' % ' '.join(REQUIRED_PACKAGES))


def create_database():
    status = fab.run("echo 'SHOW DATABASES' | mysql -u root -plebbeb")
    if 'pepper' in status:
        return

    fab.run("echo 'CREATE DATABASE pepper' | mysql -u root -plebbeb")
    fab.run("echo \"CREATE USER 'pepper'@'localhost' IDENTIFIED BY 'lebbeb'\" | "
            "mysql -u root -plebbeb")
    fab.run("echo \"GRANT ALL PRIVILEGES ON * . * TO 'pepper'@'localhost'\" | "
            "mysql -u root -plebbeb")

    # Work around for bug in django_openid_auth, where table is created in a way
    # incompatible with mysql
    fab.run("""echo 'CREATE TABLE `django_openid_auth_useropenid` (
             `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
             `user_id` integer NOT NULL,
             `claimed_id` longtext NOT NULL,
             `display_id` longtext NOT NULL)' |
             mysql -u pepper -plebbeb pepper""")


def exists(path):
    with fab.settings(warn_only=True):
        with fab.hide('warnings'):
            result = fab.run('ls %s' % path)
    return not result.failed


def checkout():
    if not exists(OPT):
        fab.sudo('mkdir %s' % OPT)
        fab.sudo('chown %s %s' % (fab.env.user, OPT))
    if not exists(DEPLOY):
        fab.run('git clone %s %s' % (config.git_url, DEPLOY))
    with fab.cd(DEPLOY):
        fab.run('git checkout %s' % config.git_commit)


def provision():
    gen_deploy_key()
    #install_prereqs()
    create_database()
    checkout()
    with fab.cd(os.path.join(DEPLOY, 'scripts')):
        fab.run("sed 's/vagrant/pepperpd/g' vagrant-provisioning.sh "
                "> pepperpd-provisioning.sh")
        fab.run("chmod +x pepperpd-provisioning.sh")
        fab.sudo('./pepperpd-provisioning.sh')
