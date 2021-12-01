import grpc
import telebot
import yaml

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


def sendMessage(id, text):
    bot.send_message(id, text)


@bot.message_handler(content_types=['text', 'document'])
def get_text_messages(message):
    user_message = um.UserMessage(user_id=message.from_user.id, text=message.text)
    if message.content_type == 'document':
        user_message.document.file_name = message.document.file_name
        user_message.document.download_url = bot.get_file_url(message.document.file_id)
    responses = stub.HandleMessage(user_message)
    for response in responses:
        if response.timestamp is not None and response.event_id is not None:
            job_id = f'{response.user_id}:{response.event_id}'
            if scheduler.get_job(job_id):
                scheduler.remove_job(job_id)
            scheduler.add_job(
                sendMessage, 
                'date', 
                [response.user_id, response.text], 
                run_date=datetime.fromtimestamp(response.timestamp))
        else:
            sendMessage(response.user_id, response.text)


def run():
    bot.polling(none_stop=True, interval=0)
