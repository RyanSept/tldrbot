import re
from app import slack_client, textapi_client


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


def get_help_message():
    return [{
        "fallback": "Tldrbot (too long; didn't read) allows you to summarize any article into a 5 sentence (1 minute read).\nTo use it, simply mention '@tldr' in a thread on the message containing a link to an article and wait for our team of scholarly elves to magically generate a summary.\n<https://get.slack.help/hc/en-us/articles/115000769927-Message-threads#start-a-thread-to-reply-to-a-message|How to start a thread>",
        "text": "Tldrbot (too long; didn't read) allows you to summarize any article into a 5 sentence (1 minute read).\n\nTo use it, simply mention '@tldr' in a thread on the message containing a link to an article and wait for our efficient team of scholarly elves to magically generate a summary.\n",
        "color": "#19a8e3",
        "mrkdwn": True,
        "fields": [
            {
                "title": "Glossary",
                "value": "<https://get.slack.help/hc/en-us/articles/115000769927-Message-threads#start-a-thread-to-reply-to-a-message|How to start a thread>"
            }
        ]
    }]
