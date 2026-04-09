import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess, DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
import yaml

# helper function to launch multiple controller servers
def launch_servers(config: dict):
    robot_actions = []

    for k,v in config.items():
        # launch description for 1 action server
        action_server = IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                os.path.join(get_package_share_directory('andino_fleet'), 'launch'),
                '/andino_controller.launch.py'
            ])
        )
        robot_actions.append(action_server)

    return robot_actions

# helper function to convert dictionary to string for parsing to execution process
def convert_to_text(data: dict):
    text = '\"'
    for k,v in data.items():
        robot_data = str(k) + '=' + str(v) + ';'
        text += robot_data
    text += '\"'
    return text

def launch_setup(context, *args, **kwargs):
    # 1. Retrieve the actual values of the 'id' and 'rviz' arguments
    robot_id = LaunchConfiguration('id').perform(context)
    rviz_enabled = LaunchConfiguration('rviz').perform(context)
    
    target_robot = f'andino{robot_id}'

    # 2. Load the full YAML config
    config_name = 'spawn_robots.yaml'
    config_file_path = os.path.join(get_package_share_directory('andino_fleet'), 'config', config_name)
    with open(config_file_path, 'r') as f:
        full_config = yaml.load(f, Loader=yaml.SafeLoader)
    
    # 3. Filter the config to ONLY include the target robot
    if target_robot not in full_config:
        raise ValueError(f"Robot '{target_robot}' not found in {config_file_path}")
    
    filtered_config = {target_robot: full_config[target_robot]}

    # 4. Convert dictionary to text for the spawning argument
    config_txt = convert_to_text(filtered_config)
    
    # 5. Execute andino simulation with dynamic rviz flag
    robots = ExecuteProcess(
        cmd=[[
            'ros2 launch andino_gz andino_gz.launch.py ',
            'nav2:=', 'True ',
            'robots:=', config_txt, ' ',
            'world_name:=', 'office.sdf ',
            'map:=', 'office ',
            'rviz:=', f'{rviz_enabled}', # Dynamically inject the rviz argument here
        ]],
        shell=True
    )
    
    # 6. Launch action servers (only for the filtered robot)
    controller_servers = launch_servers(config=filtered_config)

    # Return the actions to be executed
    actions = [robots]
    actions.extend(controller_servers)
    return actions

def generate_launch_description():
    # Declare the 'id' argument
    id_arg = DeclareLaunchArgument(
        'id',
        default_value='1',
        description='The ID of the robot to spawn (e.g., 1 for andino1, 2 for andino2)'
    )
    
    # Declare the 'rviz' argument
    rviz_arg = DeclareLaunchArgument(
        'rviz',
        default_value='True',
        description='Whether to launch RViz (True or False)'
    )

    ld = LaunchDescription()
    ld.add_action(id_arg)
    ld.add_action(rviz_arg)
    
    # Use OpaqueFunction to evaluate the logic at runtime
    ld.add_action(OpaqueFunction(function=launch_setup))
    
    return ld