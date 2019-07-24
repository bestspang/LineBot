import gevent.monkey
gevent.monkey.patch_all()
from gevent.pywsgi import WSGIServer
from flask_socketio import SocketIO, emit
from flask import Flask, request, abort, send_from_directory, jsonify,render_template, url_for, copy_current_request_context, Response
from oauth2client.service_account import ServiceAccountCredentials
import os, errno, configparser
import dialogflow, gspread, pprint, datetime, functools, time #tempfile
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (LineBotApiError, InvalidSignatureError)
from linebot.models import *
from threading import Thread, Event
from apscheduler.schedulers.background import BlockingScheduler
from models.Member import Member
from models.Tools import Vote, Tools, RandomThread, Hoon
from models.Text import Text

__author__ = 'bestspang'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!!!'
app.config['DEBUG'] = False

#turn the flask app into a socketio app
socketio = SocketIO(app)
#random number Generator Thread
thread = Thread()
thread_stop_event = Event()

config = configparser.ConfigParser()
config.read("config.ini")
#info = [NICKNAME,FIRST_NAME,FN_TH,LAST_NAME,LN_TH,E_MAIL,PERSONAL_ID,DOB,ADDR,MOBILE_NO,BANK_S,BANK_NO,BRANCHES]
line_bot_api = LineBotApi(config['line_bot']['line_bot_api'])
handler = WebhookHandler(config['line_bot']['handler'])
#profile = line_bot_api.get_group_member_profile(group_id, user_id)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('static/key/bplinebot-3ccea59ad6d6.json', scope)
client = gspread.authorize(creds)

sched = BlockingScheduler({'apscheduler.timezone': 'Asia/Bangkok'})

mem = Member(line_bot_api)
text = Text(line_bot_api)
tools = Tools()
hoon = Hoon()
#vote = Vote()

def make_static_tmp_dir():
    try:
        os.makedirs(static_tmp_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(static_tmp_path):
            pass
        else:
            raise

#@sched.scheduled_job('interval', seconds=5)
@sched.scheduled_job('cron', day_of_week='mon-fri', hour=9, minute=30)
def print_date_time():
    # global date_time
    # date_time += datetime.timedelta(days=1)
    #to = "U7612d77bbca83f04d6acf5e27333edeb" #best
    to = "C374667ff440b48857dafb57606ff4600" #group
    to_mem = ["U7612d77bbca83f04d6acf5e27333edeb", "U262184d96cc22dfb837493e3ff6ca85a",
            "U03fe1d43c072db5c3dde2f2a20fddcb9", "Ub4cd6bb2dc9548dd416a35e5b7488c09",
            "Uc1f00d375dd0d706511f4957e4ccc491"]
    line_bot_api.push_message(to, TextSendMessage(text=tools.getQuote()))
    for i in to_mem:
        line_bot_api.push_message(i, TextSendMessage(text="ทำงานอย่าลืม check-in นะครับผม!"))

sched.start()

@app.route("/")
def hello():
    #return "This is BP_LINEBOT2 (Mr.Doge)!"
    return render_template('index.html')

@app.route("/notify")
def call_func():
    mem.is_approve_new_member()
    return render_template('index.html')

@socketio.on('connect', namespace='/test')
def test_connect():
    # need visibility of the global thread object
    global thread
    global socketio
    print('Client connected')

    #Start the random number generator thread only if the thread has not been started before.
    if not thread.isAlive():
        print("Starting Thread")
        thread = RandomThread(socketio=socketio,thread_stop_event=thread_stop_event)
        thread.start()

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')

@app.route("/bot", methods=['POST'])
def bot():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@app.route('/static/<path:path>')
def send_static_content(path):
    return send_from_directory('static', path)

@app.route('/images/<path:path>')
def send_images_content(path):
    return send_from_directory('images', path)

@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.form['message']
    project_id = config['DIALOGFLOW_PROJECT_ID']['id']
    fulfillment_text = Text.detect_intent_texts(project_id, "unique", message, 'th')
    response_text = { "message":  fulfillment_text }
    return jsonify(response_text)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text.message_handler(event)


@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        LocationSendMessage(
            title=event.message.title, address=event.message.address,
            latitude=event.message.latitude, longitude=event.message.longitude
        )
    )


@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        StickerSendMessage(
            package_id=event.message.package_id,
            sticker_id=event.message.sticker_id)
    )


# Other Message Type
@handler.add(MessageEvent, message=(ImageMessage, VideoMessage, AudioMessage))
def handle_content_message(event):
    if isinstance(event.message, ImageMessage):
        ext = 'jpg'
    elif isinstance(event.message, VideoMessage):
        ext = 'mp4'
    elif isinstance(event.message, AudioMessage):
        ext = 'm4a'
    else:
        return

    message_content = line_bot_api.get_message_content(event.message.id)
    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=ext + '-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        tempfile_path = tf.name

    dist_path = tempfile_path + '.' + ext
    dist_name = os.path.basename(dist_path)
    os.rename(tempfile_path, dist_path)

    line_bot_api.reply_message(
        event.reply_token, [
            TextSendMessage(text='Save content.'),
            TextSendMessage(text=request.host_url + os.path.join('static', 'tmp', dist_name))
        ])


@handler.add(MessageEvent, message=FileMessage)
def handle_file_message(event):
    message_content = line_bot_api.get_message_content(event.message.id)
    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix='file-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        tempfile_path = tf.name

    dist_path = tempfile_path + '-' + event.message.file_name
    dist_name = os.path.basename(dist_path)
    os.rename(tempfile_path, dist_path)

    line_bot_api.reply_message(
        event.reply_token, [
            TextSendMessage(text='Save file.'),
            TextSendMessage(text=request.host_url + os.path.join('static', 'tmp', dist_name))
        ])


@handler.add(FollowEvent)
def handle_follow(event):
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text='Got follow event'))


@handler.add(UnfollowEvent)
def handle_unfollow():
    app.logger.info("Got Unfollow event")


@handler.add(JoinEvent)
def handle_join(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='Joined this ' + event.source.type))


@handler.add(LeaveEvent)
def handle_leave():
    app.logger.info("Got leave event")


@handler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data == 'ping':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='pong'))
    elif event.postback.data == 'comingsoon':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='ระบบมาเร็วๆนี้ โฮ่งง'))
    elif event.postback.data == 'nothing':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='กดหาdad'))
    elif event.postback.data == 'datetime_postback':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.postback.params['datetime']))
    elif event.postback.data == 'date_postback':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.postback.params['date']))

    elif event.postback.data == 'yes':
        txt = 'ใจเย็นๆโฮ่ง!\nส่งข้อมูลไปแล้วจ้า!'
        if not mem.is_member(event.source.user_id):
            mem.add_member(event.source.user_id)
            txt = 'บันทึกสมาชิกเรียบร้อย!\nกรุณารอการยืนยัน!'
            line_bot_api.reply_message(
                event.reply_token, [TextSendMessage(text=txt),
                TextSendMessage(text='รบกวนกรอกข้อมูลของท่านตามลิงค์ด้านล่าง\nhttps://forms.gle/gXGxjsELh9hWy9Wx9'),
                TextSendMessage(text='ขอบคุณครับ')
                ])
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=txt))
    elif event.postback.data == 'no':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='โอเคโฮ่งง!'))

    elif event.postback.data == 'member_yes':
        mem.approve_member(1)
        txt = 'ยืนยันสมาชิกเรียบร้อย!'
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=txt))
    elif event.postback.data == 'member_no':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='โอเคโฮ่งง!'))


@handler.add(BeaconEvent)
def handle_beacon(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(
            text='Got beacon event. hwid={}, device_message(hex string)={}'.format(
                event.beacon.hwid, event.beacon.dm)))


# @handler.add(MemberJoinedEvent)
# def handle_member_joined(event):
#     line_bot_api.reply_message(
#         event.reply_token,
#         TextSendMessage(
#             text='Got memberJoined event. event={}'.format(
#                 event)))
#
#
# @handler.add(MemberLeftEvent)
# def handle_member_left(event):
#     app.logger.info("Got memberLeft event")

if __name__ == "__main__":
    make_static_tmp_dir()
    socketio.run(app) # , log_output=False
    #app.run()
