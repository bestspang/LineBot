from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, request, abort, send_from_directory, jsonify, render_template
import json, requests, random, os, errno, sys, tempfile
import dialogflow, gspread, pprint
from html.parser import HTMLParser
from urllib.request import urlopen as uReq
from urllib.request import urlretrieve as uRet
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (LineBotApiError, InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton,
    ImageSendMessage)


urls = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRFS69FbmZBwkmCWtGWwDrA7YJyEpAmMyLHZ07FACjet8gxVX5WZ0DtVy2yW644QkY4d8UGctjfej0s/pubchart?oid=1508988021&format=image"
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('BPLINEBOT-57c70064e9b9.json', scope)
client = gspread.authorize(creds)
uRet(urls, "image.png")
sheet = client.open('AbbokIncomeAssesmentV02').worksheet("Summary2")
pp = pprint.PrettyPrinter()
expense = sheet.cell(3, 14).value
income = sheet.cell(2, 14).value

#pp.pprint(balance)
price = "รายจ่ายทั้งหมด {} บาท \n รายรับทั้งหมด {} บาท".format(expense, income)
print(price)
#url = request.url_root + '/image.png'
#app.logger.info("url=" + url)
# line_bot_api.reply_message(
#     event.reply_token,
#     #ImageSendMessage(url, url),
#     TextSendMessage(text=price)
# )
