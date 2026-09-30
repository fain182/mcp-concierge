import datetime
import tomllib
from importlib.resources import files

import pytest

from mcp_concierge import LANGUAGES, SetupPage

CLIENTS = [
    (f.name, tomllib.loads(f.read_text()))
    for f in files("mcp_concierge").joinpath("clients").iterdir()
    if f.name.endswith(".toml")
]


def test_shows_every_client():
    html = SetupPage("Weather").html().decode()
    for _, client in CLIENTS:
        assert f">{client['name']}</button>" in html


def test_only_the_first_client_starts_visible():
    html = SetupPage("Weather").html().decode()
    assert html.count("<section") == len(CLIENTS)
    assert html.count("<section") - html.count(" hidden>") == 1


def test_escapes_the_server_name():
    html = SetupPage("<script>x</script>").html().decode()
    assert "<script>x</script>" not in html
    assert "&lt;script&gt;x&lt;/script&gt;" in html


def test_writes_in_the_chosen_language():
    assert "Copia questo indirizzo" in SetupPage("Weather", "it").html().decode()
    assert "Copy this address" in SetupPage("Weather", "en").html().decode()


def test_rejects_an_unknown_language():
    with pytest.raises(ValueError):
        SetupPage("Weather", "xx")


def test_shows_the_examples_escaped():
    html = SetupPage("Weather", examples=["Rain < 5mm?"]).html().decode()
    assert "<li>Rain &lt; 5mm?</li>" in html


def test_without_examples_there_is_no_examples_block():
    assert 'class="examples"' not in SetupPage("Weather").html().decode()


def test_is_not_indexed():
    assert '<meta name="robots" content="noindex' in SetupPage("Weather").html().decode()


@pytest.mark.parametrize(("file", "client"), CLIENTS, ids=[f for f, _ in CLIENTS])
class TestClientData:
    def test_has_steps_and_note_in_every_language(self, file, client):
        for language in LANGUAGES:
            assert client["steps"][language], f"{file}: no steps in {language}"
            assert client["note"][language], f"{file}: no note in {language}"

    def test_has_the_same_number_of_steps_in_every_language(self, file, client):
        assert len({len(client["steps"][language]) for language in LANGUAGES}) == 1

    def test_has_a_verification_date(self, file, client):
        assert isinstance(client["verified"], datetime.date)
