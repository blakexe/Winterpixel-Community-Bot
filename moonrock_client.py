import datetime, aiohttp, json, os


class AuthError(BaseException):
    pass


class MoonRockClient(object):
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.token = None
        self.session = None

    async def post(self, url: str, data={}, headers={}):
        if self.session == None:
            self.session = aiohttp.ClientSession(raise_for_status=True)

        async with self.session.post(url,
                                     headers=headers,
                                     data=json.dumps(data)) as response:
            return await response.text()

    async def get(self, url, headers={}):
        if self.session == None:
            self.session = aiohttp.ClientSession(raise_for_status=True)

        async with self.session.get(url, headers=headers) as response:
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
            "vars": {
                "client_version": "99999",
            }
        }

        headers = {
            #Secret to initially access server.
            "authorization": os.environ['secret']
        }

        #Get token
        try:
            response = json.loads(await self.post(
                "https://asteroids-production-dev-nakama.winterpixel.io/v2/account/authenticate/email?create=false",
                data=data,
                headers=headers))
            self.token = response['token']
            self.last_refresh = datetime.datetime.now()
        except:
            raise AuthError("Invalid details!")

    async def get_config(self):
        await self.refresh_token()

        headers = {"authorization": f"Bearer {self.token}"}

        return json.loads(await self.post(
            "https://asteroids-production-dev-nakama.winterpixel.io/v2/rpc/winterpixel_get_config",
            headers=headers,
            data="{}"))

    async def query_leaderboard(self,
                                season: int,
                                leaderboard_id: str):
        await self.refresh_token()

        data = {
            "leaderboard": leaderboard_id,
            "limit": 100,
            "cursor": "",
            "owner_ids": [],
            "season": season
        }

        headers = {"authorization": f"Bearer {self.token}"}

        return json.loads(await self.post(
            "https://asteroids-production-dev-nakama.winterpixel.io/v2/rpc/query_leaderboard",
            data=json.dumps(data),
            headers=headers))
