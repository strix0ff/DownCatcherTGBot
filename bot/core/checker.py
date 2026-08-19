import asyncio

import json

import aiofiles

from sh.redis import (
    redissession
)

from pathlib import ( 
    Path
)

from bot.config import (
    ADMINID
)

lang_cfg_path = Path('lang.json')

async def GetUserLang():
    if lang_cfg_path.is_file():
        async with aiofiles.open(lang_cfg_path, 'r', encoding='utf-8') as file:
            data = await file.read()
            data = json.loads(data)
            lang = data['lang']
    else:
        lang = 'en'
    return lang

DownNow = {}

async def service_checker(bot):
    while True:
        CurLang = await GetUserLang()
        
        servicelist = [key async for key in redissession.scan_iter(match='service:*')]
    
        if servicelist:
            statuses = await redissession.mget(servicelist)
    
            for key, status in zip(servicelist, statuses):
                keylist = key.split(':')
                id = keylist[1]
                name = keylist[2]
                if status == 'down' and (not id in DownNow):
                    DownNow[id] = status
                    if CurLang == 'en':
                        await bot.send_message(ADMINID, f'⚠️ Warning! Service <code>{name}</code> is down!', parse_mode='HTML')
                    elif CurLang == 'ru':
                        await bot.send_message(ADMINID, f'⚠️ Внимание! Сервис <code>{name}</code> лежит!', parse_mode='HTML')
                    elif CurLang == 'fr':
                        await bot.send_message(ADMINID, f'⚠️ Attention ! Le service <code>{name}</code> est tombé !', parse_mode='HTML')
                    elif CurLang == 'ch':
                        await bot.send_message(ADMINID, f'⚠️ 注意！服务 <code>{name}</code> 挂了！', parse_mode='HTML')
                elif status == 'notfound' and (not id in DownNow):
                    DownNow[id] = status
                    if CurLang == 'en': 
                        await bot.send_message(ADMINID, f'🤷‍♂️ Warning! Service <code>{name}</code> not found!', parse_mode='HTML')
                    elif CurLang == 'ru':
                        await bot.send_message(ADMINID, f'🤷‍♂️ Внимание! Сервис <code>{name}</code> не найден!', parse_mode='HTML')
                    elif CurLang == 'fr':
                        await bot.send_message(ADMINID, f'🤷‍♂️ Attention ! Le service <code>{name}</code> est introuvable !', parse_mode='HTML')
                    elif CurLang == 'ch':
                        await bot.send_message(ADMINID, f'🤷‍♂️ 注意！服务 <code>{name}</code> 未找到！', parse_mode='HTML')
                elif status == 'up':
                    if id in DownNow:
                        del DownNow[id]
        await asyncio.sleep(10)


