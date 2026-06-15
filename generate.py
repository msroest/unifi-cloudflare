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

def normalize_hostname(hostname):
    return re.sub(r"[^a-z0-9A-Z\-_\.]", "", hostname).lower()

def parse_hostname_filter(raw_value):
    excluded = set()
    for hostname in raw_value.split(","):
        normalized = normalize_hostname(hostname.strip())
        if normalized:
            excluded.add(normalized)
    return excluded

async def list_clients(controller, excluded_hostnames=None):
    excluded_hostnames = set(excluded_hostnames or [])
    clients={}
    await controller.clients.update()
    for client in controller.clients.values():
        primary_hostname_raw = client.hostname or client.name or client.mac.replace(":","-")
        ip = client.ip
        hostname=normalize_hostname(primary_hostname_raw)
        if hostname=='' or ip=='':
            continue
        if hostname not in excluded_hostnames:
            clients[hostname]=ip
        else:
            print(f"Skipping excluded hostname: {hostname}")
        # If there is a name set also add a dns record for that.
        if client.name:
            alias = normalize_hostname(client.name)
            if alias and alias != hostname:
                if alias not in excluded_hostnames:
                    clients[alias] = ip
                else:
                    print(f"Skipping excluded hostname: {alias}")
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
    excluded_hostnames = parse_hostname_filter(get_env_var("UNIFI_EXCLUDE_HOSTNAMES", ""))
    if excluded_hostnames:
        print(f"Excluding hostnames: {', '.join(sorted(excluded_hostnames))}")
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
            clients = await list_clients(controller, excluded_hostnames)
            print("Generating Terraform...")
            generate_terraform(clients)
        except Exception as e:
            print(f'Failed fetching clients: {e}')

if __name__ == "__main__":
    asyncio.run(main())
