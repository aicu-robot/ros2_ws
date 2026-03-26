cmake_minimum_required(VERSION 3.8)
project(fw_mini_gazebo)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY launch worlds config
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
