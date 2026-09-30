import tomllib
from collections.abc import Sequence
from html import escape
from importlib.resources import files
from string import Template

_RESOURCES = files("mcp_concierge")
_TEXTS = tomllib.loads(_RESOURCES.joinpath("texts.toml").read_text())
_CLIENTS = tuple(
    tomllib.loads(f.read_text())
    for f in sorted(_RESOURCES.joinpath("clients").iterdir(), key=lambda f: f.name)
    if f.name.endswith(".toml")
)
LANGUAGES = tuple(_TEXTS)

_TEMPLATE = Template("""<!doctype html>
<html lang="$language">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>$title</title>
<style>
  :root { --text: #1f2328; --muted: #59636e; --bg-soft: #f6f8fa; --border: #d1d9e0; --accent: #c15f3c; }
  body { margin: 0; background: #fff; color: var(--text); font: 17px/1.55 system-ui, sans-serif; }
  main { max-width: 38rem; margin: 0 auto; padding: 2rem 1rem 3rem; }
  h1 { font-size: 1.6rem; margin: 0 0 .5rem; }
  p.intro { color: var(--muted); margin-top: 0; }
  ol { padding-left: 1.3rem; }
  li { margin: 1.1rem 0; }
  a { color: var(--accent); }
  button { font: inherit; padding: .5rem 1rem; border: 0; border-radius: 6px; background: var(--accent); color: #fff; cursor: pointer; }
  .url { display: flex; gap: .5rem; }
  .url input { flex: 1; min-width: 0; font: 14px ui-monospace, monospace; padding: .5rem; border: 1px solid var(--border); border-radius: 6px; background: var(--bg-soft); }
  .choice { display: flex; flex-wrap: wrap; gap: .5rem; }
  .choice button { background: var(--bg-soft); color: var(--text); border: 1px solid var(--border); }
  .choice button[aria-pressed="true"] { background: var(--accent); color: #fff; border-color: var(--accent); }
  .note { color: var(--muted); font-size: .9rem; }
  .examples { background: var(--bg-soft); border-radius: 8px; padding: .5rem 1.2rem; }
  .examples li { margin: .5rem 0; }
</style>
</head>
<body>
<main>
  <h1>$title</h1>
  <p class="intro">$intro</p>

  <p>$copy_label</p>
  <div class="url">
    <input id="url" readonly>
    <button id="copy" type="button">$copy</button>
  </div>

  <p>$choose</p>
  <div class="choice" role="group">
$buttons
  </div>
$sections
$examples
</main>
<script>
  const field = document.getElementById("url");
  field.value = location.href.split("#")[0];
  document.getElementById("copy").addEventListener("click", async (e) => {
    field.select();
    try { await navigator.clipboard.writeText(field.value); } catch { document.execCommand("copy"); }
    e.target.textContent = "$copied";
  });
  const buttons = document.querySelectorAll(".choice button");
  buttons.forEach((b) => b.addEventListener("click", () => {
    buttons.forEach((other) => {
      other.setAttribute("aria-pressed", other === b);
      document.getElementById(other.dataset.client).hidden = other !== b;
    });
  }));
</script>
</body>
</html>
""")


class SetupPage:
    """The page a person sees when they open an MCP server's URL in a browser."""

    def __init__(self, server_name: str, language: str = "en", examples: Sequence[str] = ()) -> None:
        if language not in LANGUAGES:
            raise ValueError(f"language {language!r} not supported, choose one of {LANGUAGES}")
        self._name = escape(server_name)
        self._language = language
        self._examples = tuple(escape(e) for e in examples)

    def html(self) -> bytes:
        texts = _TEXTS[self._language]
        return _TEMPLATE.substitute(
            language=self._language,
            title=texts["title"].format(name=self._name),
            intro=texts["intro"],
            copy_label=texts["copy_label"],
            copy=texts["copy"],
            copied=texts["copied"],
            choose=texts["choose"],
            buttons="\n".join(
                f'    <button type="button" data-client="client-{i}" aria-pressed="{str(i == 0).lower()}">{c["name"]}</button>'
                for i, c in enumerate(_CLIENTS)
            ),
            sections="\n".join(self._section(i, c, texts) for i, c in enumerate(_CLIENTS)),
            examples=self._examples_block(texts),
        ).encode()

    def _section(self, i: int, client: dict, texts: dict) -> str:
        steps = "\n".join(f"      <li>{p.format(name=self._name)}</li>" for p in client["steps"][self._language])
        checked = texts["verified"].format(date=client["verified"].isoformat())
        return f"""  <section id="client-{i}"{"" if i == 0 else " hidden"}>
    <ol>
{steps}
    </ol>
    <p class="note">{client["note"][self._language]} {checked}</p>
  </section>"""

    def _examples_block(self, texts: dict) -> str:
        if not self._examples:
            return ""
        items = "\n".join(f"    <li>{e}</li>" for e in self._examples)
        return f"""  <p>{texts["examples"]}</p>
  <ul class="examples">
{items}
  </ul>"""
