Introduction and Goal
=====================

The goal of this exercise is to use Rackspace public cloud servers as the hosting servers for running docker instances that run tomcat applications.
Each tomcat application runs on multiple docker instances (possibly running on multiple cloud servers) and load balanced by an nginx proxy.

This document gives a high-level details on how one can go about achieving it.


Pre-requisites
==============

* All the commands shown are run from a Ubuntu workstation (marked with $). If you are using another platform, you need to modify these accordingly.
* You also need Nova client (https://github.com/openstack/python-novaclient) on this workstation.
* And of course, a Rackspace (public cloud) account to play with.

Steps
=====

1) First create a ssh key pair to use for logging into cloud servers, for example


    $ ssh-keygen -q -t rsa -f mykey -N

2) Create a cloud server. This is what is used to install docker, configure a docker image with necessary software (JDK and tomcat). The same cloud server is snapshotted so that additional VMs can be created as necessary.


    $ nova boot --image 7437239b-bf92-4489-9607-889be189e772 --flavor 2 --file /root/.ssh/authorized_keys=mykey.pub mydkr1

3) Wait for the mydkr1 to start and ready. You can check the status with:


    $ nova show mydkr1

Once it is ready, note accessIPv4. In the following instructions use this IP for all references to mydkr1.

4) Connect to mydkr1 and prepare it with docker::

   $ ssh -i mykey root@192.237.188.82
   
Now, for docker itself::


   # apt-get update
   # apt-get install linux-image-extra-`uname -r`
   # sh -c "wget -qO- https://get.docker.io/gpg | apt-key add -"
   # sh -c "echo deb http://get.docker.io/ubuntu docker main > /etc/apt/sources.list.d/docker.list"
   # apt-get update
   # apt-get install lxc-docker

   
Create/Update docker configuration so that the daemon is running TCP port and hence can be accessed remotely. We will use this later to launch new docker instances remotely from a script::

   root@mydkr1:~# cat /etc/default/docker
   DOCKER_OPTS="-H unix:///var/run/docker.sock -H tcp://0.0.0.0:5555"


Verify that docker is correctly installed::


   # docker run -i -t ubuntu /bin/bash
   root@f169b69d6370:/# exit

Exit from docker instance. It is shutdown automatically::

   root@f169b69d6370:/# exit

Copy Dockerfile to current directory. You can get a sample from here. This includes all the instructions to build a docker image with JDK+Tomcat.

Now build a docker image::


   # docker build -t sai/tomcat7 .

Verify that the image functions as expected::


   # docker run -d -p 8080 sai/tomcat7

Get the exposed port by running::


   # docker ps

Run Curl to verify::


   # curl -X GET http://localhost:port

Shutdown docker instances::


   # docker stop <container_id>

Exit from mydkr1 back to your workstation::


   # exit

Take a VM image snapshot. This can be used to create additional cloud servers to scale.

   $ nova image-create --poll mydkr1 mydkr_snapshot

5) Create a cloud server to run nginx:

::

   $ nova boot --image 7437239b-bf92-4489-9607-889be189e772 --flavor 2 --file /root/.ssh/authorized_keys=mykey.pub mynginx
   $ nova show mynginx

Log into this cloud server to install and configure nginx:

::

   $ ssh -i mykey root@mynginx
   # apt-get install nginx

Configure nginx. First disable sites-enabled by commenting out the line "include /etc/nginx/sites-enabled/*" in /etc/nginx/nginx.conf.

Copy backends, and default.conf to /etc/nginx/conf.d by suitably modifying them. You can start with empty backends or use the docker instance running in mydkr as the sole server.


Set nginx up to run on each boot.


6) Next we create a new cloud server. It will be more complete to demonstrate the functionality with two cloud servers.

   First Find the image id of the snapshot created earlier with:

::

   $ nova image-list

::

   $ nova boot --image <image id from above> --flavor 2 --file /root/.ssh/authorized_keys=mykey.pub mydkr2

::

Now you can use the script XXX to run an instance of docker in this cloud server (or any other cloud server)

   # ...

Now you have two tomcat instances running on two docker instances each of which is running on a separate cloud server. And both are behind the nginx proxy.

7) Test

   From your work station issue curl command to make sure that tomcat welcome page shows up.

Suggestions
===========

1) Run all cloud servers hosting docker with servicenet IP only and run the docker instances launch script from with in a cloud server so that it can reach other cloud servers over the service net.
2) Instead of using nova command line, you can use Cloud Servers API.
3) Completely automate the launch of new docker instances based on load, and other performance merics. Also, build a scheduling mechanism to identify the right cloud server to run it on.
4) Automate the launch of new cloud servers based on number of docker instances running on already existing ones, and other performance metrics. 
5) Beware of RackConnect automation:
   a) Its interacttion with how cloud servers are launched. Review: http://www.rackspace.com/knowledge_center/article/the-rackconnect-api. 
   b) Als, see, accessing RackConnected public cloud servers: http://www.rackspace.com/knowledge_center/article/accessing-rackconnected-cloud-servers


References
==========

1) http://linuxg.net/how-to-install-oracle-java-jdk-678-on-ubuntu-13-04-12-10-12-04/
2) http://blog.trifork.com/2013/08/15/using-docker-to-efficiently-create-multiple-tomcat-instances/
3) http://developer.rackspace.com/blog/slumlord-hosting-with-docker.html
4) https://gist.github.com/jgeurts/5847108
5) https://www.digitalocean.com/community/articles/how-to-set-up-nginx-load-balancing
6) http://tutum.co/2013/11/23/remote-and-secure-use-of-docker-api-with-python-part-ii-of-ii/
7) http://docs.docker.io/en/latest/api/docker_remote_api/
8) https://github.com/dotcloud/docker-py

Files
=====
1) Dockerfile, docker
2) nginx default.conf and backends
3) docker instance automation script
