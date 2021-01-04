import datetime
import json
import random
from random import randint
import uuid
from faker import Faker
from user_agents import parse
from config import CLICKHOUSE_DATABASE
from clickhouse_driver import Client
import user_agents as ua

faker_generate = Faker()



random.seed(datetime.datetime.now().timestamp())


client = Client(host=CLICKHOUSE_DATABASE["HOST"],
                             user=CLICKHOUSE_DATABASE["USER"],
                             password=CLICKHOUSE_DATABASE["PASSWORD"],
                             database=CLICKHOUSE_DATABASE["DATABASE_NAME"],)
def get_custom_data_from_user_agent(user_agent):
    parsed_ua = ua.parse(user_agent)

    return {"OS": parsed_ua.os.family,
            "browser": parsed_ua.browser.family,
            "device": parsed_ua.device.family}

def add_new_event(session_id, project_id, origin_user_id, time_entered, user_agent, page_url, page_domain, page_params, event_type, referrer, campaign, custom_data):
    global client
    insert_sql = 'INSERT into web_events (session_id, project_id, origin_user_id, time_entered, user_agent, page_url, \
        page_domain, page_params, event_type,browser, os, device, referrer, utm_campaign, custom_data.key, custom_data.value) VALUES'

    user_agent_data = get_custom_data_from_user_agent(user_agent)

    inserted_rows = client.execute(insert_sql,
                                   [(session_id, project_id, origin_user_id, time_entered, user_agent,
                                     page_url, page_domain, page_params, event_type, user_agent_data[
                                         'browser'],
                                     user_agent_data['OS'], user_agent_data['device'], referrer,
                                       campaign, custom_data.keys(), [str(x) for x in custom_data.values()])])

    return inserted_rows

project_id = "flizon"

item = ['shirt','pant','shoe','sandals','TV','AC','watch']


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

    total_events = 0
    for origins in range(200):
        origin_id = faker_generate.name()
        user_agent = faker_generate.user_agent()
        time_entered = faker_generate.date_time_this_month()
        previous_url = ""
        session_id = str(uuid.uuid4())
        print("INSERT INTO `session` (`session_id`, `start_time`, `origin_id`, `project_id`, `start_page`, `end_page`) VALUES ", (session_id, time_entered.isoformat(), origin_id, project_id, '', '',), ";")
        for i in range(randint(1,15)):
            time_entered = time_entered + datetime.timedelta(0,randint(30,300))
            page_url = random.choice(url_names)
            event_index = url_names.index(page_url)
            event_in_url = event_names[event_index]
            event_type = random.choice(event_in_url)

            custom_event_type = custom_dict[event_type]
            custom_data = json.dumps(custom_event_type)
    
            if previous_url != page_url:
                pageview_custom_data = {}
                parsed_ua = parse(user_agent)
                pageview_custom_data["OS"] = parsed_ua.os.family
                pageview_custom_data["device"] = parsed_ua.device.family
                pageview_custom_data["browser"] = parsed_ua.browser.family
                pageview_custom_data = json.dumps(pageview_custom_data)
                print("INSERT INTO `web_event` (`session_id`,`user_agent`,`page_url`,`event_type`,`time_entered`, `custom_data`)"
                    " Values ", (session_id, user_agent, page_url, 'pageview', time_entered.isoformat(),pageview_custom_data),';')
                print(f"UPDATE `session` SET `end_page` = '{page_url}' WHERE (`session_id` = '{session_id}');")
                add_new_event(session_id,project_id,origin_id, time_entered, user_agent, page_url, page_url, '{}', 'pageview', 'google.com', '', json.loads(pageview_custom_data))
                time_entered = time_entered + datetime.timedelta(0,randint(30,60))
                total_events += 1

            print("INSERT INTO `web_event` (`session_id`,`user_agent`,`page_url`,`event_type`,`time_entered`,`custom_data`) Values ", (session_id, user_agent, page_url, event_type,  time_entered.isoformat(), custom_data), ';')
            add_new_event(session_id,project_id,origin_id, time_entered, user_agent, page_url, page_url, '{}', event_type, '', '', json.loads(custom_data))

            total_events += 1
            previous_url = page_url

if __name__ == '__main__':

    populate()
