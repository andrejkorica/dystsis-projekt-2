import asyncio
import pandas as pd
import aiohttp

listOfClientIDs = list(range(1, 10001))

dataset = pd.read_json("fakeDataset.json", lines = True)
print("Loaded dataset!\n")

rowsPerClient = int(len(dataset) / len(listOfClientIDs)) 

clients = {}
for id in listOfClientIDs:
	clients[id] = []

for id, codes in clients.items():
    start_index = (id - 1) * rowsPerClient
    end_index = start_index + rowsPerClient
    target_rows = dataset.iloc[start_index : end_index]
    for _, row in target_rows.iterrows():
        codes.append(row["content"])
		
tasks = []
results = []

async def processCode():
    global tasks, results
    async with aiohttp.ClientSession(connector = aiohttp.TCPConnector(ssl = False)) as session:
        for id, codes in clients.items():
            task = asyncio.create_task(session.get("http://127.0.0.1:8080/", json = { "client": id, "codes": codes }))
            tasks.append(task)
        print("Data sent.\n")
        results = await asyncio.gather(*tasks)
        results = [await x.json() for x in results]


event_loop = asyncio.new_event_loop()
asyncio.set_event_loop(event_loop)
event_loop.run_until_complete(processCode())

for result in results:
	print("client ID:", result.get("client"), " Avarage code length:", result.get("averageWordcount"))