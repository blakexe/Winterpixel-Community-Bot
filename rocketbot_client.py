import datetime, aiohttp, json, os

class AuthError(BaseException): pass

class RocketBotClient(object):
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.token = None
        self.session = None

    async def post(self, url: str, data = {}, headers = {}):
        if self.session == None:
            self.session = aiohttp.ClientSession(raise_for_status=True)
        
        async with self.session.post(url, headers = headers, data = json.dumps(data)) as response:
            return await response.text()

    async def get(self, url, headers = {}):
        if self.session == None:
            self.session = aiohttp.ClientSession(raise_for_status=True)

        async with self.session.get(url, headers = headers) as response:
            return await response.text()
    
    async def refresh_token(self):        
        #Only refresh token if 9 minutes have passed
        if self.token != None:
            time = datetime.datetime.now() - self.last_refresh

            if time.seconds < 540:
                return

        data = {
            "email": self.username,
            "password": self.password,
            "vars":{
                "client_version": "99999",
            }
        }

        headers = {
            #Secret to initially access server.
            "authorization": os.environ['secret']
        }

        #Get token
        try:
            response = json.loads(await self.post("https://dev-nakama.winterpixel.io/v2/account/authenticate/email?create=false", data=data, headers=headers))
            self.token = response['token']
            self.last_refresh = datetime.datetime.now()
        except:
            raise AuthError("Invalid details!")

    async def get_config(self):
        await self.refresh_token()

        headers = {
            "authorization": f"Bearer {self.token}"
        }

        return json.loads(await self.post("https://dev-nakama.winterpixel.io/v2/rpc/winterpixel_get_config", headers=headers, data="{}"))

    async def query_leaderboard(self, season: int, leaderboard_id:str = "tankkings_points"):
        await self.refresh_token()

        data = {
            "leaderboard": leaderboard_id,
            "limit": 50,
            "cursor": "",
            "owner_ids": [],
            "season": season
        }

        headers = {
            "authorization": f"Bearer {self.token}"
        }

        return json.loads(await self.post("https://dev-nakama.winterpixel.io/v2/rpc/query_leaderboard", data=json.dumps(data), headers=headers))   

    async def friend_code_to_id(self, friend_code: str):
        await self.refresh_token()

        data = {
            "friend_code": friend_code
        }

        headers = {
            "authorization": f"Bearer {self.token}"
        }

        return json.loads(await self.post("https://dev-nakama.winterpixel.io/v2/rpc/winterpixel_query_user_id_for_friend_code", data=json.dumps(data), headers=headers)) 

    async def get_user(self, user_id: str):
        await self.refresh_token()

        data = {
            "ids": [user_id]
        }

        headers = {
            "authorization": f"Bearer {self.token}"
        }

        return json.loads(await self.post("https://dev-nakama.winterpixel.io/v2/rpc/rpc_get_users_with_profile", data=json.dumps(data), headers=headers))  

    async def query_users(self, display_name: str):
        await self.refresh_token()

        data = {
            "display_name": display_name
        }

        headers = {
            "authorization": f"Bearer {self.token}"
        }

        return json.loads(await self.post("https://dev-nakama.winterpixel.io/v2/rpc/rpc_get_ids_from_display_name", data=json.dumps(data), headers=headers)) 

    async def collect_time_bonus(self):
        await self.refresh_token()
        
        headers = {
            "authorization": f"Bearer {self.token}"
        }
        
        return json.loads(await self.post("https://dev-nakama.winterpixel.io/v2/rpc/collect_timed_bonus", data='{}', headers=headers))  