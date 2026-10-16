"""Состав patrol.launch.py: аргументы, remap и IfCondition."""

import importlib.util
from pathlib import Path

from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch_ros.actions import Node


LAUNCH_PATH = Path(__file__).resolve().parents[1] / 'launch' / 'patrol.launch.py'


def load_description():
    spec = importlib.util.spec_from_file_location('patrol_launch', LAUNCH_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.generate_launch_description()


def test_launch_declares_required_arguments():
    description = load_description()
    names = [
        action.name for action in description.entities
        if isinstance(action, DeclareLaunchArgument)
    ]
    assert names == [
        'namespace',
        'record',
        'bag_dir',
        'subscriber_reliability',
        'log_level',
    ]


def substitution_text(value):
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple)):
        return ''.join(substitution_text(item) for item in value)
    text = getattr(value, 'text', None)
    if isinstance(text, str):
        return text
    return ''


def test_recorder_starts_only_under_if_condition():
    source = LAUNCH_PATH.read_text(encoding='utf-8')
    assert 'IfCondition' in source
    assert 'if LaunchConfiguration' not in source
    assert 'if record' not in source
    description = load_description()
    recorders = [
        action for action in description.entities
        if action.__class__.__name__ == 'ExecuteProcess'
    ]
    assert len(recorders) == 1
    assert isinstance(recorders[0].condition, IfCondition)
    command = ' '.join(substitution_text(part) for part in recorders[0].cmd)
    assert 'ros2' in command
    assert 'mcap' in command
    assert 'sensor_pose' in command


def test_command_and_pose_are_remapped_outside_the_namespace():
    source = LAUNCH_PATH.read_text(encoding='utf-8')
    assert "('cmd_vel', '/turtle1/cmd_vel')" in source
    assert source.count("('turtle1/pose', '/turtle1/pose')") == 2
    description = load_description()
    nodes = [
        action for action in description.entities
        if isinstance(action, Node)
    ]
    by_executable = {action.node_executable: action for action in nodes}
    assert set(by_executable) == {
        'turtlesim_node', 'patrol', 'pose_relay', 'pose_subscriber',
    }
    assert by_executable['turtlesim_node'].node_package == 'turtlesim'
    assert by_executable['patrol'].node_package == 'patrol'
    assert by_executable['pose_relay'].node_package == 'course_bringup'
    assert by_executable['pose_subscriber'].node_package == 'course_bringup'
