import time

from MQTT import Create_MQTT
from settings import settings


# This function is called every time that a message is received on a topic that we are listening to.
def handle_message(client, topic, m):
    print("New message on topic {0}: {1}".format(topic, m))



# You can find the client Id in the settings.py this is used to identify the board
client_id = settings["client_id"]
# This is the chanel that will be used to send and receive data
group_number = "Group_101"

# Create a mqtt connection based on the settings file.
mqtt_client = Create_MQTT(client_id, handle_message)

# Listen for messages on the group number
mqtt_client.subscribe(group_number)


counter = 0

interval = 1
last_message = time.monotonic()
current_time = last_message

while True:
    # update the current time
    current_time = time.monotonic()

    # This line checks for new messages for 0.1 seconds
    try:
        mqtt_client.loop(0.1)
    except:
        print("some mqtt error occurred")

    # Send a message every interval
    if current_time - last_message > interval:

        try:
            mqtt_client.publish(group_number, f"{client_id} is at: {counter}")
        except ConnectionError:
            print("mqtt write timeout!")
            time.sleep(0.5)

        counter += 1
        last_message = current_time



