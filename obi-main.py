from obimovement import ObiMovement
import sys, time, traceback, os
from playsound import playsound

obirobot = ObiMovement()
path = os.path.dirname(os.path.abspath(__file__))

while True: 
  with open(path + '/obi-code.txt', 'r') as f:
    code = f.read()

  if code == "":
    time.sleep(.2)
  elif code == 'SYSTEM_TERMINATE()':
    with open(path + '/obi-code.txt', 'w') as f:
      pass
    break
  else:
    with open(path + '/obi-code.txt', 'w') as f:
      pass
    with open(path + '/obi-addinfo.txt', 'w') as f:
      f.write("1")
    obirobot.start()
    try:
      exec(code, globals())
      playsound(path + "/sounds/ready.mp3")
    except: 
      if sys.exc_info()[0] != SyntaxError:
        print("Code (being excecuted from main): " + code)
        print("This code threw the following error: " + traceback.format_exc() + str(sys.exc_info()) + ".")
      else:
        print("ChatGPT response: " + code)
        playsound(path + "sounds/try-again.mp3")
    with open(path + '/obi-addinfo.txt', 'w') as f:
      f.write("0")

obirobot.close()