from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

    pkg_name = "ranger"
    pkg_path = get_package_share_directory(pkg_name)

    model_path = os.path.join(pkg_path, "description", "amr.urdf.xacro")
    # rviz_config_path = os.path.join(pkg_path, "rviz", "config_finall.rviz") #Used to visulize the robot in RViz in the saved configuration(only use if you have a rviz config file or comment this line and the rviz node in the return statement)

    robot_description = ParameterValue(
        Command(["xacro ", model_path]),
        value_type=str
    )

    return LaunchDescription([

        DeclareLaunchArgument(
            "gui",
            
            default_value="true"
        ),

        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            parameters=[{"robot_description": robot_description}]
        ),

        Node(
            package="joint_state_publisher_gui",
            executable="joint_state_publisher_gui",
            condition=None
        ),

        Node(     
           package="rviz2",
           executable="rviz2",
          # arguments=["-d", rviz_config_path],  
           output="screen"
        )
    ])