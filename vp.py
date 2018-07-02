#!/usr/bin/env python
# -*- coding: utf-8 -*-


import subprocess as sp
import re, json, os
import socket

# nginx image name, the script will find a instance under this image as the proxy instance
NGINX_IMG = 'nginx'

hostip = socket.gethostbyname(socket.getfqdn())
nginx_instance = None

ngx_cfg = '''
server{
        listen 80;
        server_name %%s;
        access_log  /var/log/nginx/%%s-access.log;
        error_log   /var/log/nginx/%%s-error.log;
        location / {
            root /root;
            proxy_pass http://%s:%%s/;
            proxy_read_timeout 300;
            proxy_connect_timeout 300;
            proxy_redirect     off;

            proxy_set_header   X-Forwarded-Proto $scheme;
            proxy_set_header   Host              $http_host;
            proxy_set_header   X-Real-IP         $remote_addr;
        }
    }

''' % hostip


def get_host_name(env):
    for line in env:
        arr = line.split('=')
        if arr[0] == 'HOSTNAME':
            return arr[-1]
    return None


out = sp.check_output(['docker', 'ps']).decode('utf-8')
out = out.split('\n')

host_port = {}

ids = []
for line in out[1:-1]:
    arr = re.split(r'\s+', line)
    ids.append(arr[0])
cmd = ['docker', 'inspect']
cmd.extend(ids)
out = sp.check_output(cmd).decode('utf-8')
jarr = json.loads(out)
for inst in jarr:
    name = inst['Name'][1:]

    if inst['Config']['Image'] == NGINX_IMG:
        print("found nginx instance %s" % name)
        nginx_instance = name
        continue

    env = inst['Config']['Env']
    hostname = get_host_name(env)
    try:
        port = inst['HostConfig']['PortBindings']['80/tcp'][0]['HostPort']
    except:
        port = None
    host_port[name] = [hostname, port]

full_cfg = ''
hosts = ''
for k in host_port:
    name, port = host_port[k]
    if name and port:
        full_cfg = full_cfg + (ngx_cfg % (name, name, name, port)) + '\n\n'
        hosts = hosts + "%s\t%s\n" % (hostip, name)
        pass
    else:
        print("no HOSTNAME env or 80 port mapping for instance %s [name=%s,port=%s]" % (k, name, port))
print("--------------- nginx cfg ------------")
print(full_cfg)
print("--------------------------------------")

if nginx_instance:
    proxy_cfg = 'proxy.conf'
    with open(proxy_cfg, 'w') as f:
        f.write(full_cfg)
    # copy proxy config
    sp.call(['docker', 'cp', proxy_cfg, '%s:/etc/nginx/conf.d/proxy.conf' % nginx_instance])
    # restart nginx
    sp.call(['docker', 'exec', nginx_instance, '/usr/sbin/nginx','-s','reload'])
    os.remove(proxy_cfg)
    print("nginx config reloaded")
print("**** pls add lines to your /etc/hosts ****\n")
print(hosts)
print("\n****************************************")



