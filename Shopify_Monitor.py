from Shopify_Class import  kith_apparel, kith, shoe_palace, bape
import asyncio



async def tasks():
 task1 = asyncio.create_task(kith_apparel.availability_check())
 task2 = asyncio.create_task(kith.availability_check())
 task3 = asyncio.create_task((shoe_palace.availability_check()))
 task4 = asyncio.create_task((bape.availability_check()))
 await task1
 await task2
 await task3


# # asyncio.run(tasks())

loop = asyncio.get_event_loop()
while True:
	loop.run_until_complete(tasks())


	
