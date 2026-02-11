import boto3
import json
import logging
import re
import urllib.error
from html import unescape
from prompts import system_prompt


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

bedrock_client = boto3.client(service_name="bedrock-runtime")
logger = logging.getLogger(__name__)
logger.setLevel("INFO")


def handler(event, context):
    """Extract the recipe from the page content."""
    url = _get_url_from_event(event)
    if not url:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": 'Missing or invalid "url" in event'}),
        }

    try:
        content = _fetch_html(url)
    except urllib.error.HTTPError as e:
        return {
            "statusCode": e.code,
            "body": json.dumps({"error": f"HTTP error: {e.reason}", "url": url}),
        }
    except urllib.error.URLError as e:
        return {
            "statusCode": 502,
            "body": json.dumps(
                {"error": f"Failed to fetch URL: {e.reason}", "url": url}
            ),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e), "url": url}),
        }

    recipes_from_jsonld = _extract_jsonld_recipes(content)
    if recipes_from_jsonld:
        recipe = _extract_recipe(recipes_from_jsonld)
    else:
        recipe = _extract_recipe(_cheap_html_cleanup(content))

    return {
        "statusCode": 200,
        "body": recipe,
    }


def _get_url_from_event(event):
    """Extract URL from event (direct invoke or API Gateway body)."""
    if isinstance(event.get("body"), str):
        try:
            payload = json.loads(event["body"])
        except (json.JSONDecodeError, TypeError):
            return None
        return (payload or {}).get("url") or None
    return event.get("url")


def _extract_jsonld_recipes(html: str):
    """Return list of recipe objects found in JSON-LD."""
    recipes = []
    jsonld_re = re.compile(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        re.IGNORECASE | re.DOTALL,
    )

    for m in jsonld_re.finditer(html):
        blob = unescape(m.group(1)).strip()
        if not blob:
            continue
        try:
            data = json.loads(blob)
        except Exception:
            continue

        nodes = []
        if isinstance(data, list):
            nodes = data
        elif isinstance(data, dict):
            if "@graph" in data and isinstance(data["@graph"], list):
                nodes = data["@graph"]
            else:
                nodes = [data]

        for node in nodes:
            if not isinstance(node, dict):
                continue
            t = node.get("@type")
            # @type can be string or list
            types = {t} if isinstance(t, str) else set(t or [])
            if "Recipe" in types:
                recipes.append(node)

    return recipes


def _fetch_html(url):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "MealMapper/1.0 (Recipe extractor)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        ctype = (resp.headers.get("Content-Type") or "").lower()
        if "html" not in ctype and "xml" not in ctype:
            raise ValueError(f"Non-HTML content-type: {ctype}")

        return resp.read().decode("utf-8", errors="replace")


def _cheap_html_cleanup(html: str) -> str:
    html = re.sub(r"<script\b[^>]*>.*?</script>", " ", html, flags=re.I | re.S)
    html = re.sub(r"<style\b[^>]*>.*?</style>", " ", html, flags=re.I | re.S)
    html = re.sub(r"<noscript\b[^>]*>.*?</noscript>", " ", html, flags=re.I | re.S)
    html = re.sub(r"\s+", " ", html)
    return html


def _extract_recipe(content):
    """Extract the recipe from the page content."""

    messages = [
        {
            "role": "user",
            "content": [{"text": f"this is the content of the page: {content}"}],
        }
    ]

    with open("schema.json", "r", encoding="utf-8") as f:
        schema = f.read()

    response = bedrock_client.converse(
        modelId="us.anthropic.claude-haiku-4-5-20251001-v1:0",
        messages=messages,
        system=[{"text": system_prompt()}],
        outputConfig={
            "textFormat": {
                "type": "json_schema",
                "structure": {
                    "jsonSchema": {
                        "schema": schema,
                        "name": "recipe_extraction",
                        "description": "Extract structured data from unstructured text",
                    }
                },
            }
        },
    )

    token_usage = response["usage"]
    logger.info("Input tokens: %s", token_usage["inputTokens"])
    logger.info("Output tokens: %s", token_usage["outputTokens"])
    logger.info("Total tokens: %s", token_usage["totalTokens"])
    logger.info("Stop reason: %s", response["stopReason"])

    return response["output"]["message"]
