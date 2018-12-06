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


def sensor_listener(data_queue):
    while True:
        sensors_data = get_sensors_data()

        # user algorithum start here

        Q1=sensors_data[0]['Quaternion1']
        Q2=sensors_data[0]['Quaternion2']
        Q3=sensors_data[0]['Quaternion3']
        Q4=sensors_data[0]['Quaternion4']
        # print("Q1:  %f,  Q2:  %f,  Q3:  %f,Q4:  %f" %(Q1, Q2, Q3, Q4))
        R=math.atan2(2*(Q4*Q3+Q1*Q2), 1-2*Q3*Q3-2*Q1*Q1)/3.14159*180
        P=math.atan2(2*(Q4*Q2+Q1*Q3), 1-2*Q1*Q1-2*Q2*Q2)/3.14159*180
        Y=math.asin(2*(Q4*Q1-Q2*Q2))/3.14159*180
        #print("R:  %f,  P:  %f,  Y:  %f" % (R, P, Y))

        data_queue.put(Y, False)


feedback_status = False
udp_port = 4010
timer_period = 3
request_time = 10
send_sensor_request(udp_port, 10)

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
udp_socket.bind(('', udp_port))



