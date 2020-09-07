# pylint: disable=too-few-public-methods
import logging

from hammurabi.reporters.base import Reporter


class JsonReporter(Reporter):
    """
    Generate reports in Json format and write into file. JsonReporter
    is the default reporter of the pillar. The example below shows the
    way how to replace a reporter which could base on the JsonReporter.

    The report will be written into the configured report file. The report
    file's name set by ``report_name`` config parameter.

    Example usage:

    .. code-block:: python

        >>> from pathlib import Path
        >>> from hammurabi import Law, Pillar, OwnerChanged
        >>> from my_company import MyJsonReporter
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
        >>> # override pillar's default JsonReporter reporter
        >>> pillar = Pillar(reporter_class=MyJsonReporter)
    """

    def report(self) -> None:
        """
        Do the actual reporting based on the report assembled in Json
        format. The report will be written into the configured report file.
        """

        logging.info('Writing report to "%s"', str(self.report_path))
        self.report_path.write_text(self._get_report().json())
