# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## What this is

A small Python library that serves a human-readable setup page when someone opens a remote MCP server's URL in a browser, instead of the blank page that never finishes loading (the browser hangs on the SSE stream). The page explains, per client (Claude, ChatGPT, …) and in the reader's language, how to add the server as a connector, with a button to copy the URL.

The reason it exists: a non-technical person given an MCP server URL tends to open it in a browser, see nothing, and give up.

**Status: private repo (`fain182/mcp-concierge`), not published.** The owner wants it solid before making it public and putting it on PyPI. Don't publish, change visibility or add a license without being asked.

## Commands

- `make install-dev` — `uv sync` (dev group: pytest)
- `make test` — full suite

## Design decisions (and why)

- **Separate package, not a feature of the MCP SDK.** The instructions are most of the value, and they go stale fast (menus and plans change). They need their own release cadence, and one central place that keeps them updated is better than every MCP server author copying and forgetting them. A hook in the SDK alone would leave each author to write the instructions.
- **Instructions are data, not code.** One TOML file per client in `mcp_concierge/clients/`, with steps and a note per language and a `verified` date that the page shows. Updating a client must be a change to its file only, so outside contributors can do it. `tests/test_page.py::TestClientData` enforces that every client has steps and note in every language in `texts.toml`, the same number of steps in each, and a date. Clients are ordered by file name; the first one is selected by default.
- **Step strings are trusted HTML** (they may contain `<b>`, `<a>`), owned by this package. `{name}` inside them is replaced by the escaped server name. The server name and examples come from the caller and are always escaped.
- **Browser vs MCP client detection:** the Streamable HTTP spec (modelcontextprotocol.io, transports) requires clients to list `text/event-stream` in the `Accept` header of their GETs. A GET on the MCP path without it gets the page; everything else (POST, SSE GET, other paths) goes to the wrapped app. Keep this rule — a looser one could break real clients.
- **The URL is read in the browser (`location.href`), not built server-side.** Behind a hosting proxy the server sees `http` and internal hosts; the address bar is always right. It also means the MCP secret path is never written into the HTML by the server.
- **`noindex` (meta tag + `X-Robots-Tag` header), not robots.txt.** Servers often protect the endpoint with a secret path: a `Disallow` would publish it, and `Disallow: /` stops crawlers from reading the page and therefore the `noindex`, while the URL can still be indexed if linked somewhere.
- **No dependencies.** The core is a pure function producing bytes plus a 20-line ASGI wrapper; it works with the MCP Python SDK's `streamable_http_app()`, FastMCP or any Starlette/ASGI app.

## Known uncertainties

- **ChatGPT steps are generic and not verified on a real account.** As of 2026-09-30 the sources disagreed: OpenAI's developer docs (developers.openai.com/apps-sdk/deploy/connect-chatgpt) say availability "depends on account and workspace policy" and describe Settings → Security and login → Developer mode; FastMCP's docs say Settings → Connectors → Advanced; a 2026-09-21 article (peliqan.io) says only Business/Enterprise/Edu workspaces can create custom MCP connectors, not Free/Plus/Pro. The OpenAI help article (help.openai.com/en/articles/12584461) returned 403 to automated fetches. The note on the page tells users their plan may not include it. Fix the steps once someone checks them on a real account, and update `verified`.
- **Claude steps** follow claude.com/docs/connectors/custom/remote-mcp (checked 2026-09-30): Customize → Connectors → Add custom connector; custom connectors by URL work on Free (one connector), Pro, Max, Team, Enterprise. The Italian UI labels were not verified.
- The page has not been looked at rendered in a browser from this repo (no headless browser on the machine where it was written).

## Possible next steps

- More clients: Claude Code (a `claude mcp add --transport http <name> <url>` command to copy), Cursor, VS Code. Some have one-click install links: verify each one before adding it.
- Pick the language from the browser's `Accept-Language` instead of a fixed parameter.
- A periodic check that flags clients whose `verified` date is older than N months.

## Conventions

- Code, identifiers, comments, commit messages and README in English (the package is meant to go public).
- Comments explain a current constraint, not history.
