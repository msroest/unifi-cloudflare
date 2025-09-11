#!/usr/bin/env python3
# Requires: pip install aiounifi

import aiohttp
import asyncio
import os
import re
import time
from aiounifi.controller import Controller
from aiounifi.models.configuration import Configuration

TMPL_FILE="terraform/dns-record.tf.tmpl"
OUTPUT_PATH="terraform"
def get_env_var(name, default=None, required=False):
    value = os.getenv(name, default)
    if required and value is None:
        raise ValueError(f"Missing required environment variable: {name}")
    return value

async def list_clients(controller):
    clients={}
    await controller.clients.update()
    for client in controller.clients.values():
        hostname = client.hostname or client.name or client.mac.replace(":","-")
        ip = client.ip
        hostname=re.sub(r"[^a-z0-9A-Z\-_\.]","",hostname).lower()
        if hostname=='' or ip=='':
            continue
        clients[hostname]=ip
        # if there is a name set also add a dns record for that.
        if hostname != client.name and client.name:
            print(hostname)
            print(client.name)
            clients[re.sub(r"[^a-z0-9A-Z\-_\.]","",client.name).lower()] = ip
    return clients

def generate_terraform(clients):
    template=''
    with open(TMPL_FILE, 'r') as file:
        template = file.read()
    
    for host,ip in clients.items():
        content = template.replace("<HOSTNAME>",host).replace("<IP>",ip)
        path = f'{OUTPUT_PATH}/{host}.tf'
        with open(path,'w') as writer:
            writer.write(content)
            writer.flush()
        print(f'Wrote {path}')


async def main():
    print("Running client generation")
    host = get_env_var("UNIFI_HOST", required=True)
    port = int(get_env_var("UNIFI_PORT", 443))
    username = get_env_var("UNIFI_USERNAME", required=True)
    password = get_env_var("UNIFI_PASSWORD", required=True)
    site = get_env_var("UNIFI_SITE", 'default')
    ssl_verify_str = get_env_var("UNIFI_SSL_VERIFY", "true").lower()
    ssl_verify = ssl_verify_str not in ["false", "0", "no"]
    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True)) as session:
        config = Configuration(
            host= host,
            port=port,
            username=username,
            password=password,
            site=site,
            session=session,
            ssl_context=None if ssl_verify else ssl_verify
        )
        controller = Controller(
            config
        )
        
        try:
            print("Starting....")
            print(f"Logging into {host}")
            await controller.login()
            print("Fetching Clients...")
            clients = await list_clients(controller)
            print("Generating Terraform...")
            generate_terraform(clients)
        except Exception as e:
            print(f'Failed fetching clients: {e}')

if __name__ == "__main__":
    asyncio.run(main())
