#!/usr/bin/env python3
"""
FW-Mini WASD Keyboard Teleoperation
동시 키 입력 지원 (W+A, W+D, S+A, S+D)

키 조작:
  W     : 전진
  S     : 후진
  A     : 좌회전
  D     : 우회전
  W + A : 전진 + 좌회전
  W + D : 전진 + 우회전
  S + A : 후진 + 좌회전
  S + D : 후진 + 우회전
  Q / E : 선속도 증가 / 감소
  Z / C : 각속도 증가 / 감소
  Space : 정지
  ESC   : 종료
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from pynput import keyboard


LINEAR_STEP  = 0.05
ANGULAR_STEP = 0.1
MAX_LINEAR   = 1.0
MAX_ANGULAR  = 2.0


class TeleopKeyboard(Node):

    def __init__(self):
        super().__init__('fw_mini_teleop_keyboard')

        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.timer = self.create_timer(0.02, self.publish_cmd)  # 50 Hz

        self.pressed = set()
        self.linear_speed  = 0.3
        self.angular_speed = 0.8

        self._print_usage()

        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()

    def _print_usage(self):
        print('\n' + '='*45)
        print('  FW-Mini WASD Teleop (동시 키 입력 지원)')
        print('='*45)
        print('  W / S     : 전진 / 후진')
        print('  A / D     : 좌회전 / 우회전')
        print('  W+A / W+D : 전진+좌회전 / 전진+우회전')
        print('  S+A / S+D : 후진+좌회전 / 후진+우회전')
        print('  Q / E     : 선속도 증가 / 감소')
        print('  Z / C     : 각속도 증가 / 감소')
        print('  Space     : 정지')
        print('  ESC       : 종료')
        print('='*45)
        print(f'  선속도: {self.linear_speed:.2f} m/s  |  각속도: {self.angular_speed:.2f} rad/s')
        print('='*45 + '\n')

    def _on_press(self, key):
        try:
            c = key.char.lower()
            if c == 'q':
                self.linear_speed = round(min(self.linear_speed + 0.1, MAX_LINEAR), 2)
                print(f'\n  선속도: {self.linear_speed:.2f} m/s  |  각속도: {self.angular_speed:.2f} rad/s', flush=True)
            elif c == 'e':
                self.linear_speed = round(max(self.linear_speed - 0.1, 0.05), 2)
                print(f'\n  선속도: {self.linear_speed:.2f} m/s  |  각속도: {self.angular_speed:.2f} rad/s', flush=True)
            elif c == 'z':
                self.angular_speed = round(min(self.angular_speed + 0.1, MAX_ANGULAR), 2)
                print(f'\n  선속도: {self.linear_speed:.2f} m/s  |  각속도: {self.angular_speed:.2f} rad/s', flush=True)
            elif c == 'c':
                self.angular_speed = round(max(self.angular_speed - 0.1, 0.1), 2)
                print(f'\n  선속도: {self.linear_speed:.2f} m/s  |  각속도: {self.angular_speed:.2f} rad/s', flush=True)
            else:
                self.pressed.add(c)
        except AttributeError:
            self.pressed.add(key)

    def _on_release(self, key):
        try:
            self.pressed.discard(key.char.lower())
        except AttributeError:
            self.pressed.discard(key)

        # ESC 종료
        if key == keyboard.Key.esc:
            self.get_logger().info('종료합니다.')
            rclpy.shutdown()

    def publish_cmd(self):
        p = self.pressed
        twist = Twist()

        # 전진 / 후진
        if 'w' in p:
            twist.linear.x = self.linear_speed
        elif 's' in p:
            twist.linear.x = -self.linear_speed

        # 좌회전 / 우회전
        if 'a' in p:
            twist.angular.z = self.angular_speed
        elif 'd' in p:
            twist.angular.z = -self.angular_speed

        # 정지
        if keyboard.Key.space in p:
            twist.linear.x  = 0.0
            twist.angular.z = 0.0

        self.pub.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = TeleopKeyboard()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        stop = Twist()
        node.pub.publish(stop)
        node.listener.stop()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
