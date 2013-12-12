FROM stackbrew/ubuntu:saucy

MAINTAINER Saibaba Telukunta "https://github.com/saibaba"

RUN apt-get -y --force-yes install software-properties-common
RUN add-apt-repository -y ppa:webupd8team/java
RUN apt-get update

# automatically accept oracle license
RUN echo oracle-java7-installer shared/accepted-oracle-license-v1-1 select true | /usr/bin/debconf-set-selections
# and install java 7 oracle jdk
RUN apt-get -y install oracle-java7-installer && apt-get clean
RUN update-alternatives --display java
RUN echo "export JAVA_HOME=/usr/lib/jvm/java-7-oracle" >> ~/.bashrc
RUN apt-get -y install tomcat7
EXPOSE 8080
# tail so docker keeps running, -F to follow file rotation by tomcat
CMD service tomcat7 start && tail -F /var/lib/tomcat7/logs/catalina.out
