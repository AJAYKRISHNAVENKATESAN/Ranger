# def_bot — ROS2 Differential Drive Robot with SLAM

A ROS2 Humble differential drive robot simulated in Ignition Gazebo Fortress
with LiDAR-based SLAM mapping.

## Stack
- ROS2 Humble
- Ignition Gazebo Fortress
- slam_toolbox
- robot_localization (EKF)
- Nav2 (in progress)

## Structure
- urdf/ — Robot URDF/xacro
- launch/ — Launch files
- config/ — Controllers, EKF, SLAM config
- worlds/ — Gazebo SDF worlds
- meshes/ — 3D mesh files
- rviz/ — RViz config
- maps/ — Saved SLAM maps

## Launch
```bash
ros2 launch def_bot gz_sim.launch.py
```
