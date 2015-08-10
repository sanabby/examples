#
#
#

PREFIX=opencontrail
TAG=2.20

all: build-config build-control build-ifmap-server build-analytics build-web build-vrouter

build-%:
	$(eval SUBDIR := $(patsubst build-%,%,$@))
	docker build -t ${PREFIX}/${SUBDIR}:${TAG} ${SUBDIR}
