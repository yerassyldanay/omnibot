PROXY_LIST = [
    ('yerassyldanay', 'nS9jSPh8NJ', 'http://5.133.163.86:50100'),
    ('yerassyldanay', 'nS9jSPh8NJ', 'http://185.127.164.25:50100'),
    ('yerassyldanay', 'nS9jSPh8NJ', 'http://185.127.165.203:50100'),
    ('yerassyldanay', 'nS9jSPh8NJ', 'http://5.133.163.88:50100'),
    ('yerassyldanay', 'nS9jSPh8NJ', 'http://185.127.164.142:50100'),
]

import aiohttp
import asyncio

for i in range(5):
    username = PROXY_LIST[i][0]
    password = PROXY_LIST[i][1]

    proxy_auth = aiohttp.BasicAuth(username, password)
    proxy_url = PROXY_LIST[i][2]

    async def make_request(url):
        async with aiohttp.ClientSession() as session:
            print(proxy_url, username, password)
            async with session.get(url, proxy=proxy_url, proxy_auth=aiohttp.BasicAuth(username, password)) as response:
                return response.status

    url = 'https://www.google.com'
    status_code = asyncio.run(make_request(url))
    print(status_code)
