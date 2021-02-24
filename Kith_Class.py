import requests
import json
from discord_webhook import DiscordWebhook as dw
from discord_webhook import DiscordEmbed as de
import aiohttp
import asyncio
import aiofiles
import sqlite3
import pprint as pr

class shopify():

	def __init__(self, site_link, filename, store_domain, webhook):
		#initialize some class args
		self.site_link = site_link
		self.webhook = webhook
		self.logo = 'https://cdn.discordapp.com/attachments/773974917170593802/809939354256146432/image0.png'
		self.store_domain = store_domain
		#partner webhooks
		self.ghost_webhook = 'https://discord.com/api/webhooks/811639019867865098/5Xlg1o432_bglBxydDtFznMUrJcdtV8Y' \
							 'cx3DAGNM6zjJ0wIapOq77bC2vvNUJyQKX2QL'
		#early link webhooks
		self.early_link_webhook = 'https://discord.com/api/webhooks/810328502838624267/1jrf058mAMcxXUYm9aJhRWsmq_rqwuqr' \
								  'PNAYw0nH1IhvG3vjLVxZjpWGDxIA4TSIvjt0'
		#keywords and text files filters our monitor search
		self.keywrds = []
		self.filename = filename
		#self.checked limits whether we post to the webhook based on if we checked for the item already
		#availability stores product stock info & self.oos stores out of stock product skus to check for restocks
		self.checked = []
		self.availability = []
		self.oos = []
		#product & product variants
		self.products = ''
		self.name = ''
		self.url = ''				
		self.price = ''
		self.in_stock = ''
		self.sku = ''
		self.product_id = ''
		self.size = ''
		self.img = ''
		#stock list
		#must append in stock to this list because if the last item of the variant is false it won't
		#post the in stock items of that variant to the webhook
		############################# DEFINE PRODUCTS #####################################


	

	async def product_keys(self, product_index_key):
		#when calling this function pass self.products + the list index & key as an argument
		#this function is for displaying the keys and values in the products dictionary
		for item in product_index_key:
			print(item)
			print('\n')

	
	

	async def product_url(self, product_key):
		#pass self.products + key
		#define url
		url = f'https://{self.store_domain}/products/' + product_key
		return url




	async def keywords(self):
		async with aiofiles.open(self.filename, 'r') as f:
			words = await f.readlines()
			for word in words:
				if word.rstrip('\n') not in self.keywrds:
					self.keywrds.append(word.rstrip('\n'))
			return self.keywrds

	
	

	async def post_webhook(self, title, url, price, stock, size, img):
		#create webhook
		lab_hook = dw(url=self.webhook)

		# ghost_hook = dw(url=self.ghost_webhook)
		#create embed
		embed = de(title=self.store_domain, description=f"[{title}]({url})")
		embed.set_thumbnail(url=img)
		embed.add_embed_field(name='Price\n', value=f'{price}\n', inline=False)
		embed.add_embed_field(name='In-Stock\n', value=f'{stock}\n', inline=False)
		embed.add_embed_field(name='Sizes\n', value=size, inline=False)
		embed.add_embed_field(name='Links\n', value=f'[link]({url})\n', inline=False)
		embed.set_footer(icon_url=self.logo, text="LabMonitor | Formula-X LLC")
				

		#add embed to webhooks
		lab_hook.add_embed(embed)
		# ghost_hook.add_embed(embed)

		#excute
		lab_hook.execute()
		# ghost_hook.execute()




	async def restocked(self, title, url, price, stock, size, img):
		#create webhook
		lab_hook = dw(url=self.webhook)
		# ghost_hook = dw(url=self.ghost_webhook)
		#create embed
		embed = de(title='Item Restocked!', description=f"[{title}]({url})")
		embed.set_thumbnail(url=img)
		embed.add_embed_field(name='Price\n', value=f'{price}\n', inline=False)
		embed.add_embed_field(name='In-Stock\n', value=f'{stock}\n', inline=False)
		embed.add_embed_field(name='Sizes\n', value=size, inline=False)
		embed.add_embed_field(name='Links\n', value=f'[link]({url})\n', inline=False)
		embed.set_footer(icon_url=self.logo, text="LabMonitor | Formula-X LLC")
				

		#add embed to webhooks
		lab_hook.add_embed(embed)
		# ghost_hook.add_embed(embed)

		#excute
		lab_hook.execute()
		# ghost_hook.execute()

	
	

	async def availability_check(self):
		async with aiohttp.ClientSession() as session:
			response = await session.get(self.site_link)
			products = await response.text()
			products = json.loads(products)
			self.products = products['products']
			# pr.pprint(products)

		#loop through products in json file
		for product in self.products:


			#get the image for the embed
			for image in product['images']:
				self.img = image['src']
				break

			#MAKE SIZES ONE STRING IN EMBED & GET ALL THE OTHER EMBED ATTRIBUTES
			# loop through variants of each product
			sizes = ''
			for variant in product['variants']:
				self.name = product['title']
				self.url = await self.product_url(product['handle'])				
				self.price = variant['price']
				self.in_stock = variant['available']
				self.sku = variant['sku']
				self.product_id = variant['product_id']
				#only add the in stock sizes below
				if self.in_stock == True:
					self.size = variant['title']
					sizes += f'|{self.size}| '
				#mark sku as oos so we can check against it for restocks
				elif self.in_stock == False:
					self.oos.append(self.sku)

				self.availability.append(self.in_stock)

			#remove product name from checked list if they are all out of stock to check for them again
			if True not in self.availability:
				if self.name in self.checked:
					self.checked.remove(self.name)
				
		#CHECK FOR IN STOCK ITEMS
		#loop through variants of each product
		# for variant in product['variants']:
			# self.in_stock = variant['available']
			#check to see if at least one variant in in stock so that we can post it
			#then reset self.availability so it doesn't spam
			if True in self.availability and self.name not in self.checked:
				self.availability = []
				self.in_stock = True

				for title in  await self.keywords():
					if title in self.name:
						# for title in self.product_names:
						# 	if title in name and title not in self.checked:
						await self.post_webhook(self.name, self.url, self.price, self.in_stock, sizes, self.img)
						self.checked.append(product['title'])
						await asyncio.sleep(1)
						# elif in_stock == False and name in self.product_names and variant in self.checked:
						# 	self.checked.remove(title)

			#check if current availability for said sku changed to in stock/True
			if self.name in self.checked:

				for variant in product['variants']:
					self.name = product['title']
					self.url = await self.product_url(product['handle'])				
					self.price = variant['price']
					self.in_stock = variant['available']
					self.sku = variant['sku']
					self.size = f"| {variant['title']} |"
					if self.sku in self.oos and self.in_stock == True:
						await self.restocked(self.name, self.url, self.price, self.in_stock, self.size, self.img)
						self.oos.remove(self.sku)




	



footwear = shopify('https://kith.com/products.json', 'kith.txt', 'kith.com',
'https://discord.com/api/webhooks/774780175841755178/usLjqKHxzAtd6QleitBDPAkAD1KJBG32u9BToZrCtSh6E5veURK-v_ObMcMzAP_888ho')

mens_apparel = shopify('https://kith.com/collections/mens-apparel/products.json', 'kith.txt', 'kith.com',
'https://discord.com/api/webhooks/774780175841755178/usLjqKHxzAtd6QleitBDPAkAD1KJBG32u9BToZrCtSh6E5veURK-v_ObMcMzAP_888ho')

palace = shopify('https://www.shoepalace.com/products.json', 'shoe_palace.txt', 'shoepalace.com',
'https://discord.com/api/webhooks/814008785403510824/tMAq-yBkZbXoFYga2_YRxbFXUny-sMxwpzzvDzo_wDtPyREF-UdKyTn_fzMQGfIaMHOP')


