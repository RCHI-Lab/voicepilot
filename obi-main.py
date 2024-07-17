from obimovement import ObiMovement
import sys, time, traceback
from pydub import AudioSegment
from pydub.playback import play

obirobot = ObiMovement()

while True: 
  with open('obi-code.txt', 'r') as f:
    code = f.read()

  if code == "":
    time.sleep(.2)
  elif code == 'SYSTEM_TERMINATE()':
    with open('obi-code.txt', 'w') as f:
      pass
    break
  else:
    with open('obi-code.txt', 'w') as f:
      pass
    with open('obi-addinfo.txt', 'w') as f:
      f.write("1")
    obirobot.start()
    try:
      #sound = AudioSegment.from_mp3("sounds/moving.mp3")
      #play(sound)
      exec(code, globals())
      sound = AudioSegment.from_mp3("sounds/ready.mp3")
      play(sound)
    except: 
      if sys.exc_info()[0] != SyntaxError:
        print("Code (being excecuted from main): " + code)
        print("This code threw the following error: " + traceback.format_exc() + str(sys.exc_info()) + ".")
      else:
        print("ChatGPT response: " + code)
        sound = AudioSegment.from_mp3("sounds/try-again.mp3")
        play(sound)
    with open('obi-addinfo.txt', 'w') as f:
      f.write("0")

obirobot.close()