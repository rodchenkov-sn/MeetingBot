import grpc
import telebot


import user_message_pb2_grpc as ums
import user_message_pb2 as um


bot = telebot.TeleBot('')
channel = grpc.insecure_channel('localhost:50051')
stub = ums.UserMessageHandlerStub(channel)


@bot.message_handler(content_types=['text', 'document'])
def get_text_messages(message):
    user_message = um.UserMessage(user_id=message.from_user.id, text=message.text)
    if message.content_type == 'document':
        user_message.document.file_name = message.document.file_name
        user_message.document.download_url = bot.get_file_url(message.document.file_id)
    responses = stub.HandleMessage(user_message)
    for response in responses:
        bot.send_message(response.user_id, response.text)


def run():
    bot.polling(none_stop=True, interval=0)
