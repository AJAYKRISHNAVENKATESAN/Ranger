# ranger — ROS 2 Humble + Gazebo Fortress (Ignition) development environment
# Diff-drive AMR (2 drive wheels + castor): ros2_control diff_drive_controller,
# robot_localization EKF, and slam_toolbox for indoor SLAM. The launch files bridge
# ignition.msgs types and point IGN_GAZEBO_SYSTEM_PLUGIN_PATH at /opt/ros/humble/lib,
# so this stays on Humble + Fortress rather than the repo-wide Jazzy default.
FROM osrf/ros:humble-desktop-full

ENV DEBIAN_FRONTEND=noninteractive
ENV ROS_DISTRO=humble
ENV WORKSPACE_ROOT=/workspace
ENV RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

RUN apt-get update && apt-get install -y \
    build-essential cmake git wget curl unzip \
    python3-pip python3-colcon-common-extensions \
    ros-${ROS_DISTRO}-rmw-cyclonedds-cpp \
    # Ignition Fortress integration + ros2_control bridge
    ros-${ROS_DISTRO}-ros-gz \
    ros-${ROS_DISTRO}-ign-ros2-control \
    # ros2_control (diff_drive_controller, joint_state_broadcaster)
    ros-${ROS_DISTRO}-ros2-control \
    ros-${ROS_DISTRO}-ros2-controllers \
    ros-${ROS_DISTRO}-controller-manager \
    # EKF localization + SLAM
    ros-${ROS_DISTRO}-robot-localization \
    ros-${ROS_DISTRO}-slam-toolbox \
    # description / utilities
    ros-${ROS_DISTRO}-xacro \
    ros-${ROS_DISTRO}-joint-state-publisher-gui \
    vim nano tmux htop mesa-utils dos2unix \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p ${WORKSPACE_ROOT}/src

RUN echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> ~/.bashrc && \
    echo "source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash" >> ~/.bashrc && \
    echo "alias cb='cd ${WORKSPACE_ROOT} && colcon build --symlink-install'" >> ~/.bashrc && \
    echo "alias cs='source ${WORKSPACE_ROOT}/install/setup.bash'" >> ~/.bashrc && \
    echo "alias ws='cd ${WORKSPACE_ROOT}'" >> ~/.bashrc

WORKDIR ${WORKSPACE_ROOT}
COPY docker/entrypoint.sh /entrypoint.sh
RUN dos2unix /entrypoint.sh && chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
