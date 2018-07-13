import time
import asyncio
now = lambda:time.time()


async def do_some_work(x):
    print("Waiting:", x)
    await asyncio.sleep(2)
    return  "Done after {0}s{0}".format(x)


async def do_other_work(xx):
    print("other work")
    await asyncio.sleep(1)
    return "Done other work {0}".format(xx)

def callback(future):
    print("Callback:", future.result())

async def main():
    start = now()
    
    work_list = [
        do_some_work(2), 
        do_some_work(4), 
        do_some_work(7), 
        do_other_work(88),
        ]
    tasks = []
    for t in work_list:
        task = asyncio.ensure_future(t)
        task.add_done_callback(callback)
        tasks.append(task)

    tasks, done =  await asyncio.wait(tasks)
    for t in tasks:
        print (t)
    print('Time: ', now()-start)

loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.ensure_future(main()))


