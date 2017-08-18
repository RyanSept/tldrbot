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
def handle_mention_in_thread(message):
    attachments = []
    channel = message.body["channel"]
    user_message = ''

    if "thread_ts" in message.body:  # mention in thread
        user_message = get_message_by_thread_ts(
            channel, message.body["thread_ts"])
        if not user_message:
            time.sleep(1)
            message.reply("Sorry, we're unable to read through "
                          "messages here for now :disappointed:",
                          in_thread=True)
            return

    if user_message:
        time.sleep(1)
        message.reply(
            "Sir Cutsalot is fetching the article(s) summary... :horse_racing:", in_thread=True)
        links = remove_duplicates_from_list(extract_urls(user_message))

        # make attachments summarized article content if
        # there are links otherwise error
        attachments.extend(make_response(links)) if links else attachments.extend(
            no_links_error_attachment())
    else:
        attachments.extend(get_help_message())

    time.sleep(1)
    message.reply_webapi('<@{}>'.format(message._get_user_id()),
                         json.dumps(attachments), in_thread=True)


@respond_to('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', re.IGNORECASE)
def handle_dm(message):
    attachments = []
    user_message = ''

    if 'is_im' in message.channel._body and message.channel._body["is_im"]:
        user_message = message.body['text']

    if user_message:
        time.sleep(1)
        message.reply("Sir Cutsalot is fetching the article(s) summary... :horse_racing:")
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
