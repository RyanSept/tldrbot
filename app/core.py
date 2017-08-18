import re
from app import slack_client, textapi_client
from newspaper import Article, Config
from slackbot import settings


def get_message_by_thread_ts(channel, thread):
    '''
    Get full thread message bot was mentioned in
    '''
    # get messages from channel history starting from ours
    response = slack_client.api_call(
        "channels.history", channel=channel, oldest=thread,
        inclusive=True)

    if not response["ok"]:
        return False

    return response['messages'][-1]["text"]


def extract_urls(message):
    '''
    Extract all urls from message
    '''
    return re.findall("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", message)


def remove_duplicates_from_list(alist):
    return list(set(alist))


def get_article(article_link, summary_length=5):
    '''
    Extract article and summarize it
    '''
    article = Article(article_link)
    article.build()
    return article


def make_response(links):
    """
    Get the summary and build the attachment
    """
    color = 0
    fallback = ""
    attachments = []
    for link in links:
        if color > 3:
            color = 0
        link = link.strip("<").strip(">")
        article = get_article(link)
        if article.title:
            summary = article.summary
            heading = "*Summary for:* {}\n".format(link)
            fallback += heading + summary

            attachment = generate_attachment(
                summary, "Summary for: " + article.title,
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
    """
    Generate response attachment
    """
    colors = ["#6A2D8A", "#D662A8", "#FFB495", "#E07761"]
    return {
        "fallback": fallback,
        "title": title,
        "title_link": title_link,
        "text": text,
        "color": colors[color],
    }


def no_links_error_attachment():
    """
    Generates reply for when no links are found in the message the user tags us
    """
    text = "Oh no :cry: No links were found in the most recent message."
    return [{
        "fallback": text,
        "text": text,
        "color": "#FF3366",
    }]


def get_help_message():
    """Get the help message attachment."""
    return [{
        "fallback": "Tldrbot (too long; didn't read) summarizes any article into a 5 sentence (~1 minute read).\nTo use it, simply mention <@tldr> in a thread on the message containing a link to an article or direct message <@tldr> the link and wait for our team of scholarly elves to magically generate a summary.\n<https://get.slack.help/hc/en-us/articles/115000769927-Message-threads#start-a-thread-to-reply-to-a-message|How to start a thread>",
        "text": "Tldrbot (too long; didn't read) summarizes any article into a 5 sentence (~1 minute read).\n\nTo use it, simply mention <@tldr> in a thread on the message containing a link to an article or direct message <@tldr> the link and wait for our efficient team of scholarly elves to magically generate a summary.\n",
        "color": "#19a8e3",
        "mrkdwn": True,
        "fields": [
            {
                "title": "Glossary",
                "value": "<https://get.slack.help/hc/en-us/articles/115000769927-Message-threads#start-a-thread-to-reply-to-a-message|How to start a thread>"
            },
            {
                "title": "Report bugs/Send feedback",
                "value": "Carpe DM <@{}>".format(settings.ERRORS_TO)
            }
        ]
    }]
