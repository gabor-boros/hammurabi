# pylint: disable=too-few-public-methods

from hammurabi.reporters.base import Reporter


class JSONReporter(Reporter):
    """
    Generate reports in JSON format and write into file. JSONReporter
    is the default reporter of the pillar. The example below shows the
    way how to replace a reporter which could base on the JSONReporter.

    The report will be written into the configured report file. The report
    file's name set by ``report_name`` config parameter.

    Example usage:

    .. code-block:: python

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar, OwnerChanged
        >>> from my_company import MyJSONReporter
        >>>
        >>> example_law = Law(
        >>>     name="Name of the law",
        >>>     description="Well detailed description what this law does.",
        >>>     rules=(
        >>>         OwnerChanged(
        >>>             name="Change ownership of nginx config",
        >>>             path=Path("./nginx.conf"),
        >>>             new_value="www:web_admin"
        >>>         ),
        >>>     )
        >>> )
        >>>
        >>> # override pillar's default JSONReporter reporter
        >>> pillar = Pillar(reporter_class=MyJSONReporter)
    """

    def report(self) -> None:
        """
        Do the actual reporting based on the report assembled in JSON
        format. The report will be written into the configured report file.
        """

        self.report_path.write_text(self._get_report().json())
