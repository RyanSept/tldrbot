# coding: UTF-8
import re
import json
import time
from slackbot.bot import respond_to
from app import slack_client
from app.core import get_message_by_thread_ts, remove_duplicates_from_list, \
    extract_urls, make_response, no_links_error_attachment, get_help_message


@respond_to('hello$|hi$|hey$|aloha$', re.IGNORECASE)
def hello_reply(message):
    message.reply('Hello young master! You look well. '
                  'Type `help` for assistance')


@respond_to('^(?![\s\S])', re.IGNORECASE)
def summarize(message):
    print message.body
    attachments = []
    channel = message.body["channel"]
    user_message = ''
    message.reply("One moment...")

    if "thread_ts" in message.body:  # mention in thread
        user_message = get_message_by_thread_ts(
            channel, message.body["thread_ts"])
        if not user_message:
            time.sleep(1)
            message.reply("Sorry, we're unable to read through "
                          "messages here for now :disappointed:")
            return

    else:
        if 'is_im' in message.channel._body:
            user_message = message.body['text']

    if user_message:
        time.sleep(1)
        message.reply("Fetching article(s)... :bicyclist:")
        links = remove_duplicates_from_list(extract_urls(user_message))
        attachments.extend(make_response(links)) if links else attachments.extend(
            no_links_error_attachment())
    else:
        attachments.extend(get_help_message())

    time.sleep(1)
    message.send_webapi('', json.dumps(attachments))


@respond_to('help$|assist$', re.IGNORECASE)
def help(message):
    message.send_webapi('', get_help_message())
