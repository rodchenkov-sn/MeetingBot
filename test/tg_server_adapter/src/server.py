from dataclasses import dataclass
import threading
import flask

from werkzeug.serving import make_server
from queue import Queue
from random import randint

TOKEN = 'token'
messages_queue = Queue()


@dataclass
class Response:
    user_id: int
    text: str


responses_queue = Queue()

class ServerThread(threading.Thread):

    def __init__(self, app):
        threading.Thread.__init__(self)
        self.server = make_server('0.0.0.0', 9000, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()

def start_server():
    global server
    app = flask.Flask('myapp')

    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    @app.get(f'/bot:{TOKEN}/getUpdates')
    def get_updates():
        try:
            message = messages_queue.get(timeout=0.1)
        except:
            return flask.jsonify({'ok': True, 'result': []}), 200
        messages_queue.task_done()
        return flask.jsonify({
            'ok': True,
            'result': [
                {
                    'update_id': randint(1, 999999),
                    'message': message
                }
            ]
        }), 200
    
    @app.post(f'/bot:{TOKEN}/sendMessage')
    def send_message():
        chat_id = int(flask.request.args['chat_id'])
        text = flask.request.args['text']
        responses_queue.put(Response(chat_id, text))
        return flask.jsonify({
            'ok': True,
            'result': {
                'message_id': randint(1, 999999),
                'date': 1,
                'chat': {
                    'id': chat_id,
                    'type': 'private'
                },
            }
        }), 200

    server = ServerThread(app)
    server.start()

def stop_server():
    global server
    server.shutdown()


class Client:
    def __init__(self, username: str, id: int):
        self.username = username
        self.id = id
        self.send_message("/start")
        responses_queue.get(timeout=10)

    def send_message(self, message: str):
        messages_queue.put({
            'message_id': randint(1, 999999),
            'date': 1,
            'chat': {
                'id': self.id,
                'type': 'private'
            },
            'from': {
                'username': self.username,
                'is_bot': False,
                'first_name': 'Rei',
                'id': self.id
            },
            'text': message
        })
