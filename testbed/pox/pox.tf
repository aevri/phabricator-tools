# Configure the local Docker provider, assuming we're on a *nix machine
provider "docker" {
    host = "unix:///var/run/docker.sock"
}

resource "docker_container" "simple-haproxy" {
    image = "${docker_image.haproxy.latest}"
    name = "simple-haproxy"
    links = ["${docker_container.simpleweb.*.name}", "phab-mysql"]
    ports {
        internal = 80
        external = 8092
    }
    volumes {
        read_only = true
        container_path = "/usr/local/etc/haproxy/haproxy.cfg"
        host_path = "${path.module}/simplehaproxy.cfg"
    }
}

resource "docker_container" "pox-haproxy" {
    image = "${docker_image.haproxy.latest}"
    name = "pox-haproxy"
    links = ["${docker_container.pox.*.name}"]
    ports {
        internal = 80
        external = 8091
    }
    volumes {
        read_only = true
        container_path = "/usr/local/etc/haproxy/haproxy.cfg"
        host_path = "${path.module}/haproxy.cfg"
    }
}

resource "docker_container" "pox" {
    image = "${docker_image.pox.latest}"
    count = 2
    name = "pox${count.index}"
    links = ["phab-web"]
    command = ["--secret", "squirrel", "--port" ,"80", "--uri", "http://phab-web/", "--user", "phab", "--cert", "xnh5tpatpfh4pff4tpnvdv74mh74zkmsualo4l6mx7bb262zqr55vcachxgz7ru3lrvafgzquzl3geyjxw426ujcyqdi2t4ktiv7gmrtlnc3hsy2eqsmhvgifn2vah2uidj6u6hhhxo2j3y2w6lcsehs2le4msd5xsn4f333udwvj6aowokq5l2llvfsl3efcucraawtvzw462q2sxmryg5y5rpicdk3lyr3uvot7fxrotwpi3ty2b2sa2kvlpf"]
    ports {
        internal = 80
        external = "808${count.index}"
    }
}

resource "docker_container" "simpleweb" {
    image = "${docker_image.python.latest}"
    count = 2
    name = "simpleweb${count.index}"
    command = ["python", "-m", "SimpleHTTPServer", "80"]
    ports {
        internal = 80
        external = "807${count.index}"
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
    name = "mysql:latest"
}

resource "docker_image" "haproxy" {
    name = "haproxy:latest"
}

resource "docker_image" "python" {
    name = "python:2-slim"
}

