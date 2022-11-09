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
		'text':   text,
	}
	async with aiohttp.ClientSession(raise_for_status=True) as session:
		async with session.get('https://genshin.azurewebsites.net/api/speak', params=params) as resp:
			return await resp.read()

async def moegoe_jp(id: int, text: str) -> bytes:
	params = {
		'id':     id,
		'text':   text,
	}
	async with aiohttp.ClientSession(raise_for_status=True) as session:
		async with session.get('https://moegoe.azurewebsites.net/api/speak', params=params) as resp:
			return await resp.read()

async def moegoe_kr(id: int, text: str) -> bytes:
	params = {
		'id':     id,
		'text':   text,
	}
	async with aiohttp.ClientSession(raise_for_status=True) as session:
		async with session.get('https://moegoe.azurewebsites.net/api/speakkr', params=params) as resp:
			return await resp.read()

speaker_map = {
	'派蒙': (moegoe_gs, 0),
	'凯亚': (moegoe_gs, 1),
	'安柏': (moegoe_gs, 2),
	'丽莎': (moegoe_gs, 3),
	'琴': (moegoe_gs, 4),
	'香菱': (moegoe_gs, 5),
	'枫原万叶': (moegoe_gs, 6),
	'迪卢克': (moegoe_gs, 7),
	'温迪': (moegoe_gs, 8),
	'可莉': (moegoe_gs, 9),
	'早柚': (moegoe_gs, 10),
	'托马': (moegoe_gs, 11),
	'芭芭拉': (moegoe_gs, 12),
	'优菈': (moegoe_gs, 13),
	'云堇': (moegoe_gs, 14),
	'钟离': (moegoe_gs, 15),
	'魈': (moegoe_gs, 16),
	'凝光': (moegoe_gs, 17),
	'雷电将军': (moegoe_gs, 18),
	'北斗': (moegoe_gs, 19),
	'甘雨': (moegoe_gs, 20),
	'七七': (moegoe_gs, 21),
	'刻晴': (moegoe_gs, 22),
	'神里绫华': (moegoe_gs, 23),
	'戴因斯雷布': (moegoe_gs, 24),
	'雷泽': (moegoe_gs, 25),
	'神里绫人': (moegoe_gs, 26),
	'罗莎莉亚': (moegoe_gs, 27),
	'阿贝多': (moegoe_gs, 28),
	'八重神子': (moegoe_gs, 29),
	'宵宫': (moegoe_gs, 30),
	'荒泷一斗': (moegoe_gs, 31),
	'九条裟罗': (moegoe_gs, 32),
	'夜兰': (moegoe_gs, 33),
	'珊瑚宫心海': (moegoe_gs, 34),
	'五郎': (moegoe_gs, 35),
	'散兵': (moegoe_gs, 36),
	'女士': (moegoe_gs, 37),
	'达达利亚': (moegoe_gs, 38),
	'莫娜': (moegoe_gs, 39),
	'班尼特': (moegoe_gs, 40),
	'申鹤': (moegoe_gs, 41),
	'行秋': (moegoe_gs, 42),
	'烟绯': (moegoe_gs, 43),
	'久岐忍': (moegoe_gs, 44),
	'辛焱': (moegoe_gs, 45),
	'砂糖': (moegoe_gs, 46),
	'胡桃': (moegoe_gs, 47),
	'重云': (moegoe_gs, 48),
	'菲谢尔': (moegoe_gs, 49),
	'诺艾尔': (moegoe_gs, 50),
	'迪奥娜': (moegoe_gs, 51),
	'鹿野院平藏': (moegoe_gs, 52),
	'宁宁': (moegoe_jp, 0),
	'爱瑠': (moegoe_jp, 1),
	'芳乃': (moegoe_jp, 2),
	'茉子': (moegoe_jp, 3),
	'丛雨': (moegoe_jp, 4),
	'小春': (moegoe_jp, 5),
	'七海': (moegoe_jp, 6),
	'Sua': (moegoe_kr, 0),
	'Mimiru': (moegoe_kr, 1),
	'Arin': (moegoe_kr, 2),
	'Yeonhwa': (moegoe_kr, 3),
	'Yuhwa': (moegoe_kr, 4),
	'Seonbae': (moegoe_kr, 5),
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
	(func, id) = speaker_map[speaker]
	text = ev.message.extract_plain_text().strip().lstrip(ev['prefix'])
	try:
		data = await func(id=id, text=text)
	except Exception as e:
		sv.logger.error({'speaker': speaker, 'id': id, 'text': text})
		sv.logger.error(e)
		await bot.send(ev, '获取语音失败', at_sender=True)
	else:
		async with aiofiles.tempfile.NamedTemporaryFile('wb', delete=True) as f:
			sv.logger.debug(f"save to: {f.name}")
			await f.write(data)
			os.chmod(f.name, 0o644)
			msg = nonebot.message.MessageSegment.record(f"file:///{f.name}")
			await bot.send(ev, msg, at_sender=False)
