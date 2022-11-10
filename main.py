#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import NoReturn

import os
import nonebot
import aiocqhttp
import asyncio
import aiohttp
import aiofiles

import hoshino

async def moegoe_gs(id: int, text: str) -> bytes:
	params = {
		'format': 'mp3',
		'id':     id,
		'text':   text.lstrip('\ufeff'),
	}
	async with aiohttp.ClientSession(raise_for_status=True) as session:
		async with session.get('https://genshin.azurewebsites.net/api/speak', params=params) as resp:
			return await resp.read()

async def moegoe_jp(id: int, text: str) -> bytes:
	params = {
		'id':     id,
		'text':   text.lstrip('\ufeff'),
	}
	async with aiohttp.ClientSession(raise_for_status=True) as session:
		async with session.get('https://moegoe.azurewebsites.net/api/speak', params=params) as resp:
			return await resp.read()

async def moegoe_kr(id: int, text: str) -> bytes:
	params = {
		'id':     id,
		'text':   text.lstrip('\ufeff'),
	}
	async with aiohttp.ClientSession(raise_for_status=True) as session:
		async with session.get('https://moegoe.azurewebsites.net/api/speakkr', params=params) as resp:
			return await resp.read()

speaker_map = {
	'派蒙': {'func': moegoe_gs, 'kwargs': {'id': 0}},
	'凯亚': {'func': moegoe_gs, 'kwargs': {'id': 1}},
	'安柏': {'func': moegoe_gs, 'kwargs': {'id': 2}},
	'丽莎': {'func': moegoe_gs, 'kwargs': {'id': 3}},
	'琴': {'func': moegoe_gs, 'kwargs': {'id': 4}},
	'香菱': {'func': moegoe_gs, 'kwargs': {'id': 5}},
	'枫原万叶': {'func': moegoe_gs, 'kwargs': {'id': 6}},
	'迪卢克': {'func': moegoe_gs, 'kwargs': {'id': 7}},
	'温迪': {'func': moegoe_gs, 'kwargs': {'id': 8}},
	'可莉': {'func': moegoe_gs, 'kwargs': {'id': 9}},
	'早柚': {'func': moegoe_gs, 'kwargs': {'id': 10}},
	'托马': {'func': moegoe_gs, 'kwargs': {'id': 11}},
	'芭芭拉': {'func': moegoe_gs, 'kwargs': {'id': 12}},
	'优菈': {'func': moegoe_gs, 'kwargs': {'id': 13}},
	'云堇': {'func': moegoe_gs, 'kwargs': {'id': 14}},
	'钟离': {'func': moegoe_gs, 'kwargs': {'id': 15}},
	'魈': {'func': moegoe_gs, 'kwargs': {'id': 16}},
	'凝光': {'func': moegoe_gs, 'kwargs': {'id': 17}},
	'雷电将军': {'func': moegoe_gs, 'kwargs': {'id': 18}},
	'北斗': {'func': moegoe_gs, 'kwargs': {'id': 19}},
	'甘雨': {'func': moegoe_gs, 'kwargs': {'id': 20}},
	'七七': {'func': moegoe_gs, 'kwargs': {'id': 21}},
	'刻晴': {'func': moegoe_gs, 'kwargs': {'id': 22}},
	'神里绫华': {'func': moegoe_gs, 'kwargs': {'id': 23}},
	'戴因斯雷布': {'func': moegoe_gs, 'kwargs': {'id': 24}},
	'雷泽': {'func': moegoe_gs, 'kwargs': {'id': 25}},
	'神里绫人': {'func': moegoe_gs, 'kwargs': {'id': 26}},
	'罗莎莉亚': {'func': moegoe_gs, 'kwargs': {'id': 27}},
	'阿贝多': {'func': moegoe_gs, 'kwargs': {'id': 28}},
	'八重神子': {'func': moegoe_gs, 'kwargs': {'id': 29}},
	'宵宫': {'func': moegoe_gs, 'kwargs': {'id': 30}},
	'荒泷一斗': {'func': moegoe_gs, 'kwargs': {'id': 31}},
	'九条裟罗': {'func': moegoe_gs, 'kwargs': {'id': 32}},
	'夜兰': {'func': moegoe_gs, 'kwargs': {'id': 33}},
	'珊瑚宫心海': {'func': moegoe_gs, 'kwargs': {'id': 34}},
	'五郎': {'func': moegoe_gs, 'kwargs': {'id': 35}},
	'散兵': {'func': moegoe_gs, 'kwargs': {'id': 36}},
	'女士': {'func': moegoe_gs, 'kwargs': {'id': 37}},
	'达达利亚': {'func': moegoe_gs, 'kwargs': {'id': 38}},
	'莫娜': {'func': moegoe_gs, 'kwargs': {'id': 39}},
	'班尼特': {'func': moegoe_gs, 'kwargs': {'id': 40}},
	'申鹤': {'func': moegoe_gs, 'kwargs': {'id': 41}},
	'行秋': {'func': moegoe_gs, 'kwargs': {'id': 42}},
	'烟绯': {'func': moegoe_gs, 'kwargs': {'id': 43}},
	'久岐忍': {'func': moegoe_gs, 'kwargs': {'id': 44}},
	'辛焱': {'func': moegoe_gs, 'kwargs': {'id': 45}},
	'砂糖': {'func': moegoe_gs, 'kwargs': {'id': 46}},
	'胡桃': {'func': moegoe_gs, 'kwargs': {'id': 47}},
	'重云': {'func': moegoe_gs, 'kwargs': {'id': 48}},
	'菲谢尔': {'func': moegoe_gs, 'kwargs': {'id': 49}},
	'诺艾尔': {'func': moegoe_gs, 'kwargs': {'id': 50}},
	'迪奥娜': {'func': moegoe_gs, 'kwargs': {'id': 51}},
	'鹿野院平藏': {'func': moegoe_gs, 'kwargs': {'id': 52}},
	'宁宁': {'func': moegoe_jp, 'kwargs': {'id': 0}},
	'爱瑠': {'func': moegoe_jp, 'kwargs': {'id': 1}},
	'芳乃': {'func': moegoe_jp, 'kwargs': {'id': 2}},
	'茉子': {'func': moegoe_jp, 'kwargs': {'id': 3}},
	'丛雨': {'func': moegoe_jp, 'kwargs': {'id': 4}},
	'小春': {'func': moegoe_jp, 'kwargs': {'id': 5}},
	'七海': {'func': moegoe_jp, 'kwargs': {'id': 6}},
	'Sua': {'func': moegoe_kr, 'kwargs': {'id': 0}},
	'Mimiru': {'func': moegoe_kr, 'kwargs': {'id': 1}},
	'Arin': {'func': moegoe_kr, 'kwargs': {'id': 2}},
	'Yeonhwa': {'func': moegoe_kr, 'kwargs': {'id': 3}},
	'Yuhwa': {'func': moegoe_kr, 'kwargs': {'id': 4}},
	'Seonbae': {'func': moegoe_kr, 'kwargs': {'id': 5}},
}

sv = hoshino.Service(
	'MoeGoe',
	visible=True,
	enable_on_default=True,
	help_='[让xxx说] 合成语音\n' + ','.join(speaker_map.keys())
)

@sv.on_prefix(*map(lambda x: f"让{x}说", speaker_map.keys()))
async def speak(bot, ev: nonebot.message.CQEvent) -> NoReturn:
	speaker = ev['prefix'].lstrip('让').rstrip('说')
	caller = speaker_map[speaker]
	text = ev.message.extract_plain_text().strip().lstrip(ev['prefix'])
	try:
		data = await caller['func'](**caller['kwargs'], text=text)
	except Exception as e:
		sv.logger.error(caller)
		sv.logger.error(text)
		sv.logger.error(e)
		await bot.send(ev, '获取语音失败', at_sender=True)
	else:
		async with aiofiles.tempfile.NamedTemporaryFile('wb', delete=True) as f:
			sv.logger.debug(f"save to: {f.name}")
			await f.write(data)
			os.chmod(f.name, 0o644)
			msg = nonebot.message.MessageSegment.record(f"file:///{f.name}")
			await bot.send(ev, msg, at_sender=False)
