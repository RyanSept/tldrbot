from urlparse import urlparse
from slackclient import SlackClient
from aylienapiclient import textapi
from flask import Flask, request, Response
from config import API_TOKEN, SLACK_WEBHOOK_SECRET, AYLIEN_APP_ID, AYLIEN_APP_KEY
import re
import requests
import json


app = Flask(__name__)
slack_client = SlackClient(API_TOKEN)
textapi_client = textapi.Client("cffd4827", "262ad2161baa70a58d11d8781bbb4eb2")


@app.route('/slack', methods=['POST'])
def inbound():
    if request.form.get('token') == SLACK_WEBHOOK_SECRET:
        requests.get(request.form.get("response_url"))  # prevent slack timeout

        channel = request.form.get('channel_id')
        username = request.form.get('user_name')
        command = request.form.get('text').strip().lower()
        inbound_message = username + " in " + channel + " says: " + command

        print inbound_message
        slack_client.api_call(
            "chat.postMessage", channel=channel,
            text="One moment... :bicyclist:")

        attachments = []
        if command == "this":  # get most recent message and check for link
            # get channel history
            response = slack_client.api_call(
                "channels.history", channel=channel, count=2)
            if response["ok"]:
                user_message = response['messages'][-1]["text"]
                links = remove_duplicates_from_list(extract_urls(user_message))
                attachments.extend(make_response(links)) if links else attachments.extend(no_links_error_attachment()) 
            else:
                reply = "Sorry, we're unable to read through "\
                    "messages here :disappointed:"
                slack_client.api_call("chat.postMessage",
                                      channel=channel, text=reply)
                return Response(), 200

        print "Sending", attachments
        slack_client.api_call("chat.postMessage",
                              channel=channel, attachments=attachments)
    return Response(), 200


@app.route('/', methods=['GET'])
def test():
    return Response('It works!')


def get_summary(article_link, summary_length=5):
    '''
    Make call to aylien api
    '''
    params = {"url": article_link, 'sentences_number': summary_length}
    summary = textapi_client.Summarize(params)
    return summary["sentences"]


def make_response(links):
    color = 0
    fallback = ""
    attachments = []
    for link in links:
        if color > 3:
            color = 0
        link = link.strip("<").strip(">")
        print link
        summary = get_summary(link)
        if summary:
            summary = "\n".join(summary)
            heading = "*Summary for:* {}\n".format(link)
            fallback += heading + summary

            attachment = generate_attachment(
                summary, "Summary - " + link.rsplit("/", 1)[-1],
                link, color, fallback)
            attachments.append(attachment)
            color += 1
        else:
            fallback += "\n*We were unable to find the page: {}*\n".format(
                link)
            text = "<{}>".format(link)
            attachment = generate_attachment(
                text, "404 - Page not found", "None", -1, fallback)
            attachments.append(attachment)

    return attachments


def generate_attachment(text, title, title_link, color, fallback):
    colors = ["#6A2D8A", "#D662A8", "#FFB495", "#E07761"]
    return {
        "fallback": fallback,
        "title": title,
        "title_link": title_link,
        "text": text,
        "color": colors[color],
    }


def no_links_error_attachment():
    text = "Oh no :cry: No links were found in the most recent message."
    return [{
        "fallback": text,
        "text": text,
        "color": "#FF3366",
    }]


def extract_urls(url):
    '''
    Extract all urls from message
    '''
    return re.findall("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", url)


def remove_duplicates_from_list(alist):
    return list(set(alist))


if __name__ == "__main__":
    app.run(debug=True)
