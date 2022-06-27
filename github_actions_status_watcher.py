import json
import time
import serial
import requests
import os

REPO_WORKFLOW_URL = "https://api.github.com/repos/adafruit/circuitpython/actions/workflows/build.yml/runs"
POLL_DELAY = 60 * 3  # 3 minutes
CONCLUSION_LIGHT_TIME = 30  # seconds
CONCLUSION_BUZZER_TIME = 2  # seconds
ENABLE_USB_LIGHT_MESSAGES = False
# serialPort = 'COM57'  # Change to the serial/COM port of the tower light
serialPort = '/dev/USBserial0'  # on mac/linux, it will be a /dev path

RED_ON = 0x11
RED_OFF = 0x21
RED_BLINK = 0x41

YELLOW_ON = 0x12
YELLOW_OFF = 0x22
YELLOW_BLINK = 0x42

GREEN_ON = 0x14
GREEN_OFF = 0x24
GREEN_BLINK = 0x44

BUZZER_ON = 0x18
BUZZER_OFF = 0x28
BUZZER_BLINK = 0x48

baudRate = 9600


def sendCommand(serialport, cmd):
    serialport.write(bytes([cmd]))


def resetState():
    # Clean up any old state
    sendCommand(mSerial, BUZZER_OFF)
    sendCommand(mSerial, RED_OFF)
    sendCommand(mSerial, YELLOW_OFF)
    sendCommand(mSerial, GREEN_OFF)


already_shown_ids = []

headers = {'Accept': "application/vnd.github.v3+json",
           'Authorization': f"token {os.getenv('GITHUB_API_TOKEN')}"}


if __name__ == '__main__':
    mSerial = None
    if ENABLE_USB_LIGHT_MESSAGES:
        print("opening serial port")
        mSerial = serial.Serial(serialPort, baudRate)

    print("Starting Github Workflow Status Watcher")
    print("Press Ctrl-C to Exit")
    while True:
        print("fetching workflow run status")
        resp = requests.get(f"{REPO_WORKFLOW_URL}?per_page=1", headers=headers)
        resp_json = resp.json()
        f = open("action_status_result.json", "w")
        f.write(json.dumps(resp_json))
        f.close()

        workflow_run_id = resp_json['workflow_runs'][0]['id']
        if workflow_run_id not in already_shown_ids:

            status = resp_json['workflow_runs'][0]['status']
            conclusion = resp_json['workflow_runs'][0]['conclusion']
            print(f"{status} - {conclusion}")
            if status == "in_progress" or status == "queued":
                print("YELLOW")
                if ENABLE_USB_LIGHT_MESSAGES:
                    print("sending serial command yellow on")
                    sendCommand(mSerial, YELLOW_ON)

            if status == "completed":
                print(f"adding {workflow_run_id} to shown IDs")
                already_shown_ids.append(workflow_run_id)
                if conclusion == "success":
                    print("GREEN ON")
                    if ENABLE_USB_LIGHT_MESSAGES:
                        sendCommand(mSerial, GREEN_ON)
                        if CONCLUSION_BUZZER_TIME > 0:
                            sendCommand(mSerial, BUZZER_ON)
                            time.sleep(CONCLUSION_BUZZER_TIME)
                            sendCommand(mSerial, BUZZER_OFF)

                    time.sleep(CONCLUSION_LIGHT_TIME - CONCLUSION_BUZZER_TIME)
                    if ENABLE_USB_LIGHT_MESSAGES:
                        sendCommand(mSerial, GREEN_OFF)
                    print("GREEN OFF")
                else:
                    print("RED ON")
                    if ENABLE_USB_LIGHT_MESSAGES:
                        sendCommand(mSerial, RED_ON)
                        if CONCLUSION_BUZZER_TIME > 0:
                            sendCommand(mSerial, BUZZER_ON)
                            time.sleep(CONCLUSION_BUZZER_TIME)
                            sendCommand(mSerial, BUZZER_OFF)

                    time.sleep(CONCLUSION_LIGHT_TIME - CONCLUSION_BUZZER_TIME)
                    if ENABLE_USB_LIGHT_MESSAGES:
                        sendCommand(mSerial, RED_OFF)
                    print("RED OFF")
        else:
            print("already showed this run")
        time.sleep(POLL_DELAY)
