#coding:utf-8
import requests
import threading
import socket
import json
import time
import math
import queue
import threading

data_queue = queue.Queue()

url_feedback_trigger = 'http://192.168.137.1/api/v1/feedback_trigger'
url_sensors_request = 'http://192.168.137.1/api/v1/sensors_request'

calib_count=0

#sensor1
R_total_1=0
P_total_1=0
Y_total_1=0

#sensor2
R_total_2 = 0
P_total_2 = 0
Y_total_2 = 0


def sage_listener():
    while True:
        item = data_queue.get()
        print(item)
        data_queue.task_done()#完成后必须调用


def send_feedback(index, _type, time):

    def feedback_url_request(index, _type, time):
        parameters = {'index':index, 'type':_type, 'time':time}
        resp = requests.get(url_feedback_trigger, params=parameters, timeout=1)
        print(resp)
        return resp

    send_feedback_thread = threading.Thread(
        name="SendFeedback",
        target=feedback_url_request,
        args=(index, _type, time))
    send_feedback_thread.setDaemon(True)
    send_feedback_thread.start()


def get_sensors_data():
    global udp_socket
    buffer_size = 50000
    recv_data = udp_socket.recvfrom(buffer_size)
    #print(recv_data)
    sensors_data = json.loads(recv_data[0].decode('utf-8'))
    return sensors_data


def send_sensor_request(port, time):
    global time_period
    parameters = {'port':port, 'time':time}
    resp = requests.get(url_sensors_request, params=parameters, timeout=1)
    print(resp.status_code)
    sensors_data_stream = threading.Timer(timer_period, send_sensor_request, [port, time])
    sensors_data_stream.start()


def bias_quater(Q1,Q2,Q3,Q4,Q1_ex,Q2_ex,Q3_ex,Q4_ex):

    Q1_bias = -Q1*Q4_ex+Q4*Q1_ex+(-Q2*Q3_ex)-(-Q3*Q2_ex)
    Q2_bias= -Q2*Q4_ex+Q4*Q2_ex+(-Q3*Q1_ex)-(-Q1*Q3_ex)
    Q3_bias= -Q3*Q4_ex+Q3_ex*Q4+(-Q1*Q2_ex)-(-Q2*Q1_ex)
    Q4_bias=Q4*Q4_ex-(-Q1*Q1_ex)-(-Q2*Q2_ex)-(-Q3*Q3_ex)
    #print("Q1:  %f,  Q2:  %f,  Q3:  %f,Q4:  %f" %(Q1_bias, Q2_bias, Q3_bias, Q4_bias))

    return Q1_bias, Q2_bias, Q3_bias, Q4_bias

class DataPacket():
    def __init__(self,R,P,Y):
        self.R = R
        self.P = P
        self.Y = Y


def sensor_listener(data_queue):
    while True:
        sensors_data = get_sensors_data()
        # user algorithum start here
        global R_total_1, P_total_1, Y_total_1
        global R_total_2, P_total_2, Y_total_2
        global calib_count

        calib_iter_times=10
        calib_count=calib_count+1
        print(calib_count)


        # sensor 1
        Q1_1=sensors_data[0]['Quaternion1']
        Q2_1=sensors_data[0]['Quaternion2']
        Q3_1=sensors_data[0]['Quaternion3']
        Q4_1=sensors_data[0]['Quaternion4']
        #print("Q1:  %f,  Q2:  %f,  Q3:  %f,Q4:  %f" %(Q1, Q2, Q3, Q4))

        # R=math.atan2(2*(Q4_1*Q3_1+Q1_1*Q2_1), 1-2*Q3_1*Q3_1-2*Q1_1*Q1_1)/3.14159*180
        # P=math.atan2(2*(Q4_1*Q2_1+Q1_1*Q3_1), 1-2*Q1_1*Q1_1-2*Q2_1*Q2_1)/3.14159*180
        # try:
        #     Y=math.asin(2*(Q4_1*Q1_1-Q2_1*Q2_1))/3.14159*180
        #     if abs(Q1_1) <0.7:
        #         Y=180-Y
        #     elif Y<0:
        #         Y=Y+360
        # except ValueError:
        #     continue
        # print("raw")
        # print("R:  %f,  P:  %f,  Y:  %f" % (R, P, Y))

        #with bias_quater function
        if calib_count <=calib_iter_times:
            Q1_ex_1 = Q1_1
            Q2_ex_1 = Q2_1
            Q3_ex_1 = Q3_1
            Q4_ex_1 = Q4_1
            #print("Q1_cal:  %f,  Q2_cal:  %f,  Q3_cal:  %f,Q4_cal:  %f" %(Q1_cal, Q2_cal, Q3_cal, Q4_cal))
        else:
            Q1_bias_1, Q2_bias_1, Q3_bias_1, Q4_bias_1=bias_quater(Q1_1, Q2_1, Q3_1, Q4_1, Q1_ex_1, Q2_ex_1, Q3_ex_1, Q4_ex_1)
            # print("Q1:  %f,  Q2:  %f,  Q3:  %f,Q4:  %f" %(Q1, Q2, Q3, Q4))
            R_bias_1 = math.atan2(2 * (Q4_bias_1 * Q2_bias_1 + Q1_bias_1 * Q3_bias_1),
                                1 - 2 * Q1_bias_1 * Q1_bias_1 - 2 * Q2_bias_1 * Q2_bias_1) / 3.14159 * 180
            P_bias_1 = math.atan2(2 * (Q4_bias_1 * Q3_bias_1 + Q1_bias_1 * Q2_bias_1),
                                1 - 2 * Q3_bias_1 * Q3_bias_1 - 2 * Q1_bias_1 * Q1_bias_1) / 3.14159 * 180
            try:
                Y_bias_1 = math.asin(2 * (Q4_bias_1 * Q1_bias_1 - Q2_bias_1 * Q2_bias_1)) / 3.14159 * 180
            except ValueError:
                continue

            Q1_ex_1 = Q1_1
            Q2_ex_1 = Q2_1
            Q3_ex_1 = Q3_1
            Q4_ex_1 = Q4_1

            R_total_1 = R_total_1+R_bias_1
            P_total_1 = P_total_1+P_bias_1
            Y_total_1 = Y_total_1+Y_bias_1
            data_queue.put(DataPacket(R_total_1,P_total_1,Y_total_1), False)
            print("R:  %f,  P:  %f,  Y:  %f" % (R_total_1,P_total_1,Y_total_1))

        # sensor 2
        Q1_2 = sensors_data[1]['Quaternion1']
        Q2_2 = sensors_data[1]['Quaternion2']
        Q3_2 = sensors_data[1]['Quaternion3']
        Q4_2 = sensors_data[1]['Quaternion4']
        # print("Q1:  %f,  Q2:  %f,  Q3:  %f,Q4:  %f" %(Q1, Q2, Q3, Q4))

        # with bias_quater function
        if calib_count <= calib_iter_times:
            Q1_ex_2 = Q1_2
            Q2_ex_2 = Q2_2
            Q3_ex_2 = Q3_2
            Q4_ex_2 = Q4_2
            # print("Q1_cal:  %f,  Q2_cal:  %f,  Q3_cal:  %f,Q4_cal:  %f" %(Q1_cal, Q2_cal, Q3_cal, Q4_cal))
        else:
            Q1_bias_2, Q2_bias_2, Q3_bias_2, Q4_bias_2 = bias_quater(Q1_2, Q2_2, Q3_2, Q4_2, Q1_ex_2, Q2_ex_2, Q3_ex_2, Q4_ex_2)
            # print("Q1:  %f,  Q2:  %f,  Q3:  %f,Q4:  %f" %(Q1, Q2, Q3, Q4))
            R_bias_2 = math.atan2(2 * (Q4_bias_2 * Q2_bias_2 + Q1_bias_2 * Q3_bias_2),
                                1 - 2 * Q1_bias_2 * Q1_bias_2 - 2 * Q2_bias_2 * Q2_bias_2) / 3.14159 * 180
            P_bias_2 = math.atan2(2 * (Q4_bias_2 * Q3_bias_2 + Q1_bias_2 * Q2_bias_2),
                                1 - 2 * Q3_bias_2 * Q3_bias_2 - 2 * Q1_bias_2 * Q1_bias_2) / 3.14159 * 180
            try:
                Y_bias_2 = math.asin(2 * (Q4_bias_2 * Q1_bias_2 - Q2_bias_2 * Q2_bias_2)) / 3.14159 * 180
            except ValueError:
                continue

            Q1_ex_2 = Q1_2
            Q2_ex_2 = Q2_2
            Q3_ex_2 = Q3_2
            Q4_ex_2 = Q4_2

            R_total_2 = R_total_2 + R_bias_2
            P_total_2 = P_total_2 + P_bias_2
            Y_total_2 = Y_total_2 + Y_bias_2
            #data_queue.put(DataPacket(R_total_2, P_total_2, Y_total_2), False)
            print("R:  %f,  P:  %f,  Y:  %f" % (R_total_2, P_total_2, Y_total_2))

feedback_status = False
udp_port = 4010
timer_period = 3
request_time = 10
send_sensor_request(udp_port, 10)

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
udp_socket.bind(('', udp_port))



