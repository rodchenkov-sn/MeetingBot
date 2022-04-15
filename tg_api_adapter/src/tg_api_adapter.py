from typing import Match
import grpc
import telebot
import yaml
import redis
import re
import os

from datetime import datetime
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler

import user_message_pb2_grpc as ums
import user_message_pb2 as um


if os.environ['AdapterSysTestEnv'] is None:
    with open('config.yml', 'r') as config_file:
        config = yaml.safe_load(config_file)
    token = config['tg_token']
else:
    from telebot import apihelper
    apihelper.API_URL = 'http://tg-test-service:9000/bot:{0}/{1}'
    token = 'token'


bot = telebot.TeleBot(token)


channel = grpc.insecure_channel('frontend-service:50051')
stub = ums.UserMessageHandlerStub(channel)

jobstores = {
    'default': RedisJobStore(jobs_key='dispatched_trips_jobs', run_times_key='dispatched_trips_running', host='redis-service', port=6379)
}
executors = {
    'default': ThreadPoolExecutor(100),
    'processpool': ProcessPoolExecutor(5)
}
scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors)
scheduler.start()

username_id_redis = redis.Redis(host='redis-service', port=6379, db=1)
id_username_redis = redis.Redis(host='redis-service', port=6379, db=2)

assert(username_id_redis.ping())
assert(id_username_redis.ping())


def sendMessage(id: int, text: str):
    if text == '':
        bot.send_message(id, '...')
    bot.send_message(id, text)


def mentions_to_ids(text: str) -> str:
    if text is None:
        return ''
    def m_to_i(s: Match[str]) -> str:
        id = username_id_redis.get(s.group())
        if id is None:
            return '!!ERR!!'
        else:
            return f'[[{id.decode("utf-8")}]]'
    return re.sub(r'@[A-Za-z0-9_-]+', m_to_i, text)


def ids_to_mentions(text: str) -> str:
    if text is None:
        return ''
    def i_to_m(id: Match[str]) -> str:
        id_s = id.group()
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
        user_message.file_name = message.document.file_name
        user_message.file_url = bot.get_file_url(message.document.file_id)
    responses = stub.HandleMessage(user_message)
    for response in responses:
        if response.timestamp != 0 and response.event_id != 0:
            print(response.timestamp, response.event_id)
            job_id = f'{response.user_id}:{response.event_id}'
            if scheduler.get_job(job_id):
                scheduler.remove_job(job_id)
            scheduler.add_job(
                sendMessage, 
                'date', 
                args=[response.user_id, ids_to_mentions(response.text)], 
                run_date=datetime.fromtimestamp(response.timestamp),
                timezone='Europe/Moscow')
        else:
            sendMessage(response.user_id, ids_to_mentions(response.text))


def run():
    bot.infinity_polling()

