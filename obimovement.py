import obi, time, csv, sys, os
from playsound import playsound

path = os.path.dirname(os.path.abspath(__file__))

with open(path + '/saved-positions/bowls.csv', 'r') as read_obj:
  csv_reader = csv.reader(read_obj)
  BOWL_COORDS = list(csv_reader)

with open(path + '/saved-positions/bowl0-scoop-refined.csv', 'r') as read_obj:
  csv_reader = csv.reader(read_obj)
  SCOOP_0 = list(csv_reader)[:-1]

with open(path + '/saved-positions/bowl1-scoop-refined.csv', 'r') as read_obj:
  csv_reader = csv.reader(read_obj)
  SCOOP_1 = list(csv_reader)[:-1]

with open(path + '/saved-positions/bowl2-scoop-refined.csv', 'r') as read_obj:
  csv_reader = csv.reader(read_obj)
  SCOOP_2 = list(csv_reader)[:-1]

with open(path + '/saved-positions/bowl3-scoop-refined.csv', 'r') as read_obj:
  csv_reader = csv.reader(read_obj)
  SCOOP_3 = list(csv_reader)[:-1]

with open(path + '/saved-positions/bowl0-scrape-refined.csv', 'r') as read_obj:
  csv_reader = csv.reader(read_obj)
  SCRAPE_0 = list(csv_reader)

with open(path + '/saved-positions/bowl1-scrape-refined.csv', 'r') as read_obj:
  csv_reader = csv.reader(read_obj)
  SCRAPE_1 = list(csv_reader)

with open(path + '/saved-positions/bowl2-scrape-refined.csv', 'r') as read_obj:
  csv_reader = csv.reader(read_obj)
  SCRAPE_2 = list(csv_reader)

with open(path + '/saved-positions/bowl3-scrape-refined.csv', 'r') as read_obj:
  csv_reader = csv.reader(read_obj)
  SCRAPE_3 = list(csv_reader)

with open(path + '/saved-positions/bowl0-scoop-deep-refined.csv', 'r') as read_obj:
  csv_reader = csv.reader(read_obj)
  DEEPSCOOP_0 = list(csv_reader)[:-1]

with open(path + '/saved-positions/bowl1-scoop-deep-refined.csv', 'r') as read_obj:
  csv_reader = csv.reader(read_obj)
  DEEPSCOOP_1 = list(csv_reader)[:-1]

with open(path + '/saved-positions/bowl2-scoop-deep-refined.csv', 'r') as read_obj:
  csv_reader = csv.reader(read_obj)
  DEEPSCOOP_2 = list(csv_reader)[:-1]

with open(path + '/saved-positions/bowl3-scoop-deep-refined.csv', 'r') as read_obj:
  csv_reader = csv.reader(read_obj)
  DEEPSCOOP_3 = list(csv_reader)[:-1]

with open(path + '/saved-positions/mouth-pos.csv', 'r') as read_obj:
  csv_reader = csv.reader(read_obj)
  MOUTHPOS = list(csv_reader)[0]

class ObiMovement():
  def __init__(self):
    self.robot = obi.Obi('/dev/cu.usbserial-FTBXXIGY')
    self.bowlno = 0
    self.speed = 2
    self.accel = 2
    self.mouthpos = MOUTHPOS #[21274, 17098, 15270, 17810, 19902, 26628] #[23146,15515,18839,19867,18021,26601]
    self.scoop_depth = 0
    self.flag = 0
    print(self.robot.SerialIsOpen())
    print(self.robot.VersionInfo())
    self.robot.Wakeup()
    self.robot.WaitForCMUResponse()
    print("I'm up!")

  def start(self):
    self.flag = 0
    print("Started")
  
  def pause_indefinitely(self):
    self.flag = 1
    print("Paused")

  def stop(self):
    self.flag = 2
    print("Stopped")
    # playsound(path + "/sounds/stop.mp3")

  def time_delay(self, secs):
    self.check_for_code()
    if self.flag == 2:
      return
    while self.flag == 1:
      time.sleep(.2)
      self.check_for_code()
    print("Waiting for " + str(secs) + " seconds.")
    time.sleep(secs)
  
  def cap_speed_and_accel(self):
    if self.speed > 5:
      self.speed = 5
    elif self.speed < 0:
      self.speed = 0

    if self.accel > 5:
      self.accel = 5
    elif self.accel < 0:
      self.accel = 0

  def check_for_code(self):
    with open('obi-code.txt', 'r') as f:
      lines = f.readlines()
      
    with open('obi-code.txt', 'w') as f:
      for line in lines:
        mod_line = line.strip('\n ')
        mod_line = mod_line.replace('obirobot.', 'self.')
        if mod_line in ['self.start()', 'self.pause_indefinitely()', 'self.stop()']:
          ldict = {'self':self}
          exec(mod_line, globals(), ldict)
        elif 'speed' in line or 'accel' in line or 'scoop_depth' in line:
          try:
            ldict = {'self':self}
            exec(mod_line, globals(), ldict)
          except: 
            print("Code (being excecuted within class): " + mod_line)
            if sys.exc_info()[0] != SyntaxError:
              print("This code threw the following error: " + str(sys.exc_info()[0]) + ".")
        else:
          f.write(line)
    
    with open(path + '/obi-code.txt', 'r') as f:
      code = f.read()
    if code != "":
      self.stop()

  def scoop_from_bowlno(self, bowlno="previous"):
    self.check_for_code()
    if self.flag == 2:
      return
    while self.flag == 1:
      time.sleep(.2)
      self.check_for_code()

    self.cap_speed_and_accel()
    print(f"Scooping from bowl {str(self.bowlno)} at max speed {self.speed} and max accel {self.accel} with {'deep scoops' if self.scoop_depth == 1 else 'shallow scoops'}")
    playsound(path + "/sounds/scoop.mp3")

    if self.scoop_depth == 1:
      if bowlno == 0:
        waypoints = DEEPSCOOP_0
      elif bowlno == 1:
        waypoints = DEEPSCOOP_1
      elif bowlno == 2:
        waypoints = DEEPSCOOP_2
      else:
        waypoints = DEEPSCOOP_3
    else:
      if bowlno == 0:
        waypoints = SCOOP_0
      elif bowlno == 1:
        waypoints = SCOOP_1
      elif bowlno == 2:
        waypoints = SCOOP_2
      else:
        waypoints = SCOOP_3

    if bowlno != "previous":
      self.bowlno = bowlno
    
    for i in range(9):
      waypoint = waypoints[i] + [self.speed*2000, self.accel*6000, 0]
      self.robot.SendOnTheFlyWaypointToObi(i, waypoint)
    self.robot.ExecuteOnTheFlyPath()
    self.robot.WaitForCMUResponse()

  def scrape_then_scoop_bowlno(self, bowlno="previous"):
    self.check_for_code()
    if self.flag == 2:
      return
    while self.flag == 1:
      time.sleep(.2)
      self.check_for_code()
    self.cap_speed_and_accel()
    if bowlno != "previous":
      self.bowlno = bowlno
    print(f"Scraping down bowl {str(self.bowlno)} at max speed {self.speed} and max accel {self.accel}")
    playsound(path + "/sounds/scrape.mp3")

    if self.bowlno == 0:
      waypoints = SCRAPE_0
    elif self.bowlno == 1:
      waypoints = SCRAPE_1
    elif self.bowlno == 2:
      waypoints = SCRAPE_2
    else:
      waypoints = SCRAPE_3
    
    for i in range(9):
      waypoint = waypoints[i] + [self.speed*2000, self.accel*6000, 0]
      self.robot.SendOnTheFlyWaypointToObi(i, waypoint)
    self.robot.ExecuteOnTheFlyPath()
    self.robot.WaitForCMUResponse()

    print(f"Scooping from bowl {str(self.bowlno)} at max speed {self.speed} and max accel {self.accel} with {'deep scoops' if self.scoop_depth == 1 else 'shallow scoops'}")
    playsound(path + "/sounds/scoop.mp3")
    if self.scoop_depth == 1:
      if bowlno == 0:
        waypoints = DEEPSCOOP_0
      elif bowlno == 1:
        waypoints = DEEPSCOOP_1
      elif bowlno == 2:
        waypoints = DEEPSCOOP_2
      else:
        waypoints = DEEPSCOOP_3
    else:
      if bowlno == 0:
        waypoints = SCOOP_0
      elif bowlno == 1:
        waypoints = SCOOP_1
      elif bowlno == 2:
        waypoints = SCOOP_2
      else:
        waypoints = SCOOP_3

    if bowlno == 0:
      waypoints[0] = SCRAPE_0[-1]
    elif bowlno == 1:
      waypoints[0] = SCRAPE_1[-1]
    elif bowlno == 2:
      waypoints[0] = SCRAPE_2[-1]
    else:
      waypoints[0] = SCRAPE_3[-1]

    if bowlno != "previous":
      self.bowlno = bowlno
    
    for i in range(9):
      waypoint = waypoints[i] + [self.speed*2000, self.accel*6000, 0]
      self.robot.SendOnTheFlyWaypointToObi(i, waypoint)
    self.robot.ExecuteOnTheFlyPath()
    self.robot.WaitForCMUResponse()

  def move_to_mouth(self):
    self.check_for_code()
    if self.flag == 2:
      return
    while self.flag == 1:
      time.sleep(.2)
      self.check_for_code()

    self.cap_speed_and_accel()
    print(f"Moving to mouth at max speed {self.speed} and max accel {self.accel}")
    waypoint = self.mouthpos + [self.speed*2000, self.accel*6000, 0]
    self.robot.SendOnTheFlyWaypointToObi(0, waypoint)
    self.robot.ExecuteOnTheFlyPath()
    self.robot.WaitForCMUResponse()

  def close(self):
    self.robot.GoToSleep()
    self.robot.Close()
    print(self.robot.SerialIsOpen())
    print("All done")
