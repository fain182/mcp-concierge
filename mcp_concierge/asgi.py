from .page import SetupPage


def with_setup_page(app, path: str, page: SetupPage):
    """Wraps an ASGI app so that a browser opening `path` gets `page` instead of the MCP endpoint."""
    body_bytes = page.html()

    async def asgi(scope, receive, send):
        # An MCP client always lists text/event-stream in the Accept of its GETs (Streamable HTTP
        # spec): without it, it's a person in a browser, who would otherwise hang on the SSE stream.
        if scope["type"] == "http" and scope["method"] == "GET" and scope["path"] == path:
            accept = dict(scope["headers"]).get(b"accept", b"")
            if b"text/event-stream" not in accept:
                await send({
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [(b"content-type", b"text/html; charset=utf-8"), (b"x-robots-tag", b"noindex")],
                })
                await send({"type": "http.response.body", "body": body_bytes})
                return
        await app(scope, receive, send)

    return asgi
