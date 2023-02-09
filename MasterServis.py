from aiohttp import web
import random
import asyncio
import aiohttp
import logging

logging.basicConfig(level = logging.INFO, format = '%(asctime)s - %(message)s', datefmt = '%Y-%m-%d %H:%M:%S')

M = 1000								
N = random.randint(5, 10)
reqGot = 0	
resGot = 0	
sentTasks = 0			
tasks_done = 0		

print("There are", N, "workers:")

workers = {"worker" + str(id): [] for id in range(1, N + 1)}
for key, value in workers.items():
    print(f"{key}")

routes = web.RouteTableDef()

@routes.get("/")
async def function(request):
	try:
		global N, workers, M, sentTasks, tasks_done, reqGot, resGot

		reqGot += 1
		logging.info(f"Recived: {reqGot} / 10000 requests")
	
		data = await request.json()
		codesLength = len(data.get("codes"))
		allCodes = '\n'.join(data.get("codes"))
		codes = allCodes.split("\n")
		new_codes = []
		for i in range(0, len(codes), M):
			new_codes.append("\n".join(codes[i:i+M]))
		data["codes"] = new_codes

		tasks = []
		results = []
		
		async with aiohttp.ClientSession() as session:
			currentWorker = 1
			for code in data.get("codes"):
				task = asyncio.create_task(
					session.get(f"http://127.0.0.1:{8080 + currentWorker}/", json={ "id": data.get("client"), "data": code })
				)
				sentTasks += 1
				logging.info(f"task sent to {currentWorker} worker... There are {sentTasks} currently sent tasks.") 
				tasks.append(task)
				workers["worker" + str(currentWorker)].append(task)
				currentWorker = 1 if currentWorker == N else currentWorker + 1

			
			results = await asyncio.gather(*tasks)
			tasks_done += len(results)
			logging.info(f"{len(results)} tasks are done... there are {tasks_done} complated tasks.") 
			results = [await result.json() for result in results]
			results = [result.get("numberOfWords") for result in results]

		resGot += 1
		logging.info(f"A new response has been sent. theres {resGot} responses sent")
		
		return web.json_response({"status": "OK", "client": data.get("client"), "averageWordcount": round(sum(results) / codesLength, 2)}, status = 200)
	except Exception as e:
		return web.json_response({"error": str(e)}, status = 500)

app = web.Application()

app.router.add_routes(routes)

web.run_app(app, port = 8080, access_log = None)
