# Configure the local Docker provider, assuming we're on a *nix machine
provider "docker" {
    host = "unix:///var/run/docker.sock"
}

resource "docker_container" "web" {
    image = "${docker_image.python.latest}"
    count = 2
    name = "hello${count.index}"
    command = ["python", "-m", "SimpleHTTPServer", "80"]
    ports {
        internal = 80
        external = "808${count.index}"
    }
}

resource "docker_image" "python" {
    name = "python:2-slim"
}
