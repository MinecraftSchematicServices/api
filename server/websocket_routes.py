import asyncio
from multiprocessing import Queue

queue = Queue()

def show_queue():
    push_back = []
    print("Queue:")
    while not queue.empty():
        value = queue.get()
        print(f"  {value}")
        push_back.append(value)
    for value in push_back:
        queue.put(value)

async def feed(request, ws):
    while True:
        if not queue.empty():
            # show_queue()
            await ws.send(queue.get())
        await asyncio.sleep(0.2)
