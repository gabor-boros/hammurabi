from unittest.mock import Mock, patch

from hammurabi.rules.templates import TemplateRendered


@patch("hammurabi.rules.templates.Template")
def test_rendered(mocked_template):
    mock_rendered_template = Mock()
    mock_template = Mock()
    mock_template.render.return_value = mock_rendered_template
    mocked_template.return_value = mock_template

    template_path = Mock()
    expected_destination = Mock()
    expected_context = {"context": "rendered"}

    rule = TemplateRendered(
        name="Template rendered",
        template=template_path,
        destination=expected_destination,
        context=expected_context,
    )

    rule.git_add = Mock()

    result = rule.task()
    rule.post_task_hook()

    mock_template.render.assert_called_once_with(expected_context)
    expected_destination.write_text.assert_called_once_with(mock_rendered_template)

    rule.git_add.assert_called_once_with(expected_destination)

    assert result == expected_destination
