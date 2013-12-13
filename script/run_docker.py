from fabric.contrib.files import contains, sed
from fabric.context_managers import settings
import docker
import sys
from fabric.api import run as remote_run

def get_mapped_port(info, exposed_port):
    return info['NetworkSettings']['Ports']['%s/tcp' % (exposed_port,)][0]['HostPort']

def inspect_container(host, port, container_id):
    client = docker.Client(base_url="http://%s:%s" % (host,port))
    info = client.inspect_container(container_id)
    print get_mapped_port(info, 8080)

def add_server_to_nginx(nginx_host, user, key_file, new_server):

    login = '%s@%s' % (user, nginx_host)
    with settings(host_string=login, key_filename=key_file):
        if contains("/etc/nginx/conf.d/backends", new_server, exact=False):
            print "Error: Server already exists in nginx backends!"
        else:
            print "Server does not exist in nginx backends!"
            sed("/etc/nginx/conf.d/backends", before="}", after="    server %s max_fails=1 fail_timeout=15s;\\n}" % (new_server,), use_sudo=False)

        remote_run("/usr/sbin/nginx -s reload")

def run(docker_host, docker_port):
    client = docker.Client(base_url="http://%s:%s" % (docker_host, docker_port))
    container_id = client.create_container("sai/tomcat7", ports=[8080])
    client.start(container_id, port_bindings={ 8080: None })
    info = client.inspect_container(container_id)
    return info

def run_container_and_add_to_nginx(nginx_host, nginx_user, nginx_key_file, docker_host, docker_port):
    info  = run(docker_host, docker_port)
    port = get_mapped_port(info, 8080)
    add_server_to_nginx(nginx_host, nginx_user , nginx_key_file, "%s:%s" % (docker_host, port))

if __name__ == '__main__':

    if len(sys.argv) !=  6:
        print "Usage: python run_docker.py docker_host docker_port nginx_host nginx_user nginx_key_file"
        exit(1)

    docker_daemon_host = sys.argv[1]
    default_docker_port = int(sys.argv[2])
    nginx_host = sys.argv[3]
    nginx_user = sys.argv[4]
    nginx_key_file = sys.argv[5]
    run_container_and_add_to_nginx(nginx_host, nginx_user, nginx_key_file, docker_daemon_host, default_docker_port)

