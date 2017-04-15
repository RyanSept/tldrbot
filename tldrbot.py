from urlparse import urlparse
from slackclient import SlackClient
from aylienapiclient import textapi
from flask import Flask, request, Response
from config import API_TOKEN, SLACK_WEBHOOK_SECRET, AYLIEN_APP_ID, AYLIEN_APP_KEY
import re
import requests


app = Flask(__name__)
slack_client = SlackClient(API_TOKEN)
textapi_client = textapi.Client("cffd4827", "262ad2161baa70a58d11d8781bbb4eb2")


@app.route('/slack', methods=['POST'])
def inbound():
    if request.form.get('token') == SLACK_WEBHOOK_SECRET:
        channel = request.form.get('channel_id')
        username = request.form.get('user_name')
        command = request.form.get('text').strip().lower()
        inbound_message = username + " in " + channel + " says: " + command

        print inbound_message
        slack_client.api_call(
            "chat.postMessage", channel=channel,
            text="One moment... :bicyclist:")

        reply = ""
        if command == "this":  # get most recent message and check for link
            # get channel history
            response = slack_client.api_call(
                "channels.history", channel=channel, count=2)
            if response["ok"]:
                user_message = response['messages'][-1]["text"]
                links = extract_urls(user_message)
                print links
                for link in links:
                    link = link.strip("<").strip(">")
                    print link
                    summary = get_summary(link)
                    if summary:
                        heading = "*Summary for:* {}\n".format(link)
                        reply += heading + "\n".join(summary)
                    else:
                        reply += "\n*We were unable to find the page: {}*".format(link)
            else:
                reply += "Sorry, we're unable to read through"\
                    "messages here :disappointed:"

        slack_client.api_call("chat.postMessage", channel=channel, text=reply)
    return Response(), 200


@app.route('/', methods=['GET'])
def test():
    return Response('It works!')


def url_validate(url):
    try:
        result = urlparse(url)
        return True if [result.scheme, result.netloc, result.path] else False
    except Exception as err:
        return False


def get_summary(article_link, summary_length=5):
    '''
    Make call to smmry api
    '''
    params = {"url": article_link, 'sentences_number': summary_length}
    summary = textapi_client.Summarize(params)
    return summary["sentences"]


def extract_urls(url):
    return re.findall("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", url)


if __name__ == "__main__":
    app.run(debug=True)
