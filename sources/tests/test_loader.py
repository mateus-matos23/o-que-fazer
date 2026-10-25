from pathlib import Path

import pytest
from django.core.management import CommandError, call_command

from sources.loader import load_sources
from sources.models import Agency, Source
from sources.toml_schema import ContentError

pytestmark = pytest.mark.django_db

BASE = """
[[agencies]]
slug = "mte"
name = "MTE"
jurisdiction = "FEDERAL"

[[sources]]
slug = "pagina"
agency = "mte"
url = "https://example.gov.br/a"
format = "HTML"
jurisdiction = "FEDERAL"
"""


def _write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "sources.toml"
    path.write_text(text)
    return path


def test_upsert_creates_then_updates(tmp_path: Path) -> None:
    path = _write(tmp_path, BASE)
    assert load_sources(path) == {"Agency": 1, "Source": 1}
    path.write_text(BASE.replace('name = "MTE"', 'name = "Ministério"') + 'access_notes = "x"\n')
    load_sources(path)
    assert Agency.objects.get().name == "Ministério"
    assert Source.objects.get().access_notes == "x"


def test_never_deletes(tmp_path: Path) -> None:
    load_sources(_write(tmp_path, BASE))
    load_sources(_write(tmp_path, BASE.replace("pagina", "outra").replace("/a", "/b")))
    assert Source.objects.count() == 2


def test_source_may_reference_agency_in_database(tmp_path: Path) -> None:
    load_sources(_write(tmp_path, BASE))
    only_source = BASE.split("[[sources]]")[1]
    load_sources(
        _write(tmp_path, "[[sources]]" + only_source.replace("pagina", "nova").replace("/a", "/c"))
    )
    assert Source.objects.count() == 2


def test_unknown_agency_fails_and_writes_nothing(tmp_path: Path) -> None:
    path = _write(tmp_path, BASE.replace('agency = "mte"', 'agency = "x"'))
    with pytest.raises(ContentError, match=r"sources\.toml: pagina: agência inexistente: x"):
        load_sources(path)
    assert Agency.objects.count() == 0


def test_unknown_key_fails(tmp_path: Path) -> None:
    path = _write(tmp_path, BASE + "extra = 1\n")
    with pytest.raises(ContentError, match="pagina: extra: chave desconhecida"):
        load_sources(path)


def test_command_reports_errors_and_counts(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    call_command("load_sources", str(_write(tmp_path, BASE)))
    assert "Source: 1" in capsys.readouterr().out
    bad = _write(tmp_path, BASE.replace('format = "HTML"', 'format = "PDF"'))
    with pytest.raises(CommandError, match="format"):
        call_command("load_sources", str(bad))


def test_long_slug_and_bad_url_length_fail_with_file_and_slug(tmp_path: Path) -> None:
    long_slug = "a" * 51
    path = _write(tmp_path, BASE.replace('slug = "pagina"', f'slug = "{long_slug}"'))
    with pytest.raises(ContentError, match=rf"sources\.toml: {long_slug}: slug: excede 50"):
        load_sources(path)


def test_invalid_utf8_fails(tmp_path: Path) -> None:
    path = tmp_path / "sources.toml"
    path.write_bytes(b"\xff\xfe[[agencies]]")
    with pytest.raises(ContentError, match=r"sources\.toml: -: arquivo não está em UTF-8"):
        load_sources(path)


def test_missing_file_fails(tmp_path: Path) -> None:
    with pytest.raises(ContentError, match=r"sources\.toml: -: não foi possível ler"):
        load_sources(tmp_path / "sources.toml")


def test_url_swap_between_sources_is_rejected_not_integrity_error(tmp_path: Path) -> None:
    load_sources(_write(tmp_path, BASE))
    second = BASE.split("[[sources]]")[1].replace("pagina", "outra").replace("/a", "/b")
    load_sources(_write(tmp_path, "[[sources]]" + second))
    swapped = "[[sources]]" + second.replace("/b", "/a")
    with pytest.raises(ContentError, match=r"outra: url já usada pela fonte pagina"):
        load_sources(_write(tmp_path, swapped))
