#!/usr/bin/env python
import rospy
from std_msgs.msg import Float32MultiArray
from std_msgs.msg import Float32
import tensorflow as tf
import numpy as np

NUM_STATES = 200+1024+1024  #possible degrees the joint could move, 1024 force values, two times
NUM_ACTIONS = 32 #2^5   ,one stop-state, two different speed left, two diff.speed right, two servos
GAMMA = 0.5

force_reward_max = 150  #where should the max point be
force_reward_length = 100  #how long/big the area around max
force_max_value = 1024     #how much force values possible
angle_goal = 90
angle_possible_max = 200  #how many degrees the angle can go max
current_degree = 0


angle = []
f1 = []
f2 = []
states = []

def build_reward_state():
	f_list1_length = force_reward_max - (force_reward_length/2)
	f_list1 = [(x==1050) for x in range(f_list1_length)]
	print "length f1 >%d<" %len(f_list1)

	f_list_pos = np.linspace(0,1, num=force_reward_length/2)
	print "length f-pos >%d<" %len(f_list_pos)


	f_list_neg = np.linspace(0.99,0,num=force_reward_length/2)
	print "length f-neg >%d<" %len(f_list_neg)


	f_list2 = [(x==1050) for x in range((1024 - (len(f_list1) + len(f_list_pos) + len(f_list_neg) ) ))]
	print "length f_list2 >%d<" %len(f_list2)


	#c = []
	f1.extend(f_list1)
	f1.extend(f_list_pos)
	f1.extend(f_list_neg)
	f1.extend(f_list2)
	#print(f1)
	#copy the same into f2
        f2.extend(f_list1)
        f2.extend(f_list_pos)
        f2.extend(f_list_neg)
        f2.extend(f_list2)
        #print(f2)

	angle = [(x==angle_goal) for x in range(angle_possible_max)]
	#print(angle)

	states.extend(angle)
	states.extend(f1)
	states.extend(f2)
	print "length of states >%d>" %len(states)

def get_current_state():
	a = [(x==current_degree) for x in range(angle_possible_max)]
	b = [(x==current_force_1) for x in range(force_max_value)]
	c = [(x==current_force_2) for x in range(force_max_value)]
	d = []
	d.extend(a)
	d.extend(b)
	d.extend(c)
	print "length curr-state d >%d<" %len(d)
	return d


def adc_callback(data):
    rospy.loginfo(rospy.get_caller_id() + "adc heard %s", data.data)
    rospy.loginfo("val1: %d", data.data[0])
    current_force_1 = data.data[0]
    current_force_2 = data.data[1]
    
def degree_callback(data):
    rospy.loginfo(rospy.get_caller_id() + "degree heard %f", data.data)
    current_degree = data.data

def listener():

    rospy.init_node('listener', anonymous=True)

    session = tf.Session()
    build_reward_state()

    state = tf.placeholder(float, [None, NUM_STATES])
    targets = tf.placeholder(float, [None, NUM_ACTIONS])

    hidden_weights = tf.Variable(tf.Constant(0., shape=[NUM_STATES, NUM_ACTIONS]))

    output = tf.matmul(state, hidden_weights)

    loss = tf.reduce_mean(tf.square(output - targets))

    train_operation = tf.train.AdamOptimizer(0.1).minimize(loss)

    session.run(tf.initialize_all_variables())

    state_batch = []
    rewards_batch = []
    


    rospy.Subscriber("adc_pi_plus_pub", Float32MultiArray, adc_callback)
    rospy.Subscriber("degree", Float32, degree_callback)

    rate = rospy.Rate(1)

    while not rospy.is_shutdown():
	rospy.loginfo("here")
	state_batch.append(get_current_state())

	


	rate.sleep()




    # spin() simply keeps python from exiting until this node is stopped
    #rospy.spin()

if __name__ == '__main__':
    listener()

