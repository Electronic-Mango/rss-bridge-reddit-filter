from os import getenv

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from httpx import get
from lxml.etree import fromstring, tostring

load_dotenv()
RSS_BRIDGE_URL = getenv("RSS_BRIDGE_URL")
SUBREDDIT_FILTER = "https://www.reddit.com/r/{subreddit}/"
ENCODING = "UTF-8"

app = FastAPI()


@app.get("/user/{subreddit}")
def user(subreddit: str, request: Request):
    params = dict(request.query_params)
    params |= {"action": "display", "bridge": "RedditBridge", "context": "user", "format": "Mrss"}
    rss_bridge_response = get(RSS_BRIDGE_URL, params=params)
    filtered_response = filter_rss(rss_bridge_response.text, subreddit)
    return PlainTextResponse(filtered_response)


def filter_rss(xml: str, subreddit: str) -> str:
    tree = fromstring(xml.encode(ENCODING))
    subreddit_filter = f"{SUBREDDIT_FILTER.format(subreddit=subreddit)}"
    items = tree.xpath(f"//item[not(starts-with(link,'{subreddit_filter}'))]")
    for item in items:
        item.getparent().remove(item)
    return tostring(tree, xml_declaration=True, pretty_print=True, encoding=ENCODING)
