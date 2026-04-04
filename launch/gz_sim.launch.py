# from launch import LaunchDescription
# from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable, RegisterEventHandler
# from launch_ros.actions import Node
# from launch.substitutions import Command, FindExecutable, PathJoinSubstitution
# from launch_ros.substitutions import FindPackageShare
# from launch.launch_description_sources import PythonLaunchDescriptionSource
# from launch_ros.parameter_descriptions import ParameterValue
# from ament_index_python.packages import get_package_share_directory
# from launch.actions import TimerAction
# from launch.event_handlers import OnProcessExit
# import os


# def generate_launch_description():

#     pkg_name = "ranger"
#     pkg_path = get_package_share_directory(pkg_name)

#     model_path = os.path.join(pkg_path, "urdf", "ranger_new.xacro")
#     controller_yaml_path = os.path.join(pkg_path, "config", "controller.yaml")

#     robot_description = ParameterValue(
#         Command(["xacro ", model_path]),
#         value_type=str
#     )

#     # Start Ignition Gazebo
#     ignition = IncludeLaunchDescription(
#         PythonLaunchDescriptionSource(
#             os.path.join(
#                 get_package_share_directory("ros_gz_sim"),
#                 "launch",
#                 "gz_sim.launch.py"
#             )
#         ),
#         launch_arguments={"gz_args": "-r empty.sdf"}.items(),
#     )

#     # Publish robot state
#     robot_state_publisher = Node(
#         package="robot_state_publisher",
#         executable="robot_state_publisher",
#         parameters=[{"robot_description": robot_description, "use_sim_time": True}],
#         output="screen"
#     )
    
#     # Spawn robot into Ignition
#     spawn_robot = Node(
#         package="ros_gz_sim",
#         executable="create",
#         arguments=[
#             "-topic", "/robot_description",
#             "-entity", "ranger",
#             "-z", "0.2"
#         ],
#         output="screen",
#         parameters=[{"use_sim_time": True}]
#     )

#     joint_state_broadcaster_spawner = Node(
#         package="controller_manager",
#         executable="spawner",
#         arguments=["joint_state_broadcaster", "--controller-manager-timeout", "30"],
#         parameters=[{"use_sim_time": True}]
#     )

#     diff_drive_spawner = Node(
#           package="controller_manager",
#           executable="spawner",
#           arguments=["diff_cont", "--controller-manager-timeout", "30"],
#           parameters=[{"use_sim_time": True}]
#     )

#     # ros_gz_bridge = Node(
#     #     package='ros_gz_bridge',
#     #     executable='parameter_bridge',
#     #     name='bridge_ros_gz',
#     #     parameters=[
#     #         {
#     #             'config_file': os.path.join(
#     #                 pkg_path, 'config', 'gz_bridge.yaml'
#     #             ),
#     #             'use_sim_time': True,
#     #         }
#     #     ],
#     #     output='screen',
#     # )
    
#    # diff_drive only after joint_state_broadcaster is confirmed active
#     delay_diff_drive = RegisterEventHandler(
#         event_handler=OnProcessExit(
#             target_action=joint_state_broadcaster_spawner,
#             on_exit=[diff_drive_spawner]
#         )
#     )

#     # Both spawners fire after spawn_robot exits (robot is in sim)
#     delay_controllers = RegisterEventHandler(
#         event_handler=OnProcessExit(
#             target_action=spawn_robot,
#             on_exit=[joint_state_broadcaster_spawner]
#         )
#     )
   

#     return LaunchDescription([
#         SetEnvironmentVariable(
#             name='IGN_GAZEBO_RESOURCE_PATH',
#             value=os.path.dirname(pkg_path)
#         ),
#         ignition,
#         robot_state_publisher,
#         spawn_robot,
#         delay_controllers,
#         delay_diff_drive,
#     ])


from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    SetEnvironmentVariable,
    RegisterEventHandler,
    TimerAction,
    ExecuteProcess
)
from launch_ros.actions import Node
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
import os


def generate_launch_description():

    pkg_name = "ranger"
    pkg_path = get_package_share_directory(pkg_name)
    model_path = os.path.join(pkg_path, "description", "amr.urdf.xacro")

    robot_description = ParameterValue(
        Command(["xacro ", model_path]),
        value_type=str
    )

    ignition = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("ros_gz_sim"),
                "launch",
                "gz_sim.launch.py"
            )
        ),
        launch_arguments={"gz_args": "-r " + os.path.join(pkg_path, "worlds", "slam_world.sdf")}.items(),
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{
            "robot_description": robot_description,
            "use_sim_time": True
        }],
        output="screen"
    )

    # static_tf = Node(
    #     package="tf2_ros",
    #     executable="static_transform_publisher",
    #     arguments=[
    #         "--frame-id", "base_footprint",
    #         "--child-frame-id", "base_link"
    #     ],
    #     parameters=[{"use_sim_time": True}],
    #     output="screen"
    # )

    # static_tf_lidar = Node(
    #     package="tf2_ros",
    #     executable="static_transform_publisher",
    #     arguments=[
    #         "0.05", "0.0", "0.105",  # xyz — matches lidar_joint origin in URDF
    #         "0", "0", "0",            # rpy
    #         "base_link",              # parent
    #         "lidar_link_1"            # child — matches /scan frame_id
    #     ],
    #     parameters=[{"use_sim_time": True}],
    #     output="screen"
    #)

    gz_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/scan@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan",
            "/scan/points@sensor_msgs/msg/PointCloud2[ignition.msgs.PointCloudPacked",
            "/imu@sensor_msgs/msg/Imu[ignition.msgs.IMU",
            "/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock",
        ],
        parameters=[{"use_sim_time": True}],
        output="screen"
    )

    spawn_robot = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-topic", "/robot_description",
            "-entity", "ranger",
            "-z", "0.2"
        ],
        output="screen",
        parameters=[{"use_sim_time": True}]
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager-timeout", "60"
        ],
        parameters=[{"use_sim_time": True}]
    )

    diff_drive_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "diff_cont",
            "--controller-manager-timeout", "60"
        ],
        parameters=[{"use_sim_time": True}],
        remappings=[
        ("/tf", "/tf_unused"),  # diff_drive doesn't need tf, and this prevents "tf buffer is full" warnings
        ]
    )

    # Wait 3s after spawn exits, then launch JSB
    delay_joint_state_broadcaster = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_robot,
            on_exit=[
                TimerAction(
                    period=5.0,   # gz_ros2_control needs a moment after spawn
                    actions=[joint_state_broadcaster_spawner]
                )
            ]
        )
    )

    # diff_drive only after JSB succeeds
    delay_diff_drive = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[diff_drive_spawner]
        )
    )

    ekf_node =Node(
                package="robot_localization",
                executable="ekf_node",
                name="ekf_filter_node",
                parameters=[
                    os.path.join(pkg_path, "config", "ekf.yaml"),
                    {"use_sim_time": True}
                ],
                output="screen"
    )

    delay_ekf = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=diff_drive_spawner,
            on_exit=[
                TimerAction(
                    period=2.0,
                    actions=[ekf_node]
                )
            ]
        )
    )
    
    # slam = Node(
    # package="slam_toolbox",
    # executable="async_slam_toolbox_node",
    # name="slam_toolbox",
    # parameters=[
    #     os.path.join(pkg_path, "config", "mapper_params_online_async.yaml"),
    #     {"use_sim_time": True}
    # ],
    # output="screen"
    # )

    # imu_bridge = Node(
    # package="ros_gz_bridge",
    # executable="parameter_bridge",
    # arguments=[
    #     "/imu@sensor_msgs/msg/Imu[ignition.msgs.IMU",
    # ],
    # parameters=[{"use_sim_time": True}],  # ← wall time for bridge
    # output="screen"
    # )

    delay_slam = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=diff_drive_spawner,
            on_exit=[
                TimerAction(
                    period=5.0,   # let odometry settle first
                    actions=[
                        Node(
                            package="slam_toolbox",
                            executable="async_slam_toolbox_node",
                            name="slam_toolbox",
                            parameters=[
                                os.path.join(pkg_path, "config",
                                    "mapper_params_online_async.yaml"),
                                {"use_sim_time": True}
                            ],
                            output="screen"
                        )
                    ]
                )
            ]
        )
    )

    # ekf_node = Node(
    #     package="robot_localization",
    #     executable="ekf_node",
    #     name="ekf_filter_node",
    #     parameters=[
    #         os.path.join(pkg_path, "config", "ekf.yaml"),
    #         {"use_sim_time": True,
    #         #  "publish_tf": True,
    #         #  "world_frame": "odom",
    #         }
    #     ],
    #     output="screen"
    # )

    # delay_ekf = TimerAction(
    # period=10.0,    # wait for Gazebo clock to stabilize
    #     actions=[
    #         Node(
    #             package="robot_localization",
    #             executable="ekf_node",
    #             name="ekf_filter_node",
    #             parameters=[
    #                 os.path.join(pkg_path, "config", "ekf.yaml"),
    #                 {"use_sim_time": True}
    #             ],
    #             output="screen"
    #         )
    #     ]
    # )

    # clock_bridge = Node(
    # package="ros_gz_bridge",
    # executable="parameter_bridge",
    # arguments=[
    #     "/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock"
    # ],
    # parameters=[{"use_sim_time": False}],  # clock bridge itself uses wall time
    # output="screen"
    # )


    # delay_rviz = RegisterEventHandler(
    #     event_handler=OnProcessExit(
    #         target_action=diff_drive_spawner,
    #         on_exit=[                          # ← same level as target_action
    #             TimerAction(
    #                 period=2.0,
    #                 actions=[
    #                     Node(
    #                         package="rviz2",
    #                         executable="rviz2",
    #                         arguments=[
    #                             "-d", os.path.join(pkg_path, "rviz", "slam.rviz")
    #                         ],
    #                         parameters=[{"use_sim_time": True}],
    #                         output="screen"
    #                     )
    #                 ]
    #             )
    #         ]
    #     )
    # )

    # disable_diff_tf = RegisterEventHandler(
    #     event_handler=OnProcessExit(
    #         target_action=diff_drive_spawner,
    #         on_exit=[
    #             TimerAction(
    #                 period=2.0,
    #                 actions=[
    #                     ExecuteProcess(
    #                         cmd=["ros2", "param", "set",
    #                             "/diff_cont", "publish_odom_tf", "false"],
    #                         output="screen"
    #                     )
    #                 ]
    #             )
    #         ]
    #     )
    # )


    return LaunchDescription([
        SetEnvironmentVariable(
            name='IGN_GAZEBO_RESOURCE_PATH',
            value=os.path.dirname(pkg_path)
        ),
        SetEnvironmentVariable(                         
        name='IGN_GAZEBO_SYSTEM_PLUGIN_PATH',
        value='/opt/ros/humble/lib'
        ),
        ignition,
        robot_state_publisher,
        gz_bridge,
        spawn_robot,
        delay_joint_state_broadcaster,
        delay_diff_drive,
        delay_ekf,
        delay_slam,
    ])




