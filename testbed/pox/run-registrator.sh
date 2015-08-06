docker run -d --name registrator -v /var/run/docker.sock:/tmp/docker.sock -h $HOSTNAME gliderlabs/registrator -internal consul:
