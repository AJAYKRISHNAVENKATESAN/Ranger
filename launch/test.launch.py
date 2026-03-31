import os
import xacro
from launch_ros.actions import Node
from launch import LaunchDescription
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory
from jinja2 import Environment, FileSystemLoader
from launch.actions import DeclareLaunchArgument, RegisterEventHandler, IncludeLaunchDescription, AppendEnvironmentVariable
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution, LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource

# pylint: disable=R0801
def generate_sdf_xml(  # pylint: disable=R0913, R0914, R0917
    package_name,
    output_dir,
    model_name: str,
    obj_filename: str,
    pose_x: float = 0.0,
    pose_y: float = 0.0,
    pose_z: float = 0.0,
    roll: float = 0.0,
    pitch: float = 0.0,
    yaw: float = 0.0,
):

    package_share_dir = get_package_share_directory(package_name)
    template_dir = os.path.join(package_share_dir, "launch", "templates")

    os.makedirs(output_dir, exist_ok=True)

    env = Environment(
        loader=FileSystemLoader(template_dir),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    template = env.get_template("model.sdf.j2")

    output = template.render(
        model_name=model_name,
        obj_filename=obj_filename,
        pose_x=pose_x,
        pose_y=pose_y,
        pose_z=pose_z,
        roll=roll,
        pitch=pitch,
        yaw=yaw,
    )

    output_path = os.path.join(output_dir, "model.sdf")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output)

    return output_path

def generate_launch_description():

    use_sim_time = LaunchConfiguration('use_sim_time')

    pkg_path = os.path.join(get_package_share_directory('bot_description'))
    xacro_file = os.path.join(pkg_path,'urdf','swerve_drive.xacro')
    controllers_file = os.path.join(pkg_path, 'config', 'swerve_controller.yaml')

    robot_description_config = xacro.process_file(xacro_file)
    robot_description_xml = robot_description_config.toxml()

    source_code_path = os.path.abspath(os.path.join(pkg_path, "../../../../src/bot_description"))
    urdf_save_path = os.path.join(source_code_path, "swerve.urdf")
    with open(urdf_save_path, 'w') as f:
        f.write(robot_description_xml)

    bcr_bot_path = get_package_share_directory("bcr_bot")
    # world_file = LaunchConfiguration("world_file", default = os.path.join(bcr_bot_path, "worlds", "small_warehouse.sdf"))
    world_file = os.path.join(bcr_bot_path, "worlds", "small_warehouse.sdf")

    # world_examples_path = get_package_share_directory("world_gazebo_simulator")
    world_examples_path = get_package_share_directory("bot_description")

    set_gz_mesh_path = AppendEnvironmentVariable(
        "GZ_SIM_RESOURCE_PATH", os.path.join(world_examples_path, "models")
    )

    set_gz_world_path = AppendEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=os.path.join(bcr_bot_path, "models"))

    declared_arguments = []
    # declared_arguments.append(set_gz_mesh_path)
    declared_arguments.append(
        DeclareLaunchArgument(
            "gui",
            default_value="true",
            description="Start RViz2 automatically with this launch file.",
        )
    )
    # declared_arguments.append(
    #     DeclareLaunchArgument(
    #         "use_mock_hardware",
    #         default_value="false",
    #         description="Start robot with mock hardware mirroring command to its states.",
    #     )
    # )

    # Initialize Arguments
    gui = LaunchConfiguration("gui")
    use_mock_hardware = LaunchConfiguration("use_mock_hardware")


    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]), " ",
            PathJoinSubstitution([FindPackageShare("bot_description"), "urdf", "swerve_drive.xacro"]), " ",
        ]
    )

    # params = {'robot_description': robot_description_xml, 'use_sim_time': False}

    rviz_config_file = PathJoinSubstitution(
        [FindPackageShare("bot_description"), "config", "robot.rviz"]
    )

    robot_controllers = PathJoinSubstitution(
        [
            FindPackageShare("bot_description"),
            "config",
            "swerve_controller.yaml",
        ]
    )

    control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[robot_controllers],
        output="both",
        # arguments=["--ros-args", "--log-level", "debug"],
        remappings=[
            ("~/robot_description", "/robot_description"),
            # ("/swerve_drive_controller/cmd_vel", "/cmd_vel"),
            # ("/swerve_drive_controller/odom", "/odom"),
        ],
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
    )

    robot_state_pub_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="both",
        parameters=[{"robot_description": robot_description_content, 
                    # 'use_sim_time': use_sim_time
                    }],
    )

    robot_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        # prefix=["gdbserver localhost:3000"],
        arguments=["swerve_drive_controller", "--controller-manager", "/controller_manager"],
    )

    # sdf_file = os.path.join(pkg_path, 'worlds', 'industrial-warehouse.sdf')

    # package_name = "world_gazebo_simulator"
    # output_dir = os.path.join(world_examples_path, "models", "edwards_studio")
    # sdf_file = generate_sdf_xml(
    #     package_name=package_name,
    #     output_dir=output_dir,
    #     model_name="edwards_studio",
    #     obj_filename="edwards_studio.obj",
    #     pose_x=0.0,
    #     pose_y=-35.0,
    #     pose_z=0.0,
    #     roll=0.0,
    #     pitch=0,
    #     yaw=0.0,
    # )

    sdf_file = "empty.sdf"


    gazebo_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch',
                         'gz_sim.launch.py')),
        launch_arguments={'gz_args': '-r ' + world_file}.items(),
    )

    pose = {'x': LaunchConfiguration('x_pose', default='0.00'),
            'y': LaunchConfiguration('y_pose', default='0.00'),
            'z': LaunchConfiguration('z_pose', default='0.1'),
            'R': LaunchConfiguration('roll', default='0.0'),
            'P': LaunchConfiguration('pitch', default='0.00'),
            'Y': LaunchConfiguration('yaw', default='0.00')}

    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=[
            '-entity', 'robot_10x',
            '-topic', '/robot_description',
            '-x', pose['x'], '-y', pose['y'], '-z', pose['z'],
            '-R', pose['R'], '-P', pose['P'], '-Y', pose['Y']],
        parameters=[{'use_sim_time': use_sim_time}]
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="log",
        arguments=["-d", rviz_config_file],
        condition=IfCondition(gui),
    )

    delay_control_node_after_robot_spawn = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_robot,
            on_exit=[control_node],
        )
    )

    delay_control_node_after_robot_state_pub = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=robot_state_pub_node,
            on_exit=[control_node],
        )
)

    delay_robot_controller_after_control_node = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=control_node,
            on_exit=[robot_controller_spawner],
        )
    )

    delay_rviz_after_joint_state_broadcaster_spawner = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[rviz_node],
        )
    )

    delay_joint_state_broadcaster_after_robot_controller_spawner = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=robot_controller_spawner,
            on_exit=[joint_state_broadcaster_spawner],
        )
    )

    ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='bridge_ros_gz',
        parameters=[
            {
                'config_file': os.path.join(
                    pkg_path, 'config', 'gz_bridge.yaml'
                ),
                'use_sim_time': use_sim_time,
            }
        ],
        output='screen',
    )

    nodes = [

        set_gz_mesh_path,
        set_gz_world_path,
        ros_gz_bridge,
        gazebo_sim,
        spawn_robot,     
        robot_state_pub_node,
        # delay_control_node_after_robot_spawn,
        delay_control_node_after_robot_state_pub,
        control_node,
        delay_joint_state_broadcaster_after_robot_controller_spawner,
        robot_controller_spawner,
        # delay_robot_controller_after_control_node,
        delay_rviz_after_joint_state_broadcaster_spawner,

    ]

    return LaunchDescription(declared_arguments + nodes)