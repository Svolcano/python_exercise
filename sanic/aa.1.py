import asyncio
import time

async def do_some(x):
    print(x)
    await time.sleep(1)

loop = asyncio.get_event_loop()
loop.run_until_complete(do_some(3))