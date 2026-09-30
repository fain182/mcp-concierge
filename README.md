# mcp-concierge

Turns your MCP server URL into a setup page.

When someone opens a remote MCP server's URL in a browser, they usually get a blank page that never finishes loading. With mcp-concierge they get step-by-step instructions to add the server to their assistant (Claude, ChatGPT, …), in their language, with a button to copy the URL. MCP clients keep reaching the endpoint as before.

```python
from mcp_concierge import SetupPage, with_setup_page

app = with_setup_page(mcp_app, "/mcp", SetupPage("My server", language="en", examples=["What can you do?"]))
```

`mcp_app` is any ASGI app serving the MCP endpoint at `/mcp`, for example the one returned by the MCP Python SDK's `streamable_http_app()`.

## How it tells a browser from an MCP client

The Streamable HTTP spec requires MCP clients to list `text/event-stream` in the `Accept` header of their GET requests. A GET to the MCP path without it gets the page; everything else goes to your app.

## Instructions per client

Each client's steps live in `mcp_concierge/clients/<client>.toml`, with a `verified` date shown on the page. Menus change often: updating a client is a change to that file only.

## Development

```
make install-dev
make test
```
