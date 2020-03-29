from datetime import datetime
from unittest.mock import Mock, PropertyMock

from hammurabi.reporters.base import Report, Reporter


class TestReporter(Reporter):
    def report(self) -> Report:
        return self._get_report()


def test_reporter():
    mocked_passed_rule = Mock()
    mocked_passed_rule.name = "Mocked passed rule"

    mocked_failed_rule = Mock()
    mocked_failed_rule.name = "Mocked failed rule"

    mocked_skipped_rule = Mock()
    mocked_skipped_rule.name = "Mocked skipped rule"

    mocked_law = Mock()
    mocked_law.name = "Test law"
    mocked_law.description = "Test law description"

    mocked_passed_rules_prop = PropertyMock(return_value=[mocked_passed_rule])
    mocked_failed_rules_prop = PropertyMock(return_value=[mocked_failed_rule])
    mocked_skipped_rules_prop = PropertyMock(return_value=[mocked_skipped_rule])

    type(mocked_law).passed_rules = mocked_passed_rules_prop
    type(mocked_law).failed_rules = mocked_failed_rules_prop
    type(mocked_law).skipped_rules = mocked_skipped_rules_prop

    expected_law = {"name": mocked_law.name, "description": mocked_law.description}

    expected_report = {
        "passed": [{"name": mocked_passed_rule.name, "law": expected_law}],
        "failed": [{"name": mocked_failed_rule.name, "law": expected_law}],
        "skipped": [{"name": mocked_skipped_rule.name, "law": expected_law}],
        "additional_data": {
            "pull_request_url": "",
            "started": datetime.min.isoformat(),
            "finished": datetime.min.isoformat(),
        },
    }

    reporter = TestReporter([mocked_law])
    report = reporter.report().dict()

    assert report == expected_report


def test_empty_report_returns_default():
    reporter = TestReporter(list())
    report = reporter.report()

    assert report == Report()


def test_no_passed():
    mocked_failed_rule = Mock()
    mocked_failed_rule.name = "Mocked failed rule"

    mocked_skipped_rule = Mock()
    mocked_skipped_rule.name = "Mocked skipped rule"

    mocked_law = Mock()
    mocked_law.name = "Test law"
    mocked_law.description = "Test law description"

    mocked_passed_rules_prop = PropertyMock(return_value=[])
    mocked_failed_rules_prop = PropertyMock(return_value=[mocked_failed_rule])
    mocked_skipped_rules_prop = PropertyMock(return_value=[mocked_skipped_rule])

    type(mocked_law).passed_rules = mocked_passed_rules_prop
    type(mocked_law).failed_rules = mocked_failed_rules_prop
    type(mocked_law).skipped_rules = mocked_skipped_rules_prop

    expected_law = {"name": mocked_law.name, "description": mocked_law.description}

    expected_report = {
        "passed": [],
        "failed": [{"name": mocked_failed_rule.name, "law": expected_law}],
        "skipped": [{"name": mocked_skipped_rule.name, "law": expected_law}],
        "additional_data": {
            "pull_request_url": "",
            "started": datetime.min.isoformat(),
            "finished": datetime.min.isoformat(),
        },
    }

    reporter = TestReporter([mocked_law])
    report = reporter.report().dict()

    assert report == expected_report


def test_no_failed():
    mocked_passed_rule = Mock()
    mocked_passed_rule.name = "Mocked passed rule"

    mocked_skipped_rule = Mock()
    mocked_skipped_rule.name = "Mocked skipped rule"

    mocked_law = Mock()
    mocked_law.name = "Test law"
    mocked_law.description = "Test law description"

    mocked_passed_rules_prop = PropertyMock(return_value=[mocked_passed_rule])
    mocked_failed_rules_prop = PropertyMock(return_value=[])
    mocked_skipped_rules_prop = PropertyMock(return_value=[mocked_skipped_rule])

    type(mocked_law).passed_rules = mocked_passed_rules_prop
    type(mocked_law).failed_rules = mocked_failed_rules_prop
    type(mocked_law).skipped_rules = mocked_skipped_rules_prop

    expected_law = {"name": mocked_law.name, "description": mocked_law.description}

    expected_report = {
        "passed": [{"name": mocked_passed_rule.name, "law": expected_law}],
        "failed": [],
        "skipped": [{"name": mocked_skipped_rule.name, "law": expected_law}],
        "additional_data": {
            "pull_request_url": "",
            "started": datetime.min.isoformat(),
            "finished": datetime.min.isoformat(),
        },
    }

    reporter = TestReporter([mocked_law])
    report = reporter.report().dict()

    assert report == expected_report


def test_no_skipped():
    mocked_passed_rule = Mock()
    mocked_passed_rule.name = "Mocked passed rule"

    mocked_failed_rule = Mock()
    mocked_failed_rule.name = "Mocked failed rule"

    mocked_law = Mock()
    mocked_law.name = "Test law"
    mocked_law.description = "Test law description"

    mocked_passed_rules_prop = PropertyMock(return_value=[mocked_passed_rule])
    mocked_failed_rules_prop = PropertyMock(return_value=[mocked_failed_rule])
    mocked_skipped_rules_prop = PropertyMock(return_value=[])

    type(mocked_law).passed_rules = mocked_passed_rules_prop
    type(mocked_law).failed_rules = mocked_failed_rules_prop
    type(mocked_law).skipped_rules = mocked_skipped_rules_prop

    expected_law = {"name": mocked_law.name, "description": mocked_law.description}

    expected_report = {
        "passed": [{"name": mocked_passed_rule.name, "law": expected_law}],
        "failed": [{"name": mocked_failed_rule.name, "law": expected_law}],
        "skipped": [],
        "additional_data": {
            "pull_request_url": "",
            "started": datetime.min.isoformat(),
            "finished": datetime.min.isoformat(),
        },
    }

    reporter = TestReporter([mocked_law])
    report = reporter.report().dict()

    assert report == expected_report
