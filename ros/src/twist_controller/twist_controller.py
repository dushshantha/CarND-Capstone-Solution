from yaw_controller import YawController
from lowpass import LowPassFilter
from pid import PID
import rospy
import math
import csv

GAS_DENSITY = 2.858
ONE_MPH = 0.44704
M = 0.09949492
B = -0.05454824

class Controller(object):
    def __init__(self, dbw_enabled,
                vehicle_mass, fuel_capacity,
                brake_deadband, decel_limit,
                accel_limit, wheel_radius,
                wheel_base, steer_ratio,
                max_lat_accel, max_steer_angle):
        self.vehicle_mass = vehicle_mass
        self.fuel_capacity = fuel_capacity
        self.brake_deadband = brake_deadband
        self.decel_limit = -decel_limit
        self.accel_limit = accel_limit
        self.wheel_radius = wheel_radius
        #self.wheel_base = wheel_base
        #self.steer_ratio = steer_ratio
        #self.max_lat_accel = max_lat_accel
        #self.max_steer_angle = max_steer_angle

        min_speed = 0.0
        self.yaw_controller = YawController(wheel_base, steer_ratio,
                                            min_speed, max_lat_accel,
                                            max_steer_angle)
        self.lowpass = LowPassFilter(3, 1)

        kp = 0.5
        ki = 0.0
        kd = 0.4
        self.pid_throttle = PID(kp, ki, kd, mn=0, mx=accel_limit)

        kp_s = 15.0
        ki_s = 0.0
        kd_s = 0.3
        self.pid_steer = PID(kp_s, ki_s, kd_s, mn = -max_steer_angle, mx = max_steer_angle)

        self.steer_data = []

    def control(self, dbw_enabled, goal_linear_v, goal_angular_v, stop_a, current_linear_v, current_angular_v, dt):
        if not dbw_enabled:
            self.pid_throttle.reset()

        else:
            error = goal_linear_v - current_linear_v
            throttle = self.pid_throttle.step(error, dt)

            if stop_a > self.brake_deadband:
                a_add_on = self.accel_add_on(current_linear_v)
                stop_a -= a_add_on
                brake = max(0, stop_a)*self.vehicle_mass*self.wheel_radius
            else:
                brake = 0

            error_a = goal_angular_v - current_angular_v; 
            steer = self.lowpass.filt(self.pid_steer.step(error_a, dt))
            #steer = self.yaw_controller.get_steering(goal_linear_v,
            #                                         goal_angular_v,
            #                                         current_linear_v)

        return throttle, brake, steer


    def accel_add_on(self, current_linear_v):
        # M and B were calculated by fitting a polynomial to data collected
        # by speeding ego up to high speed and then tracking delta v and dt
        # when applying no throttle or brake. On flat ground, the car in the simulator
        # decelerates linearly with respect to speed with no throttle or speed.
        return M*current_linear_v + B
