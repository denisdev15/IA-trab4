import sys
from robot import Robot
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt
import time
import angles
import math

# Antecedents objects
direction = ctrl.Antecedent(np.arange(-math.pi, math.pi, 0.01), 'direction')
direction['error_left'] = fuzz.trimf(direction.universe, [-math.pi, -math.pi, 0])
direction['error_right'] = fuzz.trimf(direction.universe, [0, math.pi, math.pi])
direction['no_error'] = fuzz.trimf(direction.universe, [-0.2, 0, 0.2])

goal_distance = ctrl.Antecedent(np.arange(0, 500, 0.01), 'goal_distance')
goal_distance['perto'] = fuzz.trimf(goal_distance.universe, [0, 0, 0.2])
goal_distance['longe'] = fuzz.trapmf(goal_distance.universe, [0.2, 1, 500, 500])

vel_left = ctrl.Consequent(np.arange(-4, 4, 0.1), 'vel_left')
vel_right = ctrl.Consequent(np.arange(-4, 4, 0.1), 'vel_right')

vel_left['pos'] = fuzz.trimf(vel_left.universe, [0, math.pi, math.pi])
vel_left['neg'] = fuzz.trimf(vel_left.universe, [-math.pi, -math.pi, 0])
vel_right['pos'] = fuzz.trimf(vel_left.universe, [0, math.pi, math.pi])
vel_right['neg'] = fuzz.trimf(vel_left.universe, [-math.pi, -math.pi, 0])

rule1 = ctrl.Rule(direction['error_left'] & goal_distance['longe'], vel_left['neg'])
rule2 = ctrl.Rule(direction['error_left'] & goal_distance['longe'], vel_right['pos'])
rule3 = ctrl.Rule(direction['error_right'] & goal_distance['longe'], vel_right['neg'])
rule4 = ctrl.Rule(direction['error_right'] & goal_distance['longe'], vel_left['pos'])
rule5 = ctrl.Rule(direction['no_error'] & goal_distance['longe'], vel_left['pos'])
rule6 = ctrl.Rule(direction['no_error'] & goal_distance['longe'], vel_right['pos'])
rule7 = ctrl.Rule(goal_distance['perto'], vel_right['pos'])
rule8 = ctrl.Rule(goal_distance['perto'], vel_right['neg'])
rule9 = ctrl.Rule(goal_distance['perto'], vel_left['neg'])
rule10 = ctrl.Rule(goal_distance['perto'], vel_left['pos'])

go_to_goal_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10])
go_to_goal = ctrl.ControlSystemSimulation(go_to_goal_ctrl)

def fuzzy(error, distance):
    go_to_goal.input['direction'] = error
    go_to_goal.input['goal_distance'] = distance
    go_to_goal.compute()
    return [go_to_goal.output['vel_left'], go_to_goal.output['vel_right']]

goal = [0, 0]

robot = Robot()
while(robot.get_connection_status() != -1):
    orientation = robot.get_current_orientation()
    # print(orientation[2])
    # gamma = angles.convert_degree_to_rad(orientation[2])

    position = robot.get_current_position()
    angle = angles.diff_angle(goal, position)

    diff = orientation[2] - angle + math.pi
    print(angle, orientation[2])
    print(diff)
    if diff > math.pi:
        diff = 2*math.pi - diff
        diff *= -1
    if diff < -math.pi:
        diff += 2*math.pi
    print(diff)

    distance = angles.euclidian_distance(position[:2], goal)
    # print(angle, orientation[2], diff, distance)

    vel = fuzzy(diff, distance) #Using only the 8 frontal sensors
    print(vel)
    robot.set_left_velocity(vel[0])
    robot.set_right_velocity(vel[1])
    # time.sleep(10)