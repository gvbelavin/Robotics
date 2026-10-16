"""Launch в /robot_a завершает свои процессы по SIGINT."""

import os
import signal
import subprocess
import time


def ros_env():
    env = os.environ.copy()
    env['ROS_DOMAIN_ID'] = '93'
    env['ROS_AUTOMATIC_DISCOVERY_RANGE'] = 'LOCALHOST'
    return env


def run_ros(args, env, timeout=12):
    return subprocess.run(
        args,
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def test_launch_isolates_namespace_and_exits(tmp_path):
    env = ros_env()
    bag_dir = tmp_path / 'bag'
    log_path = tmp_path / 'launch.txt'
    log_handle = log_path.open('w', encoding='utf-8')
    proc = subprocess.Popen(
        [
            'ros2', 'launch', 'course_bringup', 'patrol.launch.py',
            'namespace:=robot_a',
            'subscriber_reliability:=best_effort',
            'record:=false',
            'bag_dir:=%s' % bag_dir,
        ],
        env=env,
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )
    topics = ''
    nodes = ''
    try:
        deadline = time.monotonic() + 25
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                log_handle.close()
                raise AssertionError(
                    'launch завершился раньше с кодом %s\n%s' % (
                        proc.returncode, log_path.read_text(encoding='utf-8')))
            listed = run_ros(
                ['ros2', 'topic', 'list', '--no-daemon', '--spin-time', '1'],
                env,
            )
            topics = listed.stdout
            if '/robot_a/sensor_pose' in topics and '/turtle1/pose' in topics:
                nodes = run_ros(
                    ['ros2', 'node', 'list', '--no-daemon', '--spin-time', '2'],
                    env,
                ).stdout
                if '/robot_a/pose_subscriber' in nodes:
                    break
            time.sleep(0.4)
        else:
            log_handle.close()
            raise AssertionError(
                'граф не собрался\n%s\n%s\n%s' % (
                    topics, nodes, log_path.read_text(encoding='utf-8')))
        topic_names = topics.split()
        assert '/robot_a/sensor_pose' in topic_names
        assert '/turtle1/cmd_vel' in topic_names
        assert '/robot_a/cmd_vel' not in topic_names
        assert '/robot_a/turtle1/pose' not in topic_names
        assert '/turtlesim' in nodes
        assert '/robot_a/patrol' in nodes
        assert '/robot_a/pose_relay' in nodes
        assert '/robot_a/turtlesim' not in nodes
        assert not bag_dir.exists()
    finally:
        if not log_handle.closed:
            log_handle.close()
        if proc.poll() is None:
            proc.send_signal(signal.SIGINT)
            try:
                proc.wait(timeout=20)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait(timeout=5)
    assert proc.returncode == 0, log_path.read_text(encoding='utf-8')
    leftover = run_ros(
        ['ros2', 'node', 'list', '--no-daemon', '--spin-time', '2'],
        env,
    ).stdout
    assert '/turtlesim' not in leftover
    assert '/robot_a/patrol' not in leftover
    assert '/robot_a/pose_relay' not in leftover
