#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Dict, Union, NoReturn

import os
import nonebot
import asyncio
import aiohttp
import aiofiles
import base64
import random

import hoshino

MAX_RETRY_COUNT = 300
RETRY_INTERVAL = 1
MAX_WAIT_TIME = 420

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

async def moegoe_HamidashiCreative(id: int, text: str) -> bytes:
	params = {
		'id':     id,
		'text':   text,
	}
	async with aiohttp.ClientSession(raise_for_status=True) as session:
		async with session.get('https://moegoe.azurewebsites.net/api/speak2', params=params) as resp:
			return await resp.read()

async def moegoe_DRACURIOT(id: int, text: str) -> bytes:
	params = {
		'id':     id,
		'text':   text,
	}
	async with aiohttp.ClientSession(raise_for_status=True) as session:
		async with session.get('https://moegoe.azurewebsites.net/api/speak3', params=params) as resp:
			return await resp.read()

async def moegoe_kr(id: int, text: str) -> bytes:
	params = {
		'id':     id,
		'text':   text,
	}
	async with aiohttp.ClientSession(raise_for_status=True) as session:
		async with session.get('https://moegoe.azurewebsites.net/api/speakkr', params=params) as resp:
			return await resp.read()

def huggingface_hash() -> str:
	return ''.join((random.choices('0123456789abcdefghijklmnopqrstuvwxyz', k=11)))

async def huggingface_push(namespace: str, fn_index: int, data: Union[List, Dict]) -> Dict:
	async with aiohttp.ClientSession(raise_for_status=True) as session:
		data = {
			'action': 'predict',
			'fn_index': fn_index,
			'data': data,
			'session_hash': '',
		}
		async with session.post(f"https://hf.space/embed/{namespace}/api/queue/push/", json=data) as resp:
			ret = await resp.json()
		# queue_position = ret['queue_position']
		data = {
			'hash': ret['hash'],
		}
		for _ in range(MAX_RETRY_COUNT):
			await asyncio.sleep(RETRY_INTERVAL)
			async with session.post(f"https://hf.space/embed/{namespace}/api/queue/status/", json=data) as resp:
				ret = await resp.json()
			if ret['status'] == 'PENDING':
				continue
			elif ret['status'] == 'COMPLETE':
				return ret['data']
			else:
				raise ValueError(f"Unknow status {ret}")
		raise asyncio.TimeoutError(f"Maximum retry count {MAX_RETRY_COUNT} reached")

async def huggingface_join(namespace: str, fn_index: int, data: Union[List, Dict]) -> Dict:
	async with aiohttp.ClientSession(raise_for_status=True) as session:
		async with session.ws_connect(f"wss://spaces.huggingface.tech/{namespace}/queue/join") as ws:
			session_hash = huggingface_hash()
			ret = await ws.receive_json()
			if ret['msg'] != 'send_hash':
				raise ValueError(f"Unknow msg {ret}")
			await ws.send_json({
				'fn_index': fn_index,
				'session_hash': session_hash,
			})
			while not ws.closed:
				ret = await ws.receive_json()
				if ret['msg'] == 'estimation':
					if ret['queue_eta'] != 0:
						await asyncio.sleep(int(ret['queue_eta']))
				elif ret['msg'] == 'send_data':
					await ws.send_json({
						'fn_index': fn_index,
						'data': data,
						'session_hash': session_hash,
					})
				elif ret['msg'] == 'process_starts':
					pass
				elif ret['msg'] == 'process_completed':
					if not ret['success']:
						raise RuntimeWarning(f"huggingface failed: {ret}")
					return ret['output']
				else:
					raise ValueError(f"Unknow msg {ret}")

async def huggingface_nyaru_basic(text: str) -> bytes:
	data = await huggingface_push(namespace='innnky/vits-nyaru', fn_index=0, data=[text])
	assert data['data'][0] == 'Success'
	return base64.b64decode(data['data'][1][22:].encode('utf-8'))

async def huggingface_nyaru_advanced(text: str) -> bytes:
	data = await huggingface_push(namespace='innnky/vits-nyaru', fn_index=1, data=[text])
	data = await huggingface_push(namespace='innnky/vits-nyaru', fn_index=2, data=[data['data'][0]])
	assert data['data'][0] == 'Success'
	return base64.b64decode(data['data'][1][22:].encode('utf-8'))

async def huggingface_moe_tts(fn_index: int, character: str, text: str, speed: int=1) -> bytes:
	data = await huggingface_join(namespace='skytnt/moe-tts', fn_index=fn_index, data=[text, character, speed, False])
	assert data['data'][0] == 'Success'
	return base64.b64decode(data['data'][1][22:].encode('utf-8'))

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

	'綾地寧々': {'func': moegoe_jp, 'kwargs': {'id': 0}},
	'因幡めぐる': {'func': moegoe_jp, 'kwargs': {'id': 1}},
	'朝武芳乃': {'func': moegoe_jp, 'kwargs': {'id': 2}},
	'常陸茉子': {'func': moegoe_jp, 'kwargs': {'id': 3}},
	'ムラサメ': {'func': moegoe_jp, 'kwargs': {'id': 4}},
	'鞍馬小春': {'func': moegoe_jp, 'kwargs': {'id': 5}},
	'在原七海': {'func': moegoe_jp, 'kwargs': {'id': 6}},

	'和泉妃愛': {'func': moegoe_HamidashiCreative, 'kwargs': {'id': 0}},
	'常盤華乃': {'func': moegoe_HamidashiCreative, 'kwargs': {'id': 1}},
	'錦あすみ': {'func': moegoe_HamidashiCreative, 'kwargs': {'id': 2}},
	'鎌倉詩桜': {'func': moegoe_HamidashiCreative, 'kwargs': {'id': 3}},
	'竜閑天梨': {'func': moegoe_HamidashiCreative, 'kwargs': {'id': 4}},
	'和泉里': {'func': moegoe_HamidashiCreative, 'kwargs': {'id': 5}},
	'新川広夢': {'func': moegoe_HamidashiCreative, 'kwargs': {'id': 6}},
	'聖莉々子': {'func': moegoe_HamidashiCreative, 'kwargs': {'id': 7}},

	'矢来美羽': {'func': moegoe_DRACURIOT, 'kwargs': {'id': 0}},
	'布良梓': {'func': moegoe_DRACURIOT, 'kwargs': {'id': 1}},
	'エリナ': {'func': moegoe_DRACURIOT, 'kwargs': {'id': 2}},
	'稲叢莉音': {'func': moegoe_DRACURIOT, 'kwargs': {'id': 3}},
	'ニコラ': {'func': moegoe_DRACURIOT, 'kwargs': {'id': 4}},
	'荒神小夜': {'func': moegoe_DRACURIOT, 'kwargs': {'id': 5}},
	'大房ひよ里': {'func': moegoe_DRACURIOT, 'kwargs': {'id': 6}},
	'淡路萌香': {'func': moegoe_DRACURIOT, 'kwargs': {'id': 7}},
	'アンナ': {'func': moegoe_DRACURIOT, 'kwargs': {'id': 8}},
	'倉端直太': {'func': moegoe_DRACURIOT, 'kwargs': {'id': 9}},
	'枡形兵馬': {'func': moegoe_DRACURIOT, 'kwargs': {'id': 10}},
	'扇元樹': {'func': moegoe_DRACURIOT, 'kwargs': {'id': 11}},

	'수아': {'func': moegoe_kr, 'kwargs': {'id': 0}},
	'미미르': {'func': moegoe_kr, 'kwargs': {'id': 1}},
	'아린': {'func': moegoe_kr, 'kwargs': {'id': 2}},
	'연화': {'func': moegoe_kr, 'kwargs': {'id': 3}},
	'유화': {'func': moegoe_kr, 'kwargs': {'id': 4}},
	'선배': {'func': moegoe_kr, 'kwargs': {'id': 5}},

	'猫雷にゃる': {'func': huggingface_nyaru_advanced, 'kwargs': {}},

	# '綾地寧々': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 1, 'character': '綾地寧々'}},
	# '因幡めぐる': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 1, 'character': '因幡めぐる'}},
	# '朝武芳乃': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 1, 'character': '朝武芳乃'}},
	# '常陸茉子': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 1, 'character': '常陸茉子'}},
	# 'ムラサメ': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 1, 'character': 'ムラサメ'}},
	# '鞍馬小春': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 1, 'character': '鞍馬小春'}},
	# '在原七海': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 1, 'character': '在原七海'}},

	# '和泉妃愛': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 5, 'character': '和泉妃愛'}},
	# '常盤華乃': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 5, 'character': '常盤華乃'}},
	# '錦あすみ': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 5, 'character': '錦あすみ'}},
	# '鎌倉詩桜': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 5, 'character': '鎌倉詩桜'}},
	# '竜閑天梨': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 5, 'character': '竜閑天梨'}},
	# '和泉里': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 5, 'character': '和泉里'}},
	# '新川広夢': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 5, 'character': '新川広夢'}},
	# '聖莉々子': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 5, 'character': '聖莉々子'}},

	'四季ナツメ': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 9, 'character': '四季ナツメ'}},
	'明月栞那': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 9, 'character': '明月栞那'}},
	'墨染希': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 9, 'character': '墨染希'}},
	'火打谷愛衣': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 9, 'character': '火打谷愛衣'}},
	'汐山涼音': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 9, 'character': '汐山涼音'}},

	'春日野穹': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 13, 'character': '春日野穹'}},
	'天女目瑛': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 13, 'character': '天女目瑛'}},
	'依媛奈緒': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 13, 'character': '依媛奈緒'}},
	'渚一葉': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 13, 'character': '渚一葉'}},

	'蓮華': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 17, 'character': '蓮華'}},
	'篝ノ霧枝': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 17, 'character': '篝ノ霧枝'}},
	'沢渡雫': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 17, 'character': '沢渡雫'}},
	'亜璃子': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 17, 'character': '亜璃子'}},
	'灯露椎': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 17, 'character': '灯露椎'}},
	'覡夕莉': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 17, 'character': '覡夕莉'}},

	'鷹倉杏璃': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 29, 'character': '鷹倉杏璃'}},
	'鷹倉杏鈴': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 29, 'character': '鷹倉杏鈴'}},
	'アペイリア': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 29, 'character': 'アペイリア'}},
	'倉科明日香': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 29, 'character': '倉科明日香'}},
	'ATRI': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 29, 'character': 'ATRI'}},
	'アイラ': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 29, 'character': 'アイラ'}},
	'新堂彩音': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 29, 'character': '新堂彩音'}},
	'姫野星奏': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 29, 'character': '姫野星奏'}},
	'小鞠ゆい': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 29, 'character': '小鞠ゆい'}},
	'聖代橋氷織': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 29, 'character': '聖代橋氷織'}},
	'有坂真白': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 29, 'character': '有坂真白'}},
	'白咲美絵瑠': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 29, 'character': '白咲美絵瑠'}},
	'二階堂真紅': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 29, 'character': '二階堂真紅'}},

	'上海人': {'func': huggingface_moe_tts, 'kwargs': {'fn_index': 53, 'character': '上海话'}},
}

def add_map_alias(smap: Dict) -> NoReturn:
	smap.update({
		'宁宁': smap['綾地寧々'],
		'爱瑠': smap['因幡めぐる'],
		'芳乃': smap['朝武芳乃'],
		'茉子': smap['常陸茉子'],
		'丛雨': smap['ムラサメ'],
		'小春': smap['鞍馬小春'],
		'七海': smap['在原七海'],

		'Sua': smap['수아'],
		'Mimiru': smap['미미르'],
		'Arin': smap['아린'],
		'Yeonhwa': smap['연화'],
		'Yuhwa': smap['유화'],
		'Seonbae': smap['선배'],

		'猫雷': smap['猫雷にゃる'],

		'穹妹': smap['春日野穹'],

		'莲华': smap['蓮華'],
		'雾枝': smap['篝ノ霧枝'],

		'星奏': smap['姫野星奏'],
	})

sv = hoshino.Service(
	'MoeGoe',
	visible=True,
	enable_on_default=True,
	help_='[让xxx说] 合成语音\n' + ','.join(speaker_map.keys())
)

add_map_alias(speaker_map)

@sv.on_prefix(*map(lambda x: f"让{x}说", speaker_map.keys()))
async def speak(bot, ev: nonebot.message.CQEvent) -> NoReturn:
	speaker = ev['prefix'].lstrip('让').rstrip('说')
	caller = speaker_map[speaker]
	text = ev.message.extract_plain_text().strip().lstrip(ev['prefix']).lstrip('\ufeff')
	try:
		data = await asyncio.wait_for(
			caller['func'](**caller['kwargs'], text=text),
			timeout=MAX_WAIT_TIME,
		)
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
