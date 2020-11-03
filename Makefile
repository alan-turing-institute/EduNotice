.PHONY: login build clean push run

login:
	docker login ${ENS_DOCKER_IMAGE} -u ${ENS_DOCKER_USER} -p ${ENS_DOCKER_PASS}
build:
	git submodule sync
	git submodule update --init --recursive --remote
	docker build . -f Dockerfile -t ${ENS_DOCKER_IMAGE}
clean:
	docker image rm ${ENS_DOCKER_IMAGE}
push:
	docker push ${ENS_DOCKER_IMAGE}
run:
	docker run -it ${ENS_DOCKER_IMAGE} /bin/bash