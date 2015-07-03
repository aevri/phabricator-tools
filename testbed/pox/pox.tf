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

resource "docker_image" "pox" {
    name = "pox"
}
