"""Совместимость профиля сенсора и подписчика."""

from course_bringup.qos import sensor_profile, subscriber_profile
import pytest
from rclpy.qos import qos_check_compatible, QoSCompatibility, ReliabilityPolicy


def test_sensor_publisher_is_best_effort():
    assert sensor_profile().reliability == ReliabilityPolicy.BEST_EFFORT
    assert sensor_profile().depth == 10


def test_reliable_subscriber_rejects_best_effort_sensor():
    result, reason = qos_check_compatible(
        sensor_profile(), subscriber_profile('reliable'))
    assert result == QoSCompatibility.ERROR
    assert 'reliable' in reason.lower()


def test_best_effort_subscriber_accepts_sensor():
    result, _reason = qos_check_compatible(
        sensor_profile(), subscriber_profile('best_effort'))
    assert result != QoSCompatibility.ERROR
    assert subscriber_profile('best_effort').reliability == (
        ReliabilityPolicy.BEST_EFFORT)


def test_unknown_reliability_is_rejected():
    with pytest.raises(ValueError, match='reliability'):
        subscriber_profile('sensor_data')
