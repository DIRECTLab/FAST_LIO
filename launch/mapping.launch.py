import os.path

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.conditions import IfCondition

from launch_ros.actions import Node


def launch_setup(context, *args, **kwargs):
    config_path = LaunchConfiguration('config_path')
    config_file = LaunchConfiguration('config_file')
    use_sim_time = LaunchConfiguration('use_sim_time')
    rviz_use = LaunchConfiguration('rviz')
    rviz_cfg = LaunchConfiguration('rviz_cfg')

    parameters = [PathJoinSubstitution([config_path, config_file]),
                  {'use_sim_time': use_sim_time}]

    # world_frame defaults to '' (unset); only override the config file's
    # value when the user explicitly passes world_frame:=<something>.
    world_frame = LaunchConfiguration('world_frame').perform(context)
    if world_frame:
        parameters.append({'common.world_frame': world_frame})

    fast_lio_node = Node(
        package='fast_lio',
        executable='fastlio_mapping',
        parameters=parameters,
        output='screen'
    )
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_cfg],
        condition=IfCondition(rviz_use)
    )

    return [fast_lio_node, rviz_node]


def generate_launch_description():
    package_path = get_package_share_directory('fast_lio')
    default_config_path = os.path.join(package_path, 'config')
    default_rviz_config_path = os.path.join(
        package_path, 'rviz', 'fastlio.rviz')

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time', default_value='false',
        description='Use simulation (Gazebo) clock if true'
    )
    declare_config_path_cmd = DeclareLaunchArgument(
        'config_path', default_value=default_config_path,
        description='Yaml config file path'
    )
    decalre_config_file_cmd = DeclareLaunchArgument(
        'config_file', default_value='unilidar_l2.yaml',
        description='Config file'
    )
    declare_world_frame_cmd = DeclareLaunchArgument(
        'world_frame', default_value='',
        description='Fixed/world frame id used in tf and published message '
                     'headers. Leave empty to use the value from config_file.'
    )
    declare_rviz_cmd = DeclareLaunchArgument(
        'rviz', default_value='true',
        description='Use RViz to monitor results'
    )
    declare_rviz_config_path_cmd = DeclareLaunchArgument(
        'rviz_cfg', default_value=default_rviz_config_path,
        description='RViz config file path'
    )

    ld = LaunchDescription()
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_config_path_cmd)
    ld.add_action(decalre_config_file_cmd)
    ld.add_action(declare_world_frame_cmd)
    ld.add_action(declare_rviz_cmd)
    ld.add_action(declare_rviz_config_path_cmd)

    ld.add_action(OpaqueFunction(function=launch_setup))

    return ld
