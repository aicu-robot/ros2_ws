import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():

    desc_pkg  = get_package_share_directory('fw_mini_description')
    gz_pkg    = get_package_share_directory('fw_mini_gazebo')
    gazebo_ros_pkg = get_package_share_directory('gazebo_ros')

    # Gazebo가 package:// URI로 메시를 찾을 수 있도록 경로 설정
    gazebo_model_path = SetEnvironmentVariable(
        name='GAZEBO_MODEL_PATH',
        value=os.path.join(os.path.dirname(desc_pkg), '..') + ':' +
              os.environ.get('GAZEBO_MODEL_PATH', '')
    )

    # -----------------------------------------------
    # Launch Arguments
    # -----------------------------------------------
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    world_file = LaunchConfiguration(
        'world',
        default=os.path.join(gz_pkg, 'worlds', 'fw_mini_world.world')
    )
    x_pose = LaunchConfiguration('x_pose', default='0.0')
    y_pose = LaunchConfiguration('y_pose', default='0.0')
    z_pose = LaunchConfiguration('z_pose', default='0.15')

    # -----------------------------------------------
    # Gazebo 실행
    # -----------------------------------------------
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_ros_pkg, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={'world': world_file, 'verbose': 'false'}.items(),
    )

    # -----------------------------------------------
    # robot_description: xacro 처리
    # -----------------------------------------------
    urdf_file = os.path.join(desc_pkg, 'urdf', 'fw_mini.urdf.xacro')
    robot_description = ParameterValue(
        Command(['xacro ', urdf_file]),
        value_type=str
    )

    # -----------------------------------------------
    # robot_state_publisher
    # -----------------------------------------------
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': robot_description,
        }]
    )

    # -----------------------------------------------
    # Gazebo에 로봇 스폰
    # -----------------------------------------------
    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_fw_mini',
        output='screen',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'fw_mini',
            '-x', x_pose,
            '-y', y_pose,
            '-z', z_pose,
        ]
    )

    return LaunchDescription([
        gazebo_model_path,
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument(
            'world',
            default_value=os.path.join(gz_pkg, 'worlds', 'fw_mini_world.world')
        ),
        DeclareLaunchArgument('x_pose', default_value='0.0'),
        DeclareLaunchArgument('y_pose', default_value='0.0'),
        DeclareLaunchArgument('z_pose', default_value='0.15'),

        gazebo,
        robot_state_publisher,
        spawn_robot,
    ])
