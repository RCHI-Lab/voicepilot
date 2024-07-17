from obimovement import ObiMovement
from pynput import keyboard
import time, csv

obirobot = ObiMovement()

print("Press the teach button on the base of Obi to turn on teach mode. Then, holding the teach button on the arm, position the spoon to a comfortable position. Then, release the teach button on the arm. Finally, press the recording button or the space bar to indicate that this is the desired feeding position.")

button_pressed = False

def on_press(key):
  if key == keyboard.Key.space:
    global button_pressed
    button_pressed = True

listener = keyboard.Listener(
  on_press=on_press)
listener.start()

while not button_pressed:
  time.sleep(0.01)

pos = obirobot.robot.MotorPositions()
listener.stop()

with open(f"saved-positions/mouth-pos.csv", "w") as f:
  writer = csv.writer(f)
  writer.writerows([pos])

print("Done! Mouth position saved.")
obirobot.close()