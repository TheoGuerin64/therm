fedora:
	docker build -t therm:fedora -f Dockerfile.fedora .
	docker run -it --rm \
		-e TERM=xterm-256color \
		-v ./inventory.ini:/app/inventory.ini:ro \
		-v ./main.yml:/app/main.yml:ro \
		-v ./roles:/app/roles:ro \
	therm:fedora

.PHONY: fedora
