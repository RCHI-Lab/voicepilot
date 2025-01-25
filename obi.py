import serial  #Requires pyserial (i.e., you may need to do "pip install pyserial")
import time
#import array

class Obi:
    #############################################################################################
    # Open the serial connection.  Takes one input, a string that has the port they wish to open.
    # "Com3" in windows for example or "/dev/ttyUSB0" in Linux.
    #############################################################################################
    def __init__(self, StringComPort):
        global ser
        ser = serial.Serial(port = StringComPort,
                            baudrate = 115200,
                            parity = serial.PARITY_NONE,
                            stopbits = serial.STOPBITS_ONE,
                            bytesize = serial.EIGHTBITS)

    ##############################
    # Close the serial connection.
    ##############################
    def Close(self):
        ser.close()

    ##########################################################################
    # Returns a boolean indicating if the serial port is open.  True if it is.
    ##########################################################################
    def SerialIsOpen(self):
        return ser.isOpen()

    #####################################################################################
    # Used to send a command to Obi that does not cause Obi to generate a response to us.
    #####################################################################################
    def SendCommandToObiNoResponse(self, StringCommandInput):
        #########################################################################################
        # Reset the input buffer so any accumulated comamnds we've sent and had echoed back to us
        # (see "WithResponse" for more detail on this) get purged.
        #############################################;t############################################
        ser.reset_input_buffer()

        #####################################################################################
        # All commands to Obi start with \x02 (Acsii STX, start of character.  Why that one?
        # Dunno.  It predates me.) and ends with a line feed (\n, Ascii 10-decimal)
        ####################################################################################
        StringCommandOutput = '\x02' + StringCommandInput + '\n'
        ser.write(StringCommandOutput.encode())

    #############################################################################
    # Used to send a command to Obi that causes Obi to generate a response to us.
    # We return it as a string to our caller.
    #############################################################################
    def SendCommandToObiWithResponse(self, StringCommandInput):
        #######################
        # As in the previous...
        #######################
        ser.reset_input_buffer()
        StringCommandOutput = '\x02' + StringCommandInput + '\n'
        ser.write(StringCommandOutput.encode())

        #####################################################################
        # Pause a bit to give Obi time to process and respond to the command.
        #####################################################################
        time.sleep(0.25)

        ###################################################################################################
        # Note: as in other programs, the serial port buffer will contain our command, then Obi's response,
        # then perhaps other things.  For example, for version information it'll probably contain something
        # like this:
        #
        # '\x02_getversioninfo\r\n\x06<Obi Version Info Text>\r\nMaintenance Login: '
        #
        # This happens because Obi echoes serial bus input chars to the serial bus so they appear on the
        # screen in things like putty.  Alas, that means we, too get them echoed back to us.  Of course
        # if Obi has anything to say to the screen (like the login prompt above) we get that too./
        #
        # So for any transaction requiring a response, we'll have to extract the response by looking for
        # the leading \x06 then check subsequent characters 'til we hit either \r or \n.  This also means
        # that we can't easily use readline since that'll stop reading at a line terminator (\r or \n) and
        # while we could use another readline until we find what we're looking for that could leave some
        # garbage in the buffer (e.g. "Maintenance Login: " above).  Best get rid of 'em now.
        #
        # Why 'fred'?  Because I couldn't think of a good descriptive name and 'fred' is easy to type.
        ###################################################################################################
        fred1 = ''
        while ser.inWaiting() > 0:
            fred1 += ser.read(1).decode()

        fred2start = -1
        fred2end = 0
        fred1index = -1
        for fred1char in fred1:
            fred1index += 1
            #########################################################################
            # Looking for \x06 here.  For some reason Python doesn't recognize '\x06'
            # as a character as other languages do so use "ord" to tell it to look
            # for Ascii-6.
            #########################################################################
            if ord(fred1char) == 6:
                fred2start = fred1index

            #############################################################################################
            # Once we've found the leading \x06, look for the line terminator at the end of the response.
            #############################################################################################
            elif fred2start >= 0:
                if fred1char == '\r' or fred1char == '\n':
                    fred2end = fred1index
                    break

        #################################################################################################
        # Extract everything after the \x06 and before the line terminator and return that to our caller.
        #################################################################################################
        fred2 = fred1[fred2start+1:fred2end]
        return fred2

    ##################################################################################
    # Used to for a message from Obi intended for us.  It has a leading hex code of 7.
    # We return it as a string to our caller.
    ##################################################################################
    def WaitForCMUResponse(self):
        ####################################################################################
        # This message can come at any time, fairly quickly for thing like move to next bowl
        # or quite a while later when exceuting a series of waypoints.  So we need to wait
        # 'til we find the start of our message.  The (fairly safe) assumption is that we'll
        # only get this in a respmnse to a single command to Obi and the next such command
        # won't go outy until "this" one is done.
        ####################################################################################
        fred2start = -1
        while (fred2start  < 0):
           if ser.inWaiting() > 0:
               fredtest = ser.read(1).decode()
               ##################################################################################
               # "ord" is Python's way of doing what any other language would do with a hex code.
               # Hence "ord == 7" means "is this \x07".  Note that if it never arrives for example
               # if this call is made following an Obi funstion that doesn't reply with something
               # for us) we'll loop forever.  If that becomes an issue, exit the loop after enuf
               # time has gone by.
               ##################################################################################
               if ord(fredtest) == 7:
                 fred2start = 0
                 fred1index = 0
                 break
           #################################################
           # Pause for a bit to wait for the next character.
           #################################################
           time.sleep(.1)

        fred1 = ''
        while ser.inWaiting() > 0:
            fred1 += ser.read(1).decode()

        fred2end = 0
        fred1index = -1
        for fred1char in fred1:
            fred1index += 1
            #########################################################################################
            # Having found the leading \x07, look for the line terminator at the end of the response.
            #########################################################################################
            if fred2start >= 0:
                if fred1char == '\r' or fred1char == '\n':
                    fred2end = fred1index
                    break

        ################################################################
        # Extract everything after the \x07 (which is not in the string)
        # and before the line terminator (which is not in the string)
        # and return that to our caller.
        ################################################################
        fred2 = fred1[fred2start:fred2end]
        return fred2

    #####################################################################################################
    # Gets version info from Obi.  Mainly useful to check if the serial connection to Obi is operational.
    # The port can be opened without Obi actually being there so checking if the serial conection is open
    # may not be sufficient.
    #####################################################################################################
    def VersionInfo(self):
        return self.SendCommandToObiWithResponse('_getversioninfo')

    ##################################
    # Gets arm moving status from Obi.
    ##################################
    def ArmIsMoving(self):
        ArmStatusString = self.SendCommandToObiWithResponse('_ArmMovingQuery')
        ##########################################################
        # Obi gives us string with a format of:
        #
        #  ~ArmMoving, 0 or 1
        #
        # Parse 'em out into a list, keeping in mind that the 1st,
        # index 0, has the leading text,
        ##########################################################
        ArmStatii = [0, 0]
        ArmStatii = ArmStatusString.split(",")
        return ArmStatii[1]

    #############################
    # Tell Obi to turn itself on.
    #############################
    def Wakeup(self):
        self.SendCommandToObiNoResponse('_UP')

    ##############################
    # Tell Obi to turn itself off.
    ##############################
    def GoToSleep(self):
        self.SendCommandToObiNoResponse('_DN')

    ################################################################################
    # Tell Obi to stop its current motion.  This is a Noop if the Arm is not moving.
    ################################################################################
    def StopMotion(self):
        self.SendCommandToObiNoResponse('_STOP')
        #time.sleep(3.0)

    ################################################################################
    # Tell Obi to restart its motion with an 'on the fly' path.  This is a Noop if
    # the Arm is not in a collision state or no path has been defined.
    ################################################################################
    #def MoveToNewPath(self):
    #    self.SendCommandToObiNoResponse('_RESTART')

    ##################################################################
    # Tell Obi to move to the next bowl (includes returning from POD).
    # Also restarts motion after a stop command.    
    ##################################################################
    def MoveToNextBowl(self):
        self.SendCommandToObiNoResponse('_MOVE')

    ##########################################################
    # Tell Obi to move to the POD from its current location or
    # return to the most-recent bowl if already at the POD.
    # Also restarts motion after a stop command.    
    ##########################################################
    def MoveToOrFromPOD(self):
        self.SendCommandToObiNoResponse('_FEED')

    #################################################################
    # Get the current motor locations from Obi as a list of integers.
    #################################################################
    def MotorPositions(self):
        MotorPositionsString = self.SendCommandToObiWithResponse('_MTR_POS')
        ################################################################
        # Obi gives us string with a format of:
        #
        #  ~MtrPos, x1, x2,. x3, x4, x5, x6
        #
        # The x's are the motor positions.  Parse 'em out into a list,
        # keeping in mind that the 1st, index 0, has the leading text,
        # hence the "-1" on the left side of the assignment to the list
        # of just the motor angles.
        ################################################################
        CurrentMotorPositions = [0, 0, 0, 0, 0, 0]
        CurrentMotorPositionPieces = MotorPositionsString.split(",")
        for iii in range (1, 7):
            CurrentMotorPositions[iii-1] = int(CurrentMotorPositionPieces[iii].strip())
        return CurrentMotorPositions

    ######################################################################################
    # Get the current motor loads (or currents for XM540s) from Obi as a list of integers.
    ######################################################################################
    def MotorLoads(self):
        MotorLoadsString = self.SendCommandToObiWithResponse('_MTR_LOAD')
        ################################################################
        # Obi gives us string with a format of:
        #
        #  ~MtrLoad, x1, x2,. x3, x4, x5, x6
        #
        # The x's are the motor loads.  Parse 'em out into a list,
        # keeping in mind that the 1st, index 0, has the leading text,
        # hence the "-1" on the left side of the assignment to the list
        # of just the motor loads.
        ################################################################
        CurrentMotorLoads = [0, 0, 0, 0, 0, 0]
        CurrentMotorLoadPieces = MotorLoadsString.split(",")
        for iii in range (1, 7):
            CurrentMotorLoads[iii-1] = int(CurrentMotorLoadPieces[iii].strip())
        return CurrentMotorLoads

    ####################################################################
    # Get the current motor temperatures from Obi as a list of integers.
    ####################################################################
    def MotorTemperatures(self):
        MotorTemperaturesString = self.SendCommandToObiWithResponse('@P')
        #################################################################
        # Obi gives us string with a format of:
        #
        #  ~MtrTemps, x1, x2,. x3, x4, x5, x6
        #
        # The x's are the motor temperatures.  Parse 'em out into a list,
        # keeping in mind that the 1st, index 0, has the leading text,
        # hence the "-1" on the left side of the assignment to the list
        # of just the motor temperatures.
        #################################################################
        CurrentMotorTemperatures = [0, 0, 0, 0, 0, 0]
        CurrentMotorTemperaturePieces = MotorTemperaturesString.split(",")
        for iii in range (1, 7):
            CurrentMotorTemperatures[iii-1] = int(CurrentMotorTemperaturePieces[iii].strip())
        return CurrentMotorTemperatures

    #################################################################################
    # Send an "on the fly" waypoint to Obi.  Expects all input values to be integers.
    #################################################################################
    def SendOnTheFlyWaypointToObi(self, IntegerWaypointIndex, InetgerWaypointList):
        ####################################################################
        # Obi's on the fly path is limited to 9 waypoints.  Enforce it here.
        ####################################################################
        if IntegerWaypointIndex > 8:
            print ("Obi's dynamic path is limited to 9 waypoints.  Waypoint ", IntegerWaypointIndex + 1, " will be ignored.")
            return
        MsgForGarcia = "!!!," + str(IntegerWaypointIndex)
        for iii in range (0, 9):
            MsgForGarcia += "," + str(InetgerWaypointList[iii])
        self.SendCommandToObiNoResponse(MsgForGarcia)
        ##############################################
        # Pause a bit to give Obi time to digest that.
        ##############################################
        time.sleep(0.05)

    #####################################################################################
    # Tell Obi to execute the path of "on the fly" waypoints we most-recently sent to it.
    #####################################################################################
    def ExecuteOnTheFlyPath(self):
        self.SendCommandToObiNoResponse("!!!!")

    ###############################################################################
    # Move a motor to a target location.  Input values are expected to be integers.
    ###############################################################################
    def MoveMotorToAbsolutePosition(self, IntegerMotorIndex, IntegerTargetAngle):
        ########################################
        # Make sure the motor index makes sense.
        ########################################
        if IntegerMotorIndex < 0 or IntegerMotorIndex > 5:
            print ("Motor Index must be between 0 and 5 for absolute rotations")
            return
        self.SendCommandToObiNoResponse("!!A," + str(IntegerMotorIndex) + "," + str(IntegerTargetAngle))

    #############################################################################################################
    # Move a motor by a target angle relative to its current location.  Input values are expected to be integers.
    #############################################################################################################
    def MoveMotorToRelativePosition(self, IntegerMotorIndex, IntegerTargetAngle):
        ########################################
        # Make sure the motor index makes sense.
        ########################################
        if IntegerMotorIndex < 0 or IntegerMotorIndex > 5:
            print ("Motor Index must be between 0 and 5 for relative rotations")
            return
        self.SendCommandToObiNoResponse("!!R," + str(IntegerMotorIndex) + "," + str(IntegerTargetAngle))

    ###################################################################################
    # Tell Obi to disenagge/re-engage (i.e., turn torque off/on for) all of its motors.
    ###################################################################################
    def DisengageMotors(self):
        self.SendCommandToObiNoResponse("_DISENGAGE")
    def ReengageMotors(self):
        self.SendCommandToObiNoResponse("_ENGAGE")
        
    ##################################
    # Ask Obi where in the path he is.
    ##################################    
    def GetPathPositions(self):
        PathPositionsString = self.SendCommandToObiWithResponse('_PATHTIMES')
        CurrentPathPositions = [0, 0]
        CurrentPathPositionPieces = PathPositionsString.split(",")
        for iii in range (1, 3):
            CurrentPathPositions[iii-1] = int(CurrentPathPositionPieces[iii].strip())
        return CurrentPathPositions

