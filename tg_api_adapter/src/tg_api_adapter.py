# docker run -d -p 6379:6379 redis

from typing import Match
import grpc
import telebot
import yaml
import redis
import re

from datetime import datetime
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler

import user_message_pb2_grpc as ums
import user_message_pb2 as um


with open('config.yml', 'r') as config_file:
    config = yaml.safe_load(config_file)


bot = telebot.TeleBot(config['tg_token'])
channel = grpc.insecure_channel(config['frontend_server_url'])
stub = ums.UserMessageHandlerStub(channel)

jobstores = {
    'default': RedisJobStore(jobs_key='dispatched_trips_jobs', run_times_key='dispatched_trips_running', host='localhost', port=6379)
}
executors = {
    'default': ThreadPoolExecutor(100),
    'processpool': ProcessPoolExecutor(5)
}
scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors)
scheduler.start()

username_id_redis = redis.Redis('localhost', 6379, 1)
id_username_redis = redis.Redis('localhost', 6379, 2)

assert(username_id_redis.ping())
assert(id_username_redis.ping())


def sendMessage(id: int, text: str):
    bot.send_message(id, text)


def mentions_to_ids(text: str) -> str:
    def m_to_i(s: Match[str]) -> str:
        id = username_id_redis.get(s.string)
        if id is None:
            return '!!ERR!!'
        else:
            return f'[[{id.decode("utf-8")}]]'
    return re.sub(r'@[A-Za-z0-9_-]+', m_to_i, text)


def ids_to_mentions(text: str) -> str:
    def i_to_m(id: Match[str]) -> str:
        id_s = id.string
        id_s = id_s[2:len(id_s)-2]
        un = id_username_redis.get(id_s)
        if un is None:
            return '!!ERR!!'
        else:
            return un.decode('utf-8')
    return re.sub(r'\[\[\d+\]\]', i_to_m, text)


@bot.message_handler(content_types=['text', 'document'])
def get_text_messages(message):
    if message.text == '/start':
        print(f'@{message.from_user.username}', message.from_user.id)
        username_id_redis.set(f'@{message.from_user.username}', f'{message.from_user.id}')
        id_username_redis.set(f'{message.from_user.id}', f'@{message.from_user.username}')
    user_message = um.UserMessage(user_id=message.from_user.id, text=mentions_to_ids(message.text))
    if message.content_type == 'document':
        user_message.document.file_name = message.document.file_name
        user_message.document.download_url = bot.get_file_url(message.document.file_id)
    responses = stub.HandleMessage(user_message)
    for response in responses:
        print(response)
        if response.timestamp != 0 and response.event_id != 0:
            print(response.timestamp, response.event_id)
            job_id = f'{response.user_id}:{response.event_id}'
            if scheduler.get_job(job_id):
                scheduler.remove_job(job_id)
            scheduler.add_job(
                sendMessage, 
                'date', 
                [response.user_id, ids_to_mentions(response.text)], 
                run_date=datetime.fromtimestamp(response.timestamp))
        else:
            sendMessage(response.user_id, ids_to_mentions(response.text))


def run():
    bot.polling(none_stop=True, interval=0)