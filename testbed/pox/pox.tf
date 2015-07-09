# Configure the local Docker provider, assuming we're on a *nix machine
provider "docker" {
    host = "unix:///var/run/docker.sock"
}

resource "docker_container" "web" {
    image = "${docker_image.pox.latest}"
    count = 2
    name = "pox${count.index}"
    ports {
        internal = 8000
        external = "808${count.index}"
    }
}

resource "docker_container" "phab-web" {
    image = "${docker_image.phabricator.latest}"
    name = "phab-web"
    links = ["phab-mysql"]
    provisioner "local-exec" {
        command = "docker exec phab-web bash -c 'until mysql --host phab-mysql; do sleep 1; done; cd /phabricator/instances/dev/phabricator/bin/; ./config set mysql.host phab-mysql; mysql --host phab-mysql < /opt/phabricator-tools/vagrant/puppet/phabricator/files/initial.db; ./storage upgrade -f;'"
    }
    ports {
        internal = 80
        external = 8090
    }
}

resource "docker_container" "mysql" {
    image = "${docker_image.mysql.latest}"
    name = "phab-mysql"
    env = ["MYSQL_ALLOW_EMPTY_PASSWORD=yes"]
}

resource "docker_image" "phabricator" {
    name = "phabricator"
}

resource "docker_image" "pox" {
    name = "pox"
}

resource "docker_image" "mysql" {
    name = "mysql"
}
