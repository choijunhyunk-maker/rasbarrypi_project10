import time
import paho.mqtt.client as mqtt
from gpiozero import LED
from gpiozero import Buzzer
from gpiozero import MotionSensor 
import threading

redLed = LED(16)
buzzerPin = Buzzer(20) 
pirPin = MotionSensor(21)
count = 0
previous = 0

def on_message(client, userdata, msg):
    global count

    print(msg.topic+" "+str(msg.payload)) 
    message = msg.payload.decode().strip()
    print(message)
    if message == "turn_off": 
        redLed.off()
        buzzerPin.off()
        count = 0
    elif message == "turn_on": 
        redLed.on()
        buzzerPin.on()
        count = 1
client = mqtt.Client()
client.on_message = on_message

broker_address = "192.168.0.7"
client.connect(broker_address)
client.subscribe("security", 1)

def send_security():
    global count
    while True:
        if count == 0:
            client.publish("security", "safe")
            time.sleep(1)
        elif count == 1:
            client.publish("security", "warning") 
            time.sleep(1)

def detect_motion():
    global count
    global previous
    while True:
        current= pirPin.value
        if previous == 0 and current == 1:
            count = 1
            redLed.on()
            buzzerPin.on()
        previous = current
        time.sleep(0.1)

try:
    task1 = threading.Thread(target=send_security)
    task2 = threading.Thread(target=detect_motion)
    
    task1.start()
    task2.start()
    
    client.loop_forever()

except KeyboardInterrupt:
    redLed.off()
    buzzerPin.off()