from types import SimpleNamespace

from patrol.command import command_from_pose


def test_missing_pose_publishes_zero_command():
    assert command_from_pose(None) == (0.0, 0.0)
    assert command_from_pose(None, linear_x=0.5, angular_z=0.3) == (0.0, 0.0)


def test_pose_message_selects_forward_and_turn():
    pose = SimpleNamespace(x=5.544445, y=5.544445, theta=0.0)
    assert command_from_pose(pose) == (0.5, 0.3)


def test_command_is_limited():
    pose = SimpleNamespace(x=1.0, y=2.0, theta=0.4)
    assert command_from_pose(pose, linear_x=2.0, angular_z=3.0) == (1.0, 1.0)
    assert command_from_pose(pose, linear_x=-0.2, angular_z=-4.0) == (0.0, -1.0)
