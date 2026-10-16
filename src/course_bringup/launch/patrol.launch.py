"""Поднять turtlesim, patrol и сенсорный поток одной командой."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, LogInfo
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """Собрать аргументы, ноды, переназначения и условную запись MCAP."""
    namespace = LaunchConfiguration('namespace')
    record = LaunchConfiguration('record')
    bag_dir = LaunchConfiguration('bag_dir')
    subscriber_reliability = LaunchConfiguration('subscriber_reliability')
    log_level = LaunchConfiguration('log_level')
    sensor_topic = ['/', namespace, '/sensor_pose']

    return LaunchDescription([
        DeclareLaunchArgument(
            'namespace',
            default_value='robot_a',
            description='Пространство имён patrol и сенсорного потока.',
        ),
        DeclareLaunchArgument(
            'record',
            default_value='false',
            description='Писать /<namespace>/sensor_pose в MCAP, если true.',
        ),
        DeclareLaunchArgument(
            'bag_dir',
            default_value='bag',
            description='Каталог ros2 bag record.',
        ),
        DeclareLaunchArgument(
            'subscriber_reliability',
            default_value='best_effort',
            description='QoS подписчика sensor_pose: best_effort или reliable.',
        ),
        DeclareLaunchArgument(
            'log_level',
            default_value='info',
            description='Уровень логов нод.',
        ),
        LogInfo(msg=[
            'course_bringup namespace=', namespace,
            ' record=', record,
            ' bag_dir=', bag_dir,
            ' subscriber_reliability=', subscriber_reliability,
        ]),
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='turtlesim',
            output='screen',
            ros_arguments=['--log-level', log_level],
        ),
        Node(
            package='patrol',
            executable='patrol',
            namespace=namespace,
            output='screen',
            ros_arguments=['--log-level', log_level],
            remappings=[
                ('cmd_vel', '/turtle1/cmd_vel'),
                ('turtle1/pose', '/turtle1/pose'),
            ],
        ),
        Node(
            package='course_bringup',
            executable='pose_relay',
            namespace=namespace,
            output='screen',
            ros_arguments=['--log-level', log_level],
            remappings=[
                ('turtle1/pose', '/turtle1/pose'),
            ],
        ),
        Node(
            package='course_bringup',
            executable='pose_subscriber',
            namespace=namespace,
            output='screen',
            ros_arguments=['--log-level', log_level],
            parameters=[{
                'reliability': subscriber_reliability,
            }],
        ),
        ExecuteProcess(
            cmd=[
                'ros2', 'bag', 'record',
                '-s', 'mcap',
                '-o', bag_dir,
                '--topics', sensor_topic,
                '--disable-keyboard-controls',
                '--log-level', log_level,
            ],
            condition=IfCondition(record),
            output='screen',
            log_cmd=True,
        ),
    ])
