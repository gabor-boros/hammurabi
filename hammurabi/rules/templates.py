"""
Templates module contains rules which are capable to create a new
file based on a Jinja2 template by rendering it.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Template

from hammurabi.rules.common import SinglePathRule


class TemplateRendered(SinglePathRule):
    """
    Render a file from a Jinja2 template. In case the destination
    file not exists, this rule will create it, otherwise the file will
    be overridden.

    Example usage:

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar, TemplateRendered
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         TemplateRendered(
        >>>             name="Create gunicorn config from template",
        >>>             template=Path("/tmp/templates/gunicorn.conf.py"),
        >>>             destination=Path("./gunicorn.conf.py"),
        >>>             context={
        >>>                 "keepalive": 65
        >>>             },
        >>>         ),
        >>>     )
        >>> )
        >>>
        >>> pillar = Pillar()
        >>> pillar.register(example_law)
    """

    def __init__(
        self,
        name: str,
        template: Optional[Path] = None,
        destination: Optional[Path] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> None:
        self.destination: Path = self.validate(destination, required=True)
        self.context: Dict[str, Any] = context or dict()
        super().__init__(name, template, **kwargs)

    def post_task_hook(self):
        """
        Add the destination and not the original path.
        """

        self.git_add(self.destination)

    def task(self) -> Path:
        """
        Render a file from a Jinja2 template. In case the destination
        file not exists, this rule will create it, otherwise the file will
        be overridden.

        :return: Returns the path of the rendered file
        :rtype: Path
        """

        logging.debug('rendering template "%s"', str(self.param))
        rendered = Template(self.param.read_text()).render(self.context)
        self.destination.write_text(rendered)

        return self.destination
