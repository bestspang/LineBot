# from linebot.models import (MessageEvent, TextMessage, TextSendMessage, SourceUser, SourceGroup, SourceRoom,
#     TemplateSendMessage, ConfirmTemplate, MessageAction,
#     ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
#     PostbackAction, DatetimePickerAction,
#     CameraAction, CameraRollAction, LocationAction,
#     CarouselTemplate, CarouselColumn, PostbackEvent,
#     StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
#     ImageMessage, VideoMessage, AudioMessage, FileMessage,
#     UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
#     MemberJoinedEvent, MemberLeftEvent,
#     FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
#     TextComponent, SpacerComponent, IconComponent, ButtonComponent,
#     SeparatorComponent, QuickReply, QuickReplyButton,
#     ImageSendMessage)
#
#     if text == 'profile':
#         if isinstance(event.source, SourceUser):
#             profile = line_bot_api.get_profile(event.source.user_id)
#             line_bot_api.reply_message(
#                 event.reply_token, [
#                     TextSendMessage(text='Display name: ' + profile.display_name),
#                     TextSendMessage(text='Status message: ' + profile.status_message)
#                 ]
#             )
#         else:
#             line_bot_api.reply_message(
#                 event.reply_token,
#                 TextSendMessage(text="Bot can't use profile API without user ID"))
#     elif text == 'quota':
#         quota = line_bot_api.get_message_quota()
#         line_bot_api.reply_message(
#             event.reply_token, [
#                 TextSendMessage(text='type: ' + quota.type),
#                 TextSendMessage(text='value: ' + str(quota.value))
#             ]
#         )
#     elif text == 'quota_consumption':
#         quota_consumption = line_bot_api.get_message_quota_consumption()
#         line_bot_api.reply_message(
#             event.reply_token, [
#                 TextSendMessage(text='total usage: ' + str(quota_consumption.total_usage)),
#             ]
#         )
#     elif text == 'push':
#         line_bot_api.push_message(
#             event.source.user_id, [
#                 TextSendMessage(text='PUSH!'),
#             ]
#         )
#     elif text == 'multicast':
#         line_bot_api.multicast(
#             [event.source.user_id], [
#                 TextSendMessage(text='THIS IS A MULTICAST MESSAGE'),
#             ]
#         )
#     elif text == 'broadcast':
#         line_bot_api.broadcast(
#             [
#                 TextSendMessage(text='THIS IS A BROADCAST MESSAGE'),
#             ]
#         )
#     elif text.startswith('broadcast '):  # broadcast 20190505
#         date = text.split(' ')[1]
#         print("Getting broadcast result: " + date)
#         result = line_bot_api.get_message_delivery_broadcast(date)
#         line_bot_api.reply_message(
#             event.reply_token, [
#                 TextSendMessage(text='Number of sent broadcast messages: ' + date),
#                 TextSendMessage(text='status: ' + str(result.status)),
#                 TextSendMessage(text='success: ' + str(result.success)),
#             ]
#         )
#     elif text == 'bye':
#         if isinstance(event.source, SourceGroup):
#             line_bot_api.reply_message(
#                 event.reply_token, TextSendMessage(text='Leaving group'))
#             line_bot_api.leave_group(event.source.group_id)
#         elif isinstance(event.source, SourceRoom):
#             line_bot_api.reply_message(
#                 event.reply_token, TextSendMessage(text='Leaving group'))
#             line_bot_api.leave_room(event.source.room_id)
#         else:
#             line_bot_api.reply_message(
#                 event.reply_token,
#                 TextSendMessage(text="Bot can't leave from 1:1 chat"))
#     elif text == 'image':
#         url = request.url_root + '/static/logo.png'
#         app.logger.info("url=" + url)
#         line_bot_api.reply_message(
#             event.reply_token,
#             ImageSendMessage(url, url)
#         )
#     elif text == 'confirm':
#         confirm_template = ConfirmTemplate(text='Do it?', actions=[
#             MessageAction(label='Yes', text='Yes!'),
#             MessageAction(label='No', text='No!'),
#         ])
#         template_message = TemplateSendMessage(
#             alt_text='Confirm alt text', template=confirm_template)
#         line_bot_api.reply_message(event.reply_token, template_message)
#     elif text == 'buttons':
#         buttons_template = ButtonsTemplate(
#             title='My buttons sample', text='Hello, my buttons', actions=[
#                 URIAction(label='Go to line.me', uri='https://line.me'),
#                 PostbackAction(label='ping', data='ping'),
#                 PostbackAction(label='ping with text', data='ping', text='ping'),
#                 MessageAction(label='Translate Rice', text='米')
#             ])
#         template_message = TemplateSendMessage(
#             alt_text='Buttons alt text', template=buttons_template)
#         line_bot_api.reply_message(event.reply_token, template_message)
#     elif text == 'carousel':
#         carousel_template = CarouselTemplate(columns=[
#             CarouselColumn(text='hoge1', title='fuga1', actions=[
#                 URIAction(label='Go to line.me', uri='https://line.me'),
#                 PostbackAction(label='ping', data='ping')
#             ]),
#             CarouselColumn(text='hoge2', title='fuga2', actions=[
#                 PostbackAction(label='ping with text', data='ping', text='ping'),
#                 MessageAction(label='Translate Rice', text='米')
#             ]),
#         ])
#         template_message = TemplateSendMessage(
#             alt_text='Carousel alt text', template=carousel_template)
#         line_bot_api.reply_message(event.reply_token, template_message)
#     elif text == 'image_carousel':
#         image_carousel_template = ImageCarouselTemplate(columns=[
#             ImageCarouselColumn(image_url='https://via.placeholder.com/1024x1024',
#                                 action=DatetimePickerAction(label='datetime',
#                                                             data='datetime_postback',
#                                                             mode='datetime')),
#             ImageCarouselColumn(image_url='https://via.placeholder.com/1024x1024',
#                                 action=DatetimePickerAction(label='date',
#                                                             data='date_postback',
#                                                             mode='date'))
#         ])
#         template_message = TemplateSendMessage(
#             alt_text='ImageCarousel alt text', template=image_carousel_template)
#         line_bot_api.reply_message(event.reply_token, template_message)
#     elif text == 'imagemap':
#         pass
#     elif text == 'flex':
#         bubble = BubbleContainer(
#             direction='ltr',
#             hero=ImageComponent(
#                 url='https://example.com/cafe.jpg',
#                 size='full',
#                 aspect_ratio='20:13',
#                 aspect_mode='cover',
#                 action=URIAction(uri='http://example.com', label='label')
#             ),
#             body=BoxComponent(
#                 layout='vertical',
#                 contents=[
#                     # title
#                     TextComponent(text='Brown Cafe', weight='bold', size='xl'),
#                     # review
#                     BoxComponent(
#                         layout='baseline',
#                         margin='md',
#                         contents=[
#                             IconComponent(size='sm', url='https://example.com/gold_star.png'),
#                             IconComponent(size='sm', url='https://example.com/grey_star.png'),
#                             IconComponent(size='sm', url='https://example.com/gold_star.png'),
#                             IconComponent(size='sm', url='https://example.com/gold_star.png'),
#                             IconComponent(size='sm', url='https://example.com/grey_star.png'),
#                             TextComponent(text='4.0', size='sm', color='#999999', margin='md',
#                                           flex=0)
#                         ]
#                     ),
#                     # info
#                     BoxComponent(
#                         layout='vertical',
#                         margin='lg',
#                         spacing='sm',
#                         contents=[
#                             BoxComponent(
#                                 layout='baseline',
#                                 spacing='sm',
#                                 contents=[
#                                     TextComponent(
#                                         text='Place',
#                                         color='#aaaaaa',
#                                         size='sm',
#                                         flex=1
#                                     ),
#                                     TextComponent(
#                                         text='Shinjuku, Tokyo',
#                                         wrap=True,
#                                         color='#666666',
#                                         size='sm',
#                                         flex=5
#                                     )
#                                 ],
#                             ),
#                             BoxComponent(
#                                 layout='baseline',
#                                 spacing='sm',
#                                 contents=[
#                                     TextComponent(
#                                         text='Time',
#                                         color='#aaaaaa',
#                                         size='sm',
#                                         flex=1
#                                     ),
#                                     TextComponent(
#                                         text="10:00 - 23:00",
#                                         wrap=True,
#                                         color='#666666',
#                                         size='sm',
#                                         flex=5,
#                                     ),
#                                 ],
#                             ),
#                         ],
#                     )
#                 ],
#             ),
#             footer=BoxComponent(
#                 layout='vertical',
#                 spacing='sm',
#                 contents=[
#                     # callAction, separator, websiteAction
#                     SpacerComponent(size='sm'),
#                     # callAction
#                     ButtonComponent(
#                         style='link',
#                         height='sm',
#                         action=URIAction(label='CALL', uri='tel:000000'),
#                     ),
#                     # separator
#                     SeparatorComponent(),
#                     # websiteAction
#                     ButtonComponent(
#                         style='link',
#                         height='sm',
#                         action=URIAction(label='WEBSITE', uri="https://example.com")
#                     )
#                 ]
#             ),
#         )
#         message = FlexSendMessage(alt_text="hello", contents=bubble)
#         line_bot_api.reply_message(
#             event.reply_token,
#             message
#         )
#     elif text == 'quick_reply':
#         line_bot_api.reply_message(
#             event.reply_token,
#             TextSendMessage(
#                 text='Quick reply',
#                 quick_reply=QuickReply(
#                     items=[
#                         QuickReplyButton(
#                             action=PostbackAction(label="label1", data="data1")
#                         ),
#                         QuickReplyButton(
#                             action=MessageAction(label="label2", text="text2")
#                         ),
#                         QuickReplyButton(
#                             action=DatetimePickerAction(label="label3",
#                                                         data="data3",
#                                                         mode="date")
#                         ),
#                         QuickReplyButton(
#                             action=CameraAction(label="label4")
#                         ),
#                         QuickReplyButton(
#                             action=CameraRollAction(label="label5")
#                         ),
#                         QuickReplyButton(
#                             action=LocationAction(label="label6")
#                         ),
#                     ])))
#     else:
#         line_bot_api.reply_message(
#             event.reply_token, TextSendMessage(text=event.message.text))
#
#
# @handler.add(MessageEvent, message=LocationMessage)
# def handle_location_message(event):
#     line_bot_api.reply_message(
#         event.reply_token,
#         LocationSendMessage(
#             title=event.message.title, address=event.message.address,
#             latitude=event.message.latitude, longitude=event.message.longitude
#         )
#     )
#
#
# @handler.add(MessageEvent, message=StickerMessage)
# def handle_sticker_message(event):
#     line_bot_api.reply_message(
#         event.reply_token,
#         StickerSendMessage(
#             package_id=event.message.package_id,
#             sticker_id=event.message.sticker_id)
# )
