import asyncio

from mcp_concierge import SetupPage, with_setup_page

PATH = "/mcp"


async def mcp_endpoint(scope, receive, send):
    await send({"type": "http.response.start", "status": 204, "headers": [(b"x-from", b"mcp")]})
    await send({"type": "http.response.body", "body": b""})


def _request(method: str, path: str = PATH, accept: bytes | None = None) -> dict:
    headers = [(b"accept", accept)] if accept is not None else []
    scope = {"type": "http", "method": method, "path": path, "headers": headers}
    sent = []

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        sent.append(message)

    app = with_setup_page(mcp_endpoint, PATH, SetupPage("Weather"))
    asyncio.run(app(scope, receive, send))
    start, body = sent
    return {"status": start["status"], "headers": dict(start["headers"]), "body": body["body"]}


def test_a_browser_gets_the_page():
    r = _request("GET", accept=b"text/html,application/xhtml+xml")
    assert r["status"] == 200
    assert r["headers"][b"content-type"].startswith(b"text/html")
    assert b"Weather" in r["body"]


def test_a_request_without_accept_gets_the_page():
    assert _request("GET")["status"] == 200


def test_the_page_is_not_indexed():
    assert _request("GET", accept=b"text/html")["headers"][b"x-robots-tag"] == b"noindex"


def test_an_mcp_client_get_reaches_the_endpoint():
    r = _request("GET", accept=b"text/event-stream")
    assert r["headers"][b"x-from"] == b"mcp"


def test_a_post_reaches_the_endpoint():
    r = _request("POST", accept=b"text/html")
    assert r["headers"][b"x-from"] == b"mcp"


def test_other_paths_reach_the_app():
    r = _request("GET", path="/other", accept=b"text/html")
    assert r["headers"][b"x-from"] == b"mcp"
