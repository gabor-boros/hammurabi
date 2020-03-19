from pathlib import Path

import pytest

from hammurabi.rules.templates import TemplateRendered
from tests.fixtures import temporary_file_generator

assert temporary_file_generator


@pytest.mark.integration
def test_rendered(temporary_file_generator):
    template_path = Path(temporary_file_generator().name)
    template_path.write_text("Hello {{ magic_word }}!")

    destination_path = Path(temporary_file_generator().name)
    destination_path.touch()

    rule = TemplateRendered(
        name="Template rendered",
        template=template_path,
        destination=destination_path,
        context={"magic_word": "World"},
    )

    rule.task()

    assert destination_path.read_text() == "Hello World!"
    destination_path.unlink()


@pytest.mark.integration
def test_destination_overwrite(temporary_file_generator):
    template_path = Path(temporary_file_generator().name)
    template_path.write_text("Hello {{ magic_word }}!")

    destination_path = Path(temporary_file_generator().name)
    destination_path.write_text("Here comes the greeting")

    rule = TemplateRendered(
        name="Template rendered",
        template=template_path,
        destination=destination_path,
        context={"magic_word": "World"},
    )

    rule.task()

    assert destination_path.read_text() == "Hello World!"
    destination_path.unlink()
