import time

import board
import digitalio
import p9813
from MQTT import Create_MQTT
from settings import settings


# This function is called every time that a message is received on a topic that we are listening to.
def handle_message(client, topic, m):
    global led_cycle, led_state, mqtt_client, group_number
    print("New message on topic {0}: {1}".format(topic, m))

    # If we are still off and receive marco reply with polo
    if led_state == "off" or led_state == "waiting" and m == "marco":
        # This sleep is here to show you that messages get received.
        # remove it to make it run at full speed.
        time.sleep(1)
        mqtt_client.publish(group_number, "polo")
        led_state = "found"
        led_cycle = 0

    # If we are waiting and revive polo go to found
    if led_state == "waiting" and m == "polo":
        led_state = "found"
        led_cycle = 0


# You can find the client Id in the settings.py this is used to identify the board
client_id = settings["client_id"]
# This is the chanel that will be used to send and receive data
group_number = "TA"

# Create a mqtt connection based on the settings file.
mqtt_client = Create_MQTT(client_id, handle_message)

# Listen for messages on the group number
mqtt_client.subscribe(group_number)

# Register sensors
button = digitalio.DigitalInOut(board.D2)
button.direction = digitalio.Direction.INPUT
button_pressed = False

# Register chainable LED
pin_clk = board.D13
pin_data = board.D10
num_leds = 1
leds = p9813.P9813(pin_clk, pin_data, num_leds)
leds.reset()

# Variables for the logic
led_state = "off"
led_cycle = 0
led_increase = True


# Scales the color value between 1 and 0
def color_scale(color: tuple, scale: float) -> tuple:
    return tuple(int(scale * x) for x in color)


while True:
    # This line checks for new messages for 0.1 seconds
    try:
        mqtt_client.loop(0.1)
    except:
        print("some mqtt error occurred")
    # If there was a new message it will execute handle_message() on that message now.

    # check if button is pressed
    if button_pressed is False and button.value is True:
        # make sure we send only once
        button_pressed = True

        # If we are off send to the group channel the message "Marco"
        if led_state == "off":
            led_cycle = 0
            led_state = "waiting"
            mqtt_client.publish(group_number, "marco")
        # If we are found turn us off
        elif led_state == "found":
            led_cycle = 0
            led_state = "off"

    # check if button is released
    if button_pressed is True and button.value is False:
        button_pressed = False

    # Set the LED state
    if led_state == "off":
        leds.fill((0, 0, 0))
    if led_state == "waiting":
        # While waiting on "Polo" blink the LED
        leds.fill(color_scale((67, 67, 254), led_cycle))
    if led_state == "found":
        # While waiting on "Polo" blink the LED
        leds.fill(color_scale((54, 254, 37), led_cycle))

    # Move the LED to its next cycle step
    if led_increase is True:
        led_cycle += 0.05
        if led_cycle > 1:
            led_cycle = 1
            led_increase = False
    else:
        led_cycle -= 0.05
        if led_cycle < 0:
            led_cycle = 0
            led_increase = True

    leds.write()
