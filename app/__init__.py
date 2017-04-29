from slackclient import SlackClient
from app.config import API_TOKEN, AYLIEN_CLIENT_ID, AYLIEN_CLIENT_SECRET
from aylienapiclient import textapi


slack_client = SlackClient(API_TOKEN)
textapi_client = textapi.Client(AYLIEN_CLIENT_ID, AYLIEN_CLIENT_SECRET)
