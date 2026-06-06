import json
import os

import pytest

from app.services.report_service import (
    generate_dashboard_stats,
    generate_report,
    generate_sorted_report,
    get_event_date,
    get_login_stats_by_day,
    get_recent_activity,
    get_session_distribution,
)


@pytest.fixture
def sample_events():
    return [
        {"date": "2026-05-20 08:00", "user": "ana", "machine": "PC-01", "type": "login", "ip": "192.168.1.10", "method": "Local"},
        {"date": "2026-05-20 08:10", "user": "carlos", "machine": "PC-01", "type": "login", "ip": "192.168.1.11", "method": "Local"},
        {"date": "2026-05-20 08:30", "user": "ana", "machine": "PC-01", "type": "logout", "ip": "192.168.1.10", "method": "Local"},
        {"date": "2026-05-20 09:00", "user": "maria", "machine": "PC-02", "type": "login", "ip": "192.168.1.20", "method": "MFA"},
    ]


@pytest.fixture
def duplicate_login_events():
    return [
        {"date": "2026-05-20 08:00", "user": "ana", "machine": "PC-01", "type": "login", "ip": "192.168.1.10", "method": "Local"},
        {"date": "2026-05-20 08:05", "user": "ana", "machine": "PC-01", "type": "login", "ip": "192.168.1.10", "method": "Local"},
        {"date": "2026-05-20 09:00", "user": "maria", "machine": "PC-02", "type": "login", "ip": "192.168.1.20", "method": "MFA"},
    ]


def test_get_event_date_returns_date_string(sample_events):
    assert get_event_date(sample_events[0]) == "2026-05-20 08:00"


def test_generate_sorted_report_handles_activity_and_duplicates(sample_events):
    report = generate_sorted_report(list(sample_events))
    assert report["PC-01"] == {"carlos"}
    assert report["PC-02"] == {"maria"}


def test_generate_sorted_report_ignores_duplicate_login_without_logout(duplicate_login_events):
    report = generate_sorted_report(list(duplicate_login_events))
    assert "ana" in report["PC-01"]
    assert "maria" in report["PC-02"]


def test_generate_report_returns_expected_counts(sample_events):
    report = generate_report(list(sample_events))
    assert "PC-01" in report
    assert "PC-02" in report
    assert "carlos" in report["PC-01"]
    assert "ana" not in report["PC-01"]
    assert "maria" in report["PC-02"]


def test_generate_dashboard_stats_computes_expected_values(sample_events):
    report = generate_sorted_report(list(sample_events))
    stats = generate_dashboard_stats(report)
    assert stats["total_machines"] == 2
    assert stats["total_active_users"] == 2
    assert stats["total_sessions"] == 2


def test_get_recent_activity_returns_last_n_events(sample_events):
    recent = get_recent_activity(list(sample_events))
    assert len(recent) == 4
    assert recent[0]["user"] == "maria"


def test_get_login_stats_by_day_counts_logins_per_day(sample_events):
    stats = get_login_stats_by_day(list(sample_events))
    assert stats["labels"] == ["2026-05-20"]
    assert stats["values"] == [3]


def test_get_session_distribution_counts_active_and_inactive(sample_events):
    report = generate_sorted_report(list(sample_events))
    dist = get_session_distribution(report)
    assert dist["labels"] == ["Active", "Inactive"]
    assert dist["values"][0] >= 1
    assert dist["values"][1] >= 0
