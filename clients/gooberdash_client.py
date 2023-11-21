import datetime
import aiohttp
import json
import os
import websocket
import requests

class AuthError(BaseException):
    pass


class GooberDashClient(object):
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.token = None
        self.session = None

    
    async def post(self, url: str, data={}, headers={}):
        if self.session == None:
            self.session = aiohttp.ClientSession(raise_for_status=True)

        async with self.session.post(
            url, headers=headers, data=json.dumps(data)
        ) as response:
            return await response.text()

    
    async def get(self, url, headers={}):
        if self.session == None:
            self.session = aiohttp.ClientSession(raise_for_status=True)

        async with self.session.get(url, headers=headers) as response:
            return await response.text()

    
    async def refresh_token(self):
        # Only refresh token if 9 minutes have passed
        if self.token != None:
            time = datetime.datetime.now() - self.last_refresh

            if time.seconds < 540:
                return

        data = {
            "email": self.username,
            "password": self.password,
            "vars": {
                "client_version": "99999",
            },
        }

        headers = {
            # Secret to initially access server.
            "authorization": os.environ["secret"]
        }

        # Get token
        try:
            response = json.loads(
                await self.post(
                    "https://gooberdash-api.winterpixel.io/v2/account/authenticate/email?create=false",
                    data=data,
                    headers=headers,
                )
            )
            self.token = response["token"]
            self.last_refresh = datetime.datetime.now()
        except:
            raise AuthError("Invalid details!")

    
    async def get_config(self):
        await self.refresh_token()
        
        ws = websocket.create_connection(
          f"wss://gooberdash-api.winterpixel.io/ws?lang=en&status=true&token={self.token}"
        )
        player_fetch_data = {"rpc": {
          "id": "player_fetch_data", "payload": "{}"}}
        ws.send(json.dumps(player_fetch_data).encode())
        ws.recv()
        msg = ws.recv()
        msg_json_loads = json.loads(msg)["rpc"]["payload"]
        server_config = json.loads(msg_json_loads)["data"]
        return server_config

    
    async def query_leaderboard(
        self,
        season: int,
        leaderboard_id: str,
        limit: int = 100,
        cursor: str = "",
        owner_ids: str = "",
    ):
        await self.refresh_token()
        
        headers = {"authorization": f"Bearer {self.token}"}

        url = "https://gooberdash-api.winterpixel.io/v2/leaderboard/"
        url += f"{leaderboard_id}.{season}"
        url += f"?limit={limit}"
        url += f"&cursor={cursor}" if cursor != "" else ""
        url += f"&owner_ids={owner_ids}" if owner_ids != "" else ""
        
        return json.loads(
            await self.get(
                url,
                headers=headers,
            )
        )

    
    async def user_info(self, user_id: str):
        await self.refresh_token()

        ws = websocket.create_connection(
            f"wss://gooberdash-api.winterpixel.io/ws?lang=en&status=true&token={self.token}"
        )
        query_player_profile = {"rpc":{"id":"query_player_profile","payload":'{\"user_id\": \"'+user_id+'\"}'}}
      
        ws.send(json.dumps(query_player_profile).encode())
        ws.recv()
        msg = ws.recv()
        try:
            player_info = json.loads(msg)["rpc"]["payload"]
        except KeyError:
            return "invalid_user_id"
        return player_info


    async def user_info_2(self, ids: str, usernames: str = ""):
        await self.refresh_token()
    
        headers = {"authorization": f"Bearer {self.token}"}

        query_url = "https://gooberdash-api.winterpixel.io/v2/user" + (f"?usernames={usernames}" if ids == "" else f"?ids={ids}")
        return json.loads(
            await self.get(
                query_url,
                headers=headers
            )
        )

    
    async def level_info(self, level_id: str):
        await self.refresh_token()

        headers = {"authorization": f"Bearer {self.token}"}
        
        return json.loads(
            await self.post(
                "https://gooberdash-api.winterpixel.io/v2/rpc/levels_editor_get",
                data='{\"id\":\"'+level_id+'\"}',
                headers=headers
            )
        )


    async def official_levels(self):
        await self.refresh_token()
        
        ws = websocket.create_connection(
            f"wss://gooberdash-api.winterpixel.io/ws?lang=en&status=true&token={self.token}"
        )
        query_official_levels = {"rpc":{"id":"levels_editor_list_public_templates","payload":"{}"}}
    
        ws.send(json.dumps(query_official_levels).encode())
        ws.recv()
        msg = ws.recv()
        official_levels = json.loads(msg)["rpc"]["payload"]
        return official_levels

    
    def non_async_user_info_2(self, ids: str):
        headers = {"authorization": f"Bearer {self.token}"}
        query_url = f"https://gooberdash-api.winterpixel.io/v2/user?ids={ids}"
        response = requests.get(
                query_url,
                headers=headers
        )
        return json.loads(response.content)
