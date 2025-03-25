import keyboard
import threading
import time
from vicon_dssdk import ViconDataStream
import pyautogui
import random
from datetime import datetime

vicon_client = ViconDataStream.Client()
vicon_client.Connect('localhost:801')
vicon_client.EnableMarkerData()

# Global variables, to control the stimulation signal
vicon_data_running = False
stimulate = 0
vicon_data = ''
voltage = 2

def decelerate_task():
    global stimulate
    stimulate = 1
    time.sleep(0.4)
    stimulate = 0

def right_task():
    global stimulate
    stimulate = 2
    time.sleep(0.4)
    stimulate = 0

def left_task():
    global stimulate
    stimulate = 3
    time.sleep(0.4)
    stimulate = 0



def get_vicon_data():
    global vicon_data_running
    global vicon_data
    global voltage
    while vicon_data_running:
        while not vicon_client.IsConnected():
            print('.')
            vicon_client.Connect('localhost:801')
            vicon_client.EnableMarkerData()

        if vicon_client.IsConnected():
            if vicon_client.GetFrame():
              vicon_data = vicon_data + 'Frame Number: {}'.format(vicon_client.GetFrameNumber()) + ' '
              vicon_data = vicon_data + 'Head: {}'.format(vicon_client.GetMarkerGlobalTranslation('CockRoach', 'Head')[0]) + ' '
              vicon_data = vicon_data + 'Body: {}'.format(vicon_client.GetMarkerGlobalTranslation('CockRoach', 'Body')[0]) + ' '
              vicon_data = vicon_data + 'Tail: {}'.format(vicon_client.GetMarkerGlobalTranslation('CockRoach', 'Tail')[0]) + ' '
              vicon_data = vicon_data + 'Ref: {}'.format(vicon_client.GetMarkerGlobalTranslation('CockRoach', 'Ref')[0]) + ' '
              vicon_data = vicon_data + 'stimulate: {}'.format(stimulate) + ' '
              vicon_data = vicon_data + 'voltage: {}'.format(voltage)+ "\n"
        with open("vicon_data.txt", "a") as file:
            file.write(vicon_data )
            vicon_data = ''


def main():
    global vicon_data_running
    global stimulate
    vicon_data_thread = threading.Thread(target=get_vicon_data)
    # keys are stored to automatically output the stimulation types
    keys =  ['left'] * 5 + ['right'] * 5 + ['up'] * 5
    key_counts = {'left': 0, 'right': 0}

    # interval between two stimulations
    interval = 6
    time.sleep(15)
    # record the start time
    start_time = time.perf_counter()

    if not vicon_data_running:
        vicon_data_running = True
        vicon_data_thread.start()
        print("Start recording data from VICON")
    try:
        for i in range(15):
            # calculate the target time
            target_time = start_time + i * interval

            # wait until the target time
            while time.perf_counter() < target_time:
                time.sleep(0.001)

            # randomly remove a key from the stored keys
            key = random.choice(keys)
            keys.remove(key)

            #  output the key
            pyautogui.press(key)

            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            if key == 'up':
                stimulate_task_thread = threading.Thread(target=decelerate_task)
                stimulate_task_thread.start()

            if key == 'left':
                stimulate_task_thread = threading.Thread(target=left_task)
                stimulate_task_thread.start()

            if key == 'right':
                stimulate_task_thread = threading.Thread(target=right_task)
                stimulate_task_thread.start()
            # update the key counts
            key_counts[key] += 1

            # print the current time, the current pressed key and total pressed keys
            print(f'{current_time} - Pressed {key} ')
            print(f'Totally: {key_counts}')
    except KeyboardInterrupt:
        print("Program ended")
    finally:
        print(f'Final keys pressed: {key_counts}')




if __name__ == "__main__":
    main()
