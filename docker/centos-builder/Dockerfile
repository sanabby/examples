FROM centos:7
RUN curl https://storage.googleapis.com/git-repo-downloads/repo > /usr/bin/repo && chmod 755 /usr/bin/repo
RUN mkdir -p src/contrail
WORKDIR src/contrail
RUN yum install -y git python-lxml wget gcc patch make unzip flex bison gcc-c++ openssl openssl-devel autoconf automake vim python-devel python-setuptools net-snmp-python
RUN yum install -y libtool kernel-devel
RUN yum install -y bzip2 boost-devel tbb-devel libcurl-devel libxml2-devel zlib-devel
RUN yum install -y epel-release
RUN yum install -y scons protobuf protobuf-devel protobuf-compiler
RUN repo init -u https://github.com/Juniper/contrail-vnc.git -m noauth.xml
RUN repo sync third_party
RUN USER=nobody python third_party/fetch_packages.py
RUN (cd third_party && wget http://sourceforge.net/projects/libipfix/files/libipfix/libipfix_110209.tgz && tar zxvf libipfix_110209.tgz && cd libipfix_110209 && ./configure && make && make install)
RUN (cd third_party && wget -O librdkafka-0.8.5.tar.gz https://github.com/edenhill/librdkafka/archive/0.8.5.tar.gz && tar zxvf librdkafka-0.8.5.tar.gz && cd librdkafka-0.8.5 && ./configure && make && make install)
ADD build-contrail.sh /usr/bin/build-contrail.sh
RUN chmod 755 /usr/bin/build-contrail.sh
