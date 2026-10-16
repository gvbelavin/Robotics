import os
from types import SimpleNamespace

from patrol.parameters import validate_values, values_with_update
from patrol.patrol import Patrol
import pytest
import rclpy
from rclpy.parameter import Parameter


CURRENT = (0.5, 0.3, 10.0)


def test_frequency_change_from_10_to_5_is_accepted():
    linear_speed, turn_rate, publish_hz = values_with_update(
        CURRENT[0], CURRENT[1], CURRENT[2], {'publish_hz': 5.0})
    assert (linear_speed, turn_rate) == (0.5, 0.3)
    assert validate_values(linear_speed, turn_rate, publish_hz) == (True, '')


def test_zero_negative_and_nan_frequency_are_rejected():
    for bad in (0.0, -1.0, float('nan'), float('inf'), float('-inf')):
        linear_speed, turn_rate, publish_hz = values_with_update(
            CURRENT[0], CURRENT[1], CURRENT[2], {'publish_hz': bad})
        ok, reason = validate_values(linear_speed, turn_rate, publish_hz)
        assert ok is False
        assert reason
        assert linear_speed == 0.5
        assert turn_rate == 0.3


def test_speed_and_turn_stay_inside_finite_ranges():
    assert validate_values(0.0, -1.0, 1.0) == (True, '')
    assert validate_values(1.0, 1.0, 30.0) == (True, '')
    assert validate_values(1.1, 0.3, 10.0)[0] is False
    assert validate_values(0.5, -1.1, 10.0)[0] is False
    assert validate_values(float('nan'), 0.3, 10.0)[0] is False
    assert validate_values('fast', 0.3, 10.0)[0] is False


@pytest.fixture(scope='module')
def ros_context():
    os.environ['ROS_DOMAIN_ID'] = '85'
    os.environ['ROS_AUTOMATIC_DISCOVERY_RANGE'] = 'LOCALHOST'
    rclpy.init()
    yield
    rclpy.try_shutdown()


@pytest.fixture
def patrol_node(ros_context):
    node = Patrol()
    yield node
    node.destroy_node()


def test_invalid_start_does_not_create_timer(monkeypatch, ros_context):
    created = []
    real_create_timer = Patrol.create_timer

    def wrapped(self, *args, **kwargs):
        created.append(args)
        return real_create_timer(self, *args, **kwargs)

    monkeypatch.setattr(Patrol, 'create_timer', wrapped)
    with pytest.raises(ValueError, match='publish_hz'):
        Patrol(parameter_overrides=[
            Parameter('publish_hz', Parameter.Type.DOUBLE, 0.0),
        ])
    assert created == []


def test_rejected_frequency_keeps_timer_and_value(patrol_node):
    previous = patrol_node.timer
    for bad in (0.0, -2.0, float('nan')):
        result = patrol_node.set_parameters([
            Parameter('publish_hz', Parameter.Type.DOUBLE, bad),
        ])
        assert result[0].successful is False
        assert patrol_node.timer is previous
        assert patrol_node.publish_hz == 10.0
        assert patrol_node.get_parameter('publish_hz').value == 10.0
        assert list(patrol_node.timers) == [previous]


def test_accepted_frequency_replaces_the_only_timer(patrol_node):
    previous = patrol_node.timer
    result = patrol_node.set_parameters([
        Parameter('publish_hz', Parameter.Type.DOUBLE, 5.0),
    ])
    assert result[0].successful is True
    assert patrol_node.publish_hz == 5.0
    assert patrol_node.get_parameter('publish_hz').value == 5.0
    assert patrol_node.timer is not previous
    assert list(patrol_node.timers) == [patrol_node.timer]
    assert patrol_node.timer.timer_period_ns == int(float(1.0 / 5.0) * 1e9)


def test_same_frequency_does_not_replace_timer(patrol_node):
    previous = patrol_node.timer
    result = patrol_node.set_parameters([
        Parameter('publish_hz', Parameter.Type.DOUBLE, 10.0),
    ])
    assert result[0].successful is True
    assert patrol_node.timer is previous


def test_speed_parameter_controls_command_without_new_timer(patrol_node):
    previous = patrol_node.timer
    result = patrol_node.set_parameters([
        Parameter('linear_speed', Parameter.Type.DOUBLE, 0.8),
        Parameter('turn_rate', Parameter.Type.DOUBLE, -0.4),
    ])
    assert [item.successful for item in result] == [True, True]
    assert patrol_node.timer is previous
    patrol_node.latest_pose = SimpleNamespace(x=1.0, y=2.0, theta=0.0)
    command = patrol_node.command_twist()
    assert command.linear.x == pytest.approx(0.8)
    assert command.angular.z == pytest.approx(-0.4)


def test_rejected_speed_does_not_change_active_command(patrol_node):
    result = patrol_node.set_parameters([
        Parameter('linear_speed', Parameter.Type.DOUBLE, 2.0),
    ])
    assert result[0].successful is False
    assert patrol_node.linear_speed == 0.5
    patrol_node.latest_pose = SimpleNamespace(x=1.0, y=2.0, theta=0.0)
    command = patrol_node.command_twist()
    assert command.linear.x == pytest.approx(0.5)
    assert command.angular.z == pytest.approx(0.3)
