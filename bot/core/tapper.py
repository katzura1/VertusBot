import asyncio
import sys
from time import time
from random import randint
from urllib.parse import unquote

import aiohttp
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from pyrogram import Client
from pyrogram.errors import Unauthorized, UserDeactivated, AuthKeyUnregistered
from pyrogram.raw.functions.messages import RequestAppWebView, RequestWebView
from pyrogram.raw.types import InputBotAppShortName

from bot.config import settings
from bot.utils import logger
from bot.exceptions import InvalidSession
from .headers import headers


class Tapper:
    def __init__(self, tg_client: Client):
        self.session_name = tg_client.name
        self.tg_client = tg_client

    async def get_tg_web_data(self, proxy: str | None) -> str:
        if proxy:
            proxy = Proxy.from_str(proxy)
            proxy_dict = dict(
                scheme=proxy.protocol,
                hostname=proxy.host,
                port=proxy.port,
                username=proxy.login,
                password=proxy.password
            )
        else:
            proxy_dict = None

        self.tg_client.proxy = proxy_dict

        try:
            with_tg = True

            if not self.tg_client.is_connected:
                with_tg = False
                try:
                    await self.tg_client.connect()
                except (Unauthorized, UserDeactivated, AuthKeyUnregistered):
                    raise InvalidSession(self.session_name)

            web_view = await self.tg_client.invoke(RequestWebView(
                peer=await self.tg_client.resolve_peer('Vertus_App_bot'),
                bot=await self.tg_client.resolve_peer('Vertus_App_bot'),
                platform='android',
                from_bot_menu=False,
                url='https://thevertus.app/'
            ))

            auth_url = web_view.url
            tg_web_data = unquote(
                string=unquote(
                    string=auth_url.split('tgWebAppData=', maxsplit=1)[1].split('&tgWebAppVersion', maxsplit=1)[0]))

            if with_tg is False:
                await self.tg_client.disconnect()

            return tg_web_data

        except InvalidSession as error:
            raise error

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error during Authorization: {error}")
            await asyncio.sleep(delay=3)

    async def get_data(self, http_client: aiohttp.ClientSession) -> dict[str]:
        try:
            response = await http_client.post(url='https://api.thevertus.app/users/get-data')
            response.raise_for_status()

            response_json = await response.json()

            return response_json
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error while getting data: {error}")
            await asyncio.sleep(delay=3)

    async def collect_reward(self, http_client: aiohttp.ClientSession) -> dict[str]:
        try:
            response = await http_client.post(url='https://api.thevertus.app/game-service/collect')
            response.raise_for_status()

            response_json = await response.json()

            return response_json
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error while collecting reward: {error}")
            await asyncio.sleep(delay=3)
    
    async def upgrade_ability(self, http_client: aiohttp.ClientSession, ability: str) -> dict[str]:
        try:
            allowed_ability = ['farm', 'population', 'storage']
            if ability not in allowed_ability:
                raise ValueError(f"Ability '{ability}' is not recognized. Allowed abilities: {allowed_ability}")

            response = await http_client.post(url='https://api.thevertus.app/users/upgrade', json={'upgrade': ability})
            response.raise_for_status()

            response_json = await response.json()

            return response_json
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error while upgrading ability: {error}")
            await asyncio.sleep(delay=3)

    async def check_proxy(self, http_client: aiohttp.ClientSession, proxy: Proxy) -> None:
        try:
            response = await http_client.get(url='https://httpbin.org/ip', timeout=aiohttp.ClientTimeout(5))
            ip = (await response.json()).get('origin')
            logger.info(f"{self.session_name} | Proxy IP: {ip}")
        except Exception as error:
            logger.error(f"{self.session_name} | Proxy: {proxy} | Error: {error}")

    async def run(self, proxy: str | None) -> None:
        access_token_created_time = 0
        turbo_time = 0
        active_turbo = False

        proxy_conn = ProxyConnector().from_url(proxy) if proxy else None

        async with aiohttp.ClientSession(headers=headers, connector=proxy_conn) as http_client:
            if proxy:
                await self.check_proxy(http_client=http_client, proxy=proxy)

            while True:
                try:
                    if time() - access_token_created_time >= 3600:
                        tg_web_data = await self.get_tg_web_data(proxy=proxy)
                        http_client.headers["authorization"] = "Bearer " + tg_web_data
                        headers["authorization"] = "Bearer "+tg_web_data
                        access_token_created_time = time()
                    
                    user_data = await self.get_data(http_client=http_client)
                    user_data = user_data['user']

                    balance = user_data['balance']/1000000000000000000
                    #change decimal 6 only
                    balance = round(balance, 6)
                    walletAddress = user_data['walletAddress']
                    abilites = user_data['abilities']
                    farm = abilites['farm']
                    population = abilites['population']
                    storage = abilites['storage']

                    logger.info(f"{self.session_name} | Balance: {balance} | Wallet Address: {walletAddress}")
                    #farm level
                    logger.info(f"{self.session_name} | Farm ({farm['title']}) | Level: {farm['level']} | Price Level Up : {farm['priceToLevelUp']}")
                    #population level
                    logger.info(f"{self.session_name} | Population ({population['title']}) | Level: {population['level']} | Price Level Up : {population['priceToLevelUp']}")
                    #storage level
                    logger.info(f"{self.session_name} | Storage ({storage['title']}) | Level: {storage['level']} | Price Level Up : {storage['priceToLevelUp']}")

                    #claim rewards
                    collect = await self.collect_reward(http_client=http_client)
                    if(collect['newBalance']):
                        new_balance = collect['newBalance']/1000000000000000000
                        balance = round(new_balance, 6)
                        logger.success(f"{self.session_name} | Reward Claimed! | New Balance: {balance}")
                    else:
                        logger.info(f"{self.session_name} | No Reward Available")

                    #upgrade ability
                    if balance > farm['priceToLevelUp'] and settings.AUTO_UPGRADE_FARM and farm['level'] < settings.MAX_FARM_LEVEL:
                        upgrade = await self.upgrade_ability(http_client=http_client, ability='farm')
                        if(upgrade['newBalance']):
                            new_balance = balance - farm['priceToLevelUp']
                            balance = round(new_balance, 6)
                            logger.success(f"{self.session_name} | Farm Upgraded! | New Balance: {balance}")
                        else:
                            logger.error(f"{self.session_name} | Farm Upgrade Failed")
                    elif balance > population['priceToLevelUp'] and settings.AUTO_UPGRADE_POPULATION and population['level'] < settings.MAX_POPULATION_LEVEL:
                        upgrade = await self.upgrade_ability(http_client=http_client, ability='population')
                        if(upgrade['newBalance']):
                            new_balance = balance - population['priceToLevelUp']
                            balance = round(new_balance, 6)
                            logger.success(f"{self.session_name} | Population Upgraded! | New Balance: {balance}")
                        else:
                            logger.error(f"{self.session_name} | Population Upgrade Failed")
                    elif balance > storage['priceToLevelUp'] and settings.AUTO_UPGRADE_STORAGE and storage['level'] < settings.MAX_STORAGE_LEVEL:
                        upgrade = await self.upgrade_ability(http_client=http_client, ability='storage')
                        if(upgrade['newBalance']):
                            new_balance = balance - storage['priceToLevelUp']
                            balance = round(new_balance, 6)
                            logger.success(f"{self.session_name} | Storage Upgraded! | New Balance: {balance}")
                        else:
                            logger.error(f"{self.session_name} | Storage Upgrade Failed")

                except InvalidSession as error:
                    raise error

                except Exception as error:
                    logger.error(f"{self.session_name} | Unknown error: {error}")
                    await asyncio.sleep(delay=3)

                else:
                    timeSleep = settings.SLEEP_TIME
                    

                    logger.info(f"Sleep {timeSleep}s")
                    await asyncio.sleep(delay=timeSleep)


async def run_tapper(tg_client: Client, proxy: str | None):
    try:
        await Tapper(tg_client=tg_client).run(proxy=proxy)
    except InvalidSession:
        logger.error(f"{tg_client.name} | Invalid Session")
