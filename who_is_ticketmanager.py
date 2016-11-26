#!/usr/bin/env python3

import aiohttp
import asyncio
import async_timeout
import base64
import configparser
import json

from bs4 import BeautifulSoup


def read_config():
    cfg_parser = configparser.ConfigParser()
    cfg_parser.read('~/.who_is_ticketmanager.cfg')
    all_section = cfg_parser['ALL']
    proxy_cfg = all_section['proxy']
    url_cfg = all_section['url']
    username_cfg = all_section['username']
    password_cfg = all_section['password']
    return (proxy_cfg, url_cfg, username_cfg, password_cfg)

async def parse_json_response(json_res):
    json_data = yield from json.loads(json_res)
    html_data = json_data['body']['view']['value']
    return html_data

async def parse_html_page(html_page):
    soup = BeautifulSoup(html_page, 'html.parser')
    soup.find()

def create_auth(username, password):
    raw_auth = '%s:%s' % (username, password)
    res = base64.b64encode(raw_auth.encode('utf-8'))
    return res

async def download_ticketmanager_site(session):
    # move this late rto a better position in the code...
    proxy, url, username, password = read_config()
    auth = 'Basic ' + create_auth(username, password).decode('utf-8')
    headers = {'Accept': 'application/json', 'Authorization': auth}

    with async_timeout.timeout(10):
        async with session.get(url, headers=headers, proxy=proxy) as response:
            return await response.text()

async def main(loop):
    async with aiohttp.ClientSession(loop=loop, ) as session:
        html = await download_ticketmanager_site(session)
        print(html)

if __name__ == '__main__':
    """
    This is a good training for the python 3.5 async programming.
    Fetch the html data as fast as possible, process it and send response....
    Problem: we only need one html response here and having nothing todo
    before we have that...
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
