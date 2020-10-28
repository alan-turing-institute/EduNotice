.PHONY: build clean #push 

build:
	docker build . -f Dockerfile -t turingedunotice/edunotice:funcapp
clean:
	docker image rm turingedunotice/edunotice:funcapp
# push:
# 	docker push turingedunotice/edunotice:funcapp