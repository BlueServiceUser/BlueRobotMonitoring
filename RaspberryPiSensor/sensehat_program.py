# -*- coding: utf-8 -*-

##### Libraries #####
import datetime
from sense_hat import SenseHat
from time import sleep
from threading import Thread
import json
import asyncio
from azure.iot.device.aio import IoTHubDeviceClient

##### Logging Settings #####
FILENAME = ""
WRITE_FREQUENCY = 100
TEMP_H=True
TEMP_P=False
HUMIDITY=True
PRESSURE=True
ORIENTATION=True
ACCELERATION=True
MAG=False
GYRO=True
DELAY=1


delay = 100 #milliseconds
environmental_delay_seconds = 10 #seconds
imu_delay_milliseconds = 500 
upload_delay_seconds = 30

sense = SenseHat()
logging = True

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.timestamp() * 1000
            # return o.isoformat("T")+ "Z"

        return json.JSONEncoder.default(self, o)

##### Functions #####

def get_sense_environmental_data():
    data = {}
    data['temperature'] = sense.get_temperature()
    data['pressure'] = sense.get_pressure()
    data['humidity'] = sense.get_humidity()
    data['name'] = "Blue_env_sensor"
    data['timestamp'] = datetime.datetime.now(datetime.timezone.utc)
    return data

def get_sense_imu_data():
    retval = {}
    data = []
    
    # angle degrees
    orientation = {}
    retval["orientation"] = sense.get_orientation()
    # orientation["yaw"]
    # orientation["pitch"]
    # orientation["roll"]
    data.append(orientation) 

    ## Axis G´s
    acc = {}
    retval["acc"] = sense.get_accelerometer_raw()
    # acc["x"]
    # acc["y"]
    # acc["z"]
    data.append(acc)

    # Radians pr second
    gyro = {}
    retval["gyro"] = sense.get_gyroscope_raw()
    # gyro["x"]
    # gyro["y"]
    # gyro["z"]
    data.append(gyro)

    # retval['data'] = data
    retval['name'] = "Blue_imu_sensor"

    retval['timestamp'] = datetime.datetime.now(datetime.timezone.utc)

    return retval


def get_upload_data(payload):
    print("Uploading sensor data...")
    data = {}
    data['name'] = "Blue_pi_sensors"
    data['device'] = "blue-raspberry-sensor-1"
    data['payload'] = payload
    json_body = json.dumps(data, cls=DateTimeEncoder)
    print("Sending message: ", json_body)

    return json_body;

def handle_twin(twin):
    print("Twin received", twin)
    if ('desired' in twin):
        desired = twin['desired']
        # if ('led' in desired):
        #     GPIO.output(24, desired['led'])
        
        if ('UpdateLatencySeconds' in desired):
             updateLatencySeconds = desired['UpdateLatencySeconds']

    if ('reported' in twin):
        reported = twin['reported']
        if(updateLatencySeconds is not None):
            reported['UpdateLatencySeconds'] = updateLatencySeconds


##### Main Program #####


async def main():
    timestamp_env = datetime.datetime.now(datetime.timezone.utc)
    timestamp_imu = datetime.datetime.now(datetime.timezone.utc)
    timestamp_upload = datetime.datetime.now(datetime.timezone.utc)

    batch_data = []

    conn_str = "HostName=BlueRobotMessageBroker.azure-devices.net;DeviceId=blue-raspberry-sensor-1;SharedAccessKey=Rra31BAhJ2gZ9Y55ejFauMmS2omIrGjRCHE0q0yN/yY="
    device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)
    await device_client.connect()

    while True:
        data = get_sense_environmental_data()
        dt = data['timestamp'] - timestamp_env

        data_imu = get_sense_imu_data()
        dt_imu = data_imu['timestamp'] - timestamp_imu

        if int(dt.total_seconds()) > environmental_delay_seconds:
            batch_data.append(data)
            timestamp_env = datetime.datetime.now(datetime.timezone.utc)

        if int(dt_imu.total_seconds() * 1000) > imu_delay_milliseconds:
            batch_data.append(data_imu)
            timestamp_imu = datetime.datetime.now(datetime.timezone.utc)
        
        # Upload if enough time has passed
        upload_interval_dt = datetime.datetime.now(datetime.timezone.utc) - timestamp_upload
        if int(upload_interval_dt.total_seconds()) > upload_delay_seconds:
            twin = await device_client.get_twin()
            handle_twin(twin)

            upload_data = get_upload_data(batch_data)
            batch_data = []
            await device_client.send_message(upload_data)

            timestamp_upload = datetime.datetime.now(datetime.timezone.utc)

    await device_client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
    