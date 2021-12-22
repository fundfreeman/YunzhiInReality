import asyncio
from aiohttp.connector import TCPConnector

from yarl import URL
from typing import Any, Iterable, List, Tuple, Type, Union, Optional

import aiohttp
from aiohttp.typedefs import JSONEncoder, StrOrURL, LooseCookies, LooseHeaders
from aiohttp import BaseConnector
from aiohttp.client import _RequestContextManager, ClientTimeout
from aiohttp.abc import AbstractCookieJar
from aiohttp.client_reqrep import ClientRequest, ClientResponse
from aiohttp.client_ws import ClientWebSocketResponse
from aiohttp.helpers import BasicAuth, sentinel
from aiohttp.http_writer import HttpVersion
from aiohttp.http import HttpVersion11
from aiohttp.tracing import TraceConfig

import pyDes
import base64
import json
import time
import random

from pathgen import GEO_POINT
from const import *
default_headers = {
    'User-Agent': 'okhttp/3.12.0',
    'isApp': 'app',
    'version': APP_EDITION,
    'platform': 'android',
    'Content-Type': 'text/plain; charset=utf-8',
}

POST_DES = pyDes.des(b'YUNZHIEE', mode=pyDes.CBC, IV=b'\x01\x02\x03\x04\x05\x06\x07\x08', padmode=pyDes.PAD_PKCS5)

class YZError(BaseException):
    def __init__(self, message : str) -> None:
        super().__init__(message)

class YZEncryptClientSession(aiohttp.ClientSession) :
    def __init__(
        self,
        base_url: Optional[StrOrURL] = None,
        *,
        connector: Optional[BaseConnector] = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        cookies: Optional[LooseCookies] = None,
        headers: Optional[LooseHeaders] = None,
        skip_auto_headers: Optional[Iterable[str]] = None,
        auth: Optional[BasicAuth] = None,
        json_serialize: JSONEncoder = json.dumps,
        request_class: Type[ClientRequest] = ClientRequest,
        response_class: Type[ClientResponse] = ClientResponse,
        ws_response_class: Type[ClientWebSocketResponse] = ClientWebSocketResponse,
        version: HttpVersion = HttpVersion11,
        cookie_jar: Optional[AbstractCookieJar] = None,
        connector_owner: bool = True,
        raise_for_status: bool = False,
        read_timeout: Union[float, object] = sentinel,
        conn_timeout: Optional[float] = None,
        timeout: Union[object, ClientTimeout] = sentinel,
        auto_decompress: bool = True,
        trust_env: bool = False,
        requote_redirect_url: bool = True,
        trace_configs: Optional[List[TraceConfig]] = None,
        read_bufsize: int = 2 ** 16,
    ) -> None:
        super().__init__(base_url=base_url, connector=connector, loop=loop, cookies=cookies, headers=headers, skip_auto_headers=skip_auto_headers, auth=auth, json_serialize=json_serialize, request_class=request_class, response_class=response_class, ws_response_class=ws_response_class, version=version, cookie_jar=cookie_jar, connector_owner=connector_owner, raise_for_status=raise_for_status, read_timeout=read_timeout, conn_timeout=conn_timeout, timeout=timeout, auto_decompress=auto_decompress, trust_env=trust_env, requote_redirect_url=requote_redirect_url, trace_configs=trace_configs, read_bufsize=read_bufsize)

    def post(self, url: StrOrURL, *, data: Any = None, encrypt : bool = True, **kwargs: Any) -> _RequestContextManager:
        if data and encrypt:
            data = base64.b64encode(POST_DES.encrypt(data))

        return super().post(url, data=data, **kwargs)

class YZSession:
    http_sess : YZEncryptClientSession
    base_url : URL
    device_id : str
    token : str
    school_id : str
    account_id : str
    auth_headers : dict[str, str]

    def __init__(
        self, 
        base_url : Union[str, URL], 
        school_id : str = None, 
        account_id : str = None,
        deviceid : str = None, 
        token : str = None, 
        connector : BaseConnector = None
    ) -> None :
        self.auth_headers = {
            'deviceid' : deviceid,
            'token' : token
        }
        self.http_sess = YZEncryptClientSession(
            connector=connector if connector else TCPConnector(),
            connector_owner=False if connector else True
        )
        if not isinstance(base_url, URL):
            base_url = URL(base_url)
        
        self.base_url = base_url
        self.school_id = school_id
        self.account_id = account_id

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.http_sess.close()

    def __del__(self):
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.http_sess.close())
            else:
                loop.run_until_complete(self.http_sess.close())
        except Exception:
            pass

    def close(self):
        self.__del__()

    def APIpost(self, path : str, encrypt : bool = True, data = None, auth_headers : bool = True, headers : Optional[LooseHeaders] = None, **kwargs: Any) -> _RequestContextManager:
        if isinstance(data, dict):
            data = json.dumps(data)
        if not headers:
            headers = default_headers.copy()
        if auth_headers:
            headers.update(self.auth_headers)

        return self.http_sess.post(self.base_url.with_path(path), data=data, encrypt=encrypt, headers=headers, **kwargs)


    async def APIpost_json(self, path : str, encrypt : bool = True, data = None, auth_headers : bool = True, headers : Optional[LooseHeaders] = None, **kwargs: Any) -> dict:
        async with self.APIpost(path, encrypt, data, auth_headers, headers, **kwargs) as resp:
            try:
                if resp.status != 200:
                    raise YZError(await resp.text())
                resp_json = await resp.json()
                if resp_json['code'] == 200:
                    return resp_json['data'] if 'data' in resp_json else None
                else:
                    raise YZError(resp_json['msg'])
            except YZError as err:
                raise err
            

class YZSchool:

    def __init__(self, base_url : Union[str, URL], school_id : str, max_connection : int = 1) -> None :
        self.connector = aiohttp.TCPConnector(limit_per_host=max_connection, keepalive_timeout=POINT_BATCH*SAMPLE_PERIOD*2/1000)
        self.http_sess = YZEncryptClientSession(
            connector=self.connector
        )
        if not isinstance(base_url, URL):
            base_url = URL(base_url)
        
        self.base_url = base_url
        self.school_id = school_id

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.http_sess.close()

    def __del__(self):
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.http_sess.close())
            else:
                loop.run_until_complete(self.http_sess.close())
        except Exception:
            pass

    def close(self):
        self.__del__()
        
    async def login(self, username : str, password : str) -> YZSession:
        deviceid = f'{random.randint(0, 99)}{int(time.time()*1000)}'
        headers={
            'deviceid': deviceid,
            'token': ''
        }
        headers.update(default_headers)
        async with self.http_sess.post(
                self.base_url.with_path('/login/appLogin'),
                headers=headers,
                data=json.dumps({
                    'userName': username,
                    'password': password,
                    'schoolId': self.school_id,
                    'type': '1'
                })
            ) as resp:

            try:
                if resp.status != 200:
                    raise YZError(await resp.text())
                resp_json = await resp.json()
                if resp_json['code'] == 200:
                    return YZSession(
                        self.base_url,
                        self.school_id,
                        username,
                        deviceid,
                        resp_json['data']['token'],
                        self.connector
                    )
                else:
                    raise YZError(resp_json['msg'])
            except YZError as err:
                raise err

async def check_update(base_url : Union[str, URL], version_code : str) -> bool:
    async with YZSession(base_url) as sess:
        data = await sess.APIpost_json('/getAppEdition', auth_headers=False, data={
            'type': '2'
        })
        return version_code == data['appEdtitionNumber']
        
def parse_points(data : str) -> List[GEO_POINT]:
    str_points = data.split('|')
    points = []
    for st in str_points:
        ll = st.split(',')
        points.append((float(ll[1]), float(ll[0])))

    return points

def mpers2minperkm(ms : float) -> float:
    return 1 / (ms * 0.06)

def minperkm2mpers(minkm : float) -> float:
    return 1 / minkm / 0.06