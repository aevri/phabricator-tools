# Configure the local Docker provider, assuming we're on a *nix machine
provider "docker" {
    host = "unix:///var/run/docker.sock"
}

# Create a container
resource "docker_container" "foo" {
    image = "${docker_image.ubuntu.latest}"
    name = "foo"
    command = ["nc", "-l", "80"]
    ports {
        internal = 80
        external = 8080
    }
}

resource "docker_image" "ubuntu" {
    name = "ubuntu:latest"
}
