from slackclient import SlackClient
from app.config import API_TOKEN
from aylienapiclient import textapi


slack_client = SlackClient(API_TOKEN)
textapi_client = textapi.Client("cffd4827", "262ad2161baa70a58d11d8781bbb4eb2")
