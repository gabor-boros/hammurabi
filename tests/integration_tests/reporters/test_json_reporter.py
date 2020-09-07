from datetime import datetime
import json
from pathlib import Path
from unittest.mock import Mock, patch

from hammurabi.law import Law
from hammurabi.pillar import Pillar
from hammurabi.reporters.json import JsonReporter
from tests.fixtures import temporary_file
from tests.helpers import get_failing_rule, get_passing_rule

assert temporary_file


@patch("hammurabi.pillar.datetime")
def test_reporter(mocked_datetime, temporary_file):
    report_path = Path(temporary_file.name)

    start = datetime.min
    finish = datetime.max
    mocked_datetime.now.side_effect = [start, finish]

    expected_pr_url = "https://github.com/gabor-boros/hammurabi/pull/1"

    pillar = Pillar(reporter_class=JsonReporter)
    reporter: JsonReporter = pillar.reporter
    reporter.report_path = report_path

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
        "passed": [{"law": expected_law, "name": passing_rule.name}],
        "failed": [{"law": expected_law, "name": failing_rule.name}],
        "skipped": [],
        "additional_data": {
            "pull_request_url": expected_pr_url,
            "started": start.isoformat(),
            "finished": finish.isoformat(),
        },
    }

    # Actually do not push anything
    pillar.checkout_branch = Mock()
    pillar.push_changes = Mock()
    pillar.create_pull_request = Mock()
    pillar.create_pull_request.return_value = expected_pr_url

    # Register the law
    pillar.register(law)

    # Run the enforcement and get the report
    pillar.enforce()
    reporter.report()

    assert expected_report == json.loads(report_path.read_text())
