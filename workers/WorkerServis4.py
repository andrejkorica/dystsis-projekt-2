from aiohttp import web
import re
import asyncio
import string
import random

routes = web.RouteTableDef()

@routes.get("/")
async def function(request):
	try:
		random_request_wait_time = random.uniform(0.1, 0.5)
		await asyncio.sleep(random_request_wait_time)

		data = await request.json()
		words = re.sub(f"[{string.punctuation}]", "", data.get("data")).split()
		word_count = len(words)

		random_response_wait_time = random.uniform(0.1, 0.5)
		await asyncio.sleep(random_response_wait_time)

		return web.json_response({"status": "OK", "numberOfWords": word_count}, status = 200)
	except Exception as e:
		return web.json_response({"error": str(e)}, status = 500)

app = web.Application()

app.router.add_routes(routes)

web.run_app(app, port = 8084)
