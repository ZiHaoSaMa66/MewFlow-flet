import asyncio
import string
import secrets
from typing import Dict, Any, Optional, Union
from urllib.parse import urljoin, urlencode

import aiohttp
import hashlib

def md5(data: str) -> str:
    """返回输入字符串的 MD5 哈希值（32位小写十六进制字符串）"""
    return hashlib.md5(data.encode('utf-8')).hexdigest()

# from cryptography.hazmat.primitives import hashes
# from cryptography.hazmat.backends import default_backend
# def _crypt_md5(data: str) -> str:
    # """使用 cryptography 库计算 MD5 哈希（32位小写十六进制）"""
    # digest = hashes.Hash(hashes.MD5(), backend=default_backend())
    # digest.update(data.encode('utf-8'))
    # return digest.finalize().hex()


class NavidromeAPI:
    def __init__(self, base_url: str, username: str, password: str,last_x_nd_auth_token: str|None = None):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.client_name = 'MewFlow'
        self.version = '1.16.1'
        self.x_nd_auth_token: Optional[str] = None
        if last_x_nd_auth_token:
            print(f"debug > 提供了上次的x_nd_auth_token {last_x_nd_auth_token}")
            self.x_nd_auth_token = last_x_nd_auth_token
        # aiohttp session 由外部管理或 lazily 创建
        self._session: Optional[aiohttp.ClientSession] = None

    def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    def generate_random_string(self, length: int = 6) -> str:
        return ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(length))

    def generate_auth_token(self) -> Dict[str, str]:
        salt = self.generate_random_string()
        token = md5(self.password + salt)
        return {"salt": salt, "token": token}

    def build_url(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> str:
        if params is None:
            params = {}
        auth = self.generate_auth_token()
        base_params = {
            'u': self.username,
            't': auth['token'],
            's': auth['salt'],
            'v': self.version,
            'c': self.client_name,
            'f': 'json',
        }
        base_params.update(params)
        url = urljoin(self.base_url, f"/rest/{endpoint}.view")
        query = urlencode(base_params)
        return f"{url}?{query}"

    async def request_rest(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Union[bytes, Dict[str, Any]]:
        url = self.build_url(endpoint, params)
        session = self._get_session()
        async with session.get(url) as resp:
            if not resp.ok:
                raise aiohttp.ClientResponseError(
                    resp.request_info, resp.history,
                    status=resp.status,
                    message=f"HTTP {resp.status}: {resp.reason}"
                )
            content_type = resp.headers.get("Content-Type", "").lower()

            # 音频/图像：返回 bytes（代替前端的 createObjectURL）
            if content_type.startswith("audio/") or content_type.startswith("image/"):
                return await resp.read()  # bytes

            # JSON 响应
            try:
                data = await resp.json()
            except Exception as e:
                raise ValueError(f"Failed to parse JSON from {url}: {e}")

            sub_resp = data.get("subsonic-response")
            if not sub_resp or sub_resp.get("status") != "ok":
                err = sub_resp.get("error", {})
                msg = err.get("message", "Unknown error")
                raise ValueError(f"API error: {msg} (code {err.get('code')})")

            return sub_resp

    async def request_api(
        self,
        endpoint: str,
        url_params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        method: str = "GET"
    ) -> Dict[str, Any]:
        url = urljoin(self.base_url, f"/{endpoint}")
        if url_params:
            url += "?" + urlencode(url_params)

        headers = {
            "Client": self.client_name,
            "Content-Type": "application/json",
        }
        if self.x_nd_auth_token:
            headers["x-nd-authorization"] = f"Bearer {self.x_nd_auth_token}"

        session = self._get_session()
        kwargs = {"headers": headers}
        if method in ("POST", "PUT") and json_data is not None:
            kwargs["json"] = json_data

        async with session.request(method, url, **kwargs) as resp:
            if not resp.ok:
                raise aiohttp.ClientResponseError(
                    resp.request_info, resp.history,
                    status=resp.status,
                    message=f"HTTP {resp.status}: {resp.reason}"
                )
            try:
                return await resp.json()
            except Exception as e:
                raise ValueError(f"Failed to parse JSON from {url}: {e}")

    async def auth_and_login(self) -> Dict[str, Any]:
        data = await self.request_api(
            "auth/login",
            json_data={"username": self.username, "password": self.password},
            method="POST"
        )
        self.x_nd_auth_token = data.get("token")
        return data

    # ===== 高阶 API 方法（与 JS 一一对应）=====
    async def get_playlist(self, _end: int, _order: str, _sort: str, _start: int):
        return await self.request_api("api/playlist", {
            "_end": _end, "_order": _order, "_sort": _sort, "_start": _start
        })

    async def get_playlist_info(self, playlist_id: str):
        return await self.request_api(f"api/playlist/{playlist_id}")

    async def get_playlist_songs(self, playlist_id: str, _end: int, _order: str, _sort: str, _start: int):
        return await self.request_api(f"api/playlist/{playlist_id}/tracks", {
            "_end": _end, "_order": _order, "_sort": _sort, "_start": _start
        })

    async def get_music_folders(self):
        return await self.request_rest("getMusicFolders")

    async def get_artists(self):
        return await self.request_rest("getArtists")

    async def get_artist(self, artist_id: str):
        return await self.request_rest("getArtist", {"id": artist_id})

    async def get_album(self, album_id: str):
        return await self.request_rest("getAlbum", {"id": album_id})

    async def get_song(self, song_id: str):
        return await self.request_rest("getSong", {"id": song_id})

    async def search3(self, query: str):
        return await self.request_rest("search3", {"query": query})

    async def ping(self):
        return await self.request_rest("ping")

    async def get_random_songs(self):
        return await self.request_rest("getRandomSongs")

    async def get_cover_art(self, song_id: str, size: int):
        # 注：你 JS 中的 cover_block_sizes 是全局变量，此处需你补充逻辑
        # 示例：假设 cover_block_sizes = 500
        cover_block_sizes = 500
        if cover_block_sizes < size:
            return await self.request_rest("getCoverArt", {"id": song_id, "size": size})
        else:
            return b""  # 或 raise / return default path

    async def stream_blob(self, song_id: str) -> bytes:
        return await self.request_rest("stream", {"id": song_id})

    async def stream_url(self, song_id: str) -> str:
        return self.build_url("stream", {"id": song_id})

    async def scrobble(self, song_id: str):
        return await self.request_rest("scrobble", {"id": song_id})

    async def get_song_sort_list(self, _end: int, _order: str, _sort: str, _start: int):
        return await self.request_api("api/song", {
            "_end": _end, "_order": _order, "_sort": _sort, "_start": _start
        })

    async def get_lyrics_by_song_id(self, song_id: str):
        return await self.request_rest("getLyricsBySongId", {"id": song_id})

    async def get_lyrics_helper(self, song_id: str):
        resp = await self.get_lyrics_by_song_id(song_id)
        structured = resp.get("lyricsList", {}).get("structuredLyrics")
        if not structured or not structured[0].get("line"):
            return []
        return structured[0]["line"]

    async def scan_new_songs(self, is_full_scan: bool):
        return await self.request_rest("startScan", {"fullScan": str(is_full_scan).lower()})

    async def get_scan_status(self):
        return await self.request_rest("getScanStatus")

    # ===== 生命周期管理 =====
    async def close(self):
        if self._session:
            await self._session.close()
            self._session = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()