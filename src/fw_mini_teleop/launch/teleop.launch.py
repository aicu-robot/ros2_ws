from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    teleop = Node(
        package='fw_mini_teleop',
        executable='teleop_keyboard',
        name='teleop_keyboard',
        output='screen',
    )

    return LaunchDescription([teleop])
