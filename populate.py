from faker import Faker

import random

faker_generate = Faker()

from random import randint

import json

project_id = "flizon"

item = ['shirt','pant','shoe','sandals','TV','AC','watch']

origin_id_list = ['abcd', 'efgh', 'ijkl', 'mnop']

url_names = ['/flizon/','/flizon/view_item_list','/flizon/view_item','/flizon/cart','/flizon/wish_list']

event_names = [['login','signup','offers'], ['view_item'], ['add_to_cart', 'add_to_wishlist','purchase'], ['remove_from_cart','add_to_wishlist', 'purchase', 'view_item'], ['remove_from_wishlist', 'add_to_cart', 'purchase', 'view_item']]

login = {}
signup = {}
offers = {}

view_item = {"items":random.choice(item)}

add_to_cart = {"value":random.randrange(100,100000,98),"currency":faker_generate.currency_code(),"items":random.choice(item)}

add_to_wishlist = {"value":random.randrange(100,100000,98),"currency":faker_generate.currency_code(),"items":random.choice(item)}

purchase = {"transaction_id": randint(1,100),"value":random.randrange(100,100000,98),"currency":faker_generate.currency_code(),"items":random.choice(item)}

remove_from_cart = {"value":random.randrange(100,100000,98),"currency":faker_generate.currency_code(),"items":random.choice(item)}

remove_from_wishlist = {"value":random.randrange(100,100000,98),"currency":faker_generate.currency_code(),"items":random.choice(item)}

custom_dict = {'login': login, 'signup': signup, 'offers': offers, 'view_item': view_item, 'add_to_cart': add_to_cart, 'add_to_wishlist': add_to_wishlist, 'remove_from_cart': remove_from_cart, 'remove_from_wishlist': remove_from_wishlist, 'purchase': purchase}

def populate():

	for origin_id in origin_id_list:
		user_agent = faker_generate.user_agent()

		for i in range(random.randrange(50,70,8)):
			page_url = random.choice(url_names)

			event_index = url_names.index(page_url)

			event_in_url = event_names[event_index]

			event_type = random.choice(event_in_url)

			custom_event_type = custom_dict[event_type]

			custom_data = json.dumps(custom_event_type)
	
			print("INSERT INTO `web_event`(`project_id`,`origin_id`,`user_agent`,`page_url`,`event_type`,`custom_data`) Values", (project_id, origin_id, user_agent, page_url, event_type, custom_data))

if __name__ == '__main__':
	print("populate script")
	populate()
