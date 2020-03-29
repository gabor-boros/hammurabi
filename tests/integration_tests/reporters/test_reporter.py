from datetime import datetime
from unittest.mock import Mock, patch

from hammurabi.law import Law
from hammurabi.pillar import Pillar
from hammurabi.reporters.base import Report, Reporter
from tests.helpers import get_failing_rule, get_passing_rule


class TestReporter(Reporter):
    def report(self) -> Report:
        return self._get_report()


@patch("hammurabi.pillar.datetime")
def test_reporter(mocked_datetime):
    start = datetime.min
    finish = datetime.max
    mocked_datetime.now.side_effect = [start, finish]

    expected_pr_url = "https://github.com/gabor-boros/hammurabi/pull/1"

    pillar = Pillar(reporter_class=TestReporter)
    reporter = pillar.reporter

    passing_rule = get_passing_rule()
    failing_rule = get_failing_rule()

    law = Law(
        name="Integration test law",
        description="Integration test law description",
        rules=(passing_rule, failing_rule),
    )

    law.commit = Mock()

    expected_law = {
        "name": "Integration test law",
        "description": "Integration test law description",
    }

    expected_report = {
        "passed": [
            {
                "law": expected_law,
                "name": passing_rule.name,
            }
        ],
        "failed": [
            {
                "law": expected_law,
                "name": failing_rule.name,
            }
        ],
        "skipped": [],
        "additional_data": {
            "pull_request_url": expected_pr_url,
            "started": start.isoformat(),
            "finished": finish.isoformat(),
        },
    }

    # Actually do not push anything
    pillar.push_changes = Mock()
    pillar.create_pull_request = Mock()
    pillar.create_pull_request.return_value = expected_pr_url

    # Register the law
    pillar.register(law)

    # Run the enforcement and get the report
    pillar.enforce()
    report = reporter.report().dict()

    assert report == expected_report
