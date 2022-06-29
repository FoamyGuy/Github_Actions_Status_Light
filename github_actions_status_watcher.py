import json
import time
import serial
import requests
import os

# URL to pull data from
REPO_WORKFLOW_URL = "https://api.github.com/repos/adafruit/circuitpython/actions/workflows/build.yml/runs"

# How long to wait in between data fetches
POLL_DELAY = 60 * 3  # 3 minutes

# How long the red/green light should stay on when a workflow run is completed (success or failure)
CONCLUSION_LIGHT_TIME = 30  # seconds

# How long the buzzer should turn on for when a workflow run is completed.
CONCLUSION_BUZZER_TIME = 2  # seconds

# if True send messages to the USB light else print only
ENABLE_USB_LIGHT_MESSAGES = False

# Serial port that the USB light is connected at
# serialPort = 'COM57'  # Change to the serial/COM port of the tower light
serialPort = '/dev/USBserial0'  # on mac/linux, it will be a /dev path

# USB Light Constants
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

# baud rate for serial communication
baudRate = 9600

# convenience function to send a command
def sendCommand(serialport, cmd):
    # write the command to the serial port
    serialport.write(bytes([cmd]))


# turn off all lights and buzzer
def resetState():
    sendCommand(mSerial, BUZZER_OFF)
    sendCommand(mSerial, RED_OFF)
    sendCommand(mSerial, YELLOW_OFF)
    sendCommand(mSerial, GREEN_OFF)

# list that will store the IDs of each workflow as it gets completed.
already_shown_ids = []

# HTTP Header for github API. Must fill in your GitHub API TOKEN if not using env vars.
headers = {'Accept': "application/vnd.github.v3+json",
           'Authorization': f"token {os.getenv('GITHUB_API_TOKEN')}"}

# if program is running from CLI
if __name__ == '__main__':
    # serial connection variable
    mSerial = None

    if ENABLE_USB_LIGHT_MESSAGES:
        print("opening serial port")
        # initialize the serial connection
        mSerial = serial.Serial(serialPort, baudRate)

    print("Starting Github Workflow Status Watcher")
    print("Press Ctrl-C to Exit")
    # infinite loop until KeyboardInterrupt
    while True:
        print("fetching workflow run status")
        # GET request to github API to pull current data
        resp = requests.get(f"{REPO_WORKFLOW_URL}?per_page=1", headers=headers)

        # access response as json data
        resp_json = resp.json()

        # open a file to write the results to
        f = open("action_status_result.json", "w")

        # write the results to the opened file
        f.write(json.dumps(resp_json))
        # close to complete file write
        f.close()

        # lookup the workflow ID from the response data
        workflow_run_id = resp_json['workflow_runs'][0]['id']

        # if we have not already shown this workflow ID
        if workflow_run_id not in already_shown_ids:
            # lookup the status from the response data
            status = resp_json['workflow_runs'][0]['status']

            # lookup the conclusion from the response data
            conclusion = resp_json['workflow_runs'][0]['conclusion']

            # output status and conclusion
            print(f"{status} - {conclusion}")

            # if the workflow is running or waiting to run
            if status == "in_progress" or status == "queued":
                print("YELLOW")
                if ENABLE_USB_LIGHT_MESSAGES:
                    print("sending serial command yellow on")
                    sendCommand(mSerial, YELLOW_ON)

            # if the workflow has finished
            if status == "completed":
                print(f"adding {workflow_run_id} to shown IDs")

                # add the workflow ID to our list to remember
                already_shown_ids.append(workflow_run_id)

                # if it was successful
                if conclusion == "success":
                    print("GREEN ON")
                    if ENABLE_USB_LIGHT_MESSAGES:
                        # turn green light on
                        sendCommand(mSerial, GREEN_ON)

                        # if we need to sound the buzzer
                        if CONCLUSION_BUZZER_TIME > 0:
                            # turn on buzzer
                            sendCommand(mSerial, BUZZER_ON)
                            # wait for buzzer time
                            time.sleep(CONCLUSION_BUZZER_TIME)
                            # turn off buzzer
                            sendCommand(mSerial, BUZZER_OFF)

                    # wait the remainder of the light up time
                    time.sleep(CONCLUSION_LIGHT_TIME - CONCLUSION_BUZZER_TIME)
                    if ENABLE_USB_LIGHT_MESSAGES:
                        # turn green light off
                        sendCommand(mSerial, GREEN_OFF)
                    print("GREEN OFF")
                else:  # workflow run failed:
                    print("RED ON")
                    if ENABLE_USB_LIGHT_MESSAGES:
                        # turn red light on
                        sendCommand(mSerial, RED_ON)
                        # if we need to sound the buzzer
                        if CONCLUSION_BUZZER_TIME > 0:
                            # turn on buzzer
                            sendCommand(mSerial, BUZZER_ON)
                            # wait for buzzer time
                            time.sleep(CONCLUSION_BUZZER_TIME)
                            # turn off buzzer
                            sendCommand(mSerial, BUZZER_OFF)
                    # wait the remaining light time
                    time.sleep(CONCLUSION_LIGHT_TIME - CONCLUSION_BUZZER_TIME)
                    if ENABLE_USB_LIGHT_MESSAGES:
                        # turn off red light
                        sendCommand(mSerial, RED_OFF)
                    print("RED OFF")
        else:  # we already showed this workflow run
            print("already showed this run")

        # wait until next loop iteration
        time.sleep(POLL_DELAY)
