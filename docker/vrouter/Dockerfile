FROM ubuntu:14.04
MAINTAINER Pedro Marques <roque@juniper.net>
RUN apt-get install -y software-properties-common
RUN add-apt-repository -y ppa:opencontrail/ppa
RUN add-apt-repository -y ppa:anantha-l/opencontrail-2.20
RUN apt-get update
RUN apt-get -y install linux-headers-`uname -r`
RUN apt-get -y install contrail-vrouter-agent contrail-vrouter-utils contrail-utils python-contrail-vrouter-api
RUN apt-get -y install wget gdebi git ruby
RUN wget -qO - https://github.com/rombie/opencontrail-packages/raw/R2.20/ubuntu1404/contrail.tar.xz | tar Jx
RUN gdebi -n contrail-vrouter-init_*.deb
RUN gdebi -n contrail-setup_*.deb
RUN git clone -b fedora_ubuntu_demo https://github.com/rombie/contrail-kubernetes.git

# Provision vrouter
# RUN service supervisor restart
# RUN ruby $PWD/contrail-kubernetes/scripts/opencontrail-install/contrail_install.rb --role compute --no-contrail-install --no-provision-vrouter
