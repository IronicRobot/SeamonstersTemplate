__author__ = 'Dawson'
import wpilib
import math
class HolonomicDrive():
#PLEASE READ:
#Right side driving forward is assumed to be +1
#Turning counter-clockwise is assumed to be +1
#Meet these requriements and THEN use invertDrive() if it is all backwards.

#Summary:
#Turn should be passed in as -Joystick.getX, most likely


    def __init__(self, fl, fr, bl, br):
        self.FL = fl
        self.FR = fr
        self.BL = bl
        self.BR = br
        self.stores = [0.0, 0.0, 0.0, 0.0]
        self.encoderTargets = [0.0, 0.0, 0.0, 0.0]
        self.wheelOffset = math.pi / 4
        self.invert = 1
        self.maxVelocity = 2000
        self.previousDriveMode = 0

    #USE THESE FEW FUNCTIONS BELOW

    def driveVoltage(self, magnitude, direction, turn):
        self.ensureControlMode(wpilib.CANTalon.ControlMode.PercentVbus)
        self.calcWheels(magnitude, direction, turn)
        self.setWheels()
        self.previousDriveMode = 1
        #self.logCurrent()

    def driveSpeed(self, magnitude, direction, turn):
        self.ensureControlMode(wpilib.CANTalon.ControlMode.Speed)
        self.calcWheels(magnitude, direction, turn)
        self.scaleToMax()
        self.setWheels()
        self.previousDriveMode = 2
        #self.logCurrent()

    def driveSpeedJeffMode(self, magnitude, direction, turn): #Increments position to mock speed mode
        if (turn == 0 and magnitude == 0):
            self.disableTalons()
        elif self.FL.getControlMode() == wpilib.CANTalon.ControlMode.Disabled and self.FL.getControlMode() == wpilib.CANTalon.ControlMode.Disabled and\
            self.FL.getControlMode() == wpilib.CANTalon.ControlMode.Disabled and self.FL.getControlMode() == wpilib.CANTalon.ControlMode.Disabled:
            self.enableTalons()
            self.zeroEncoderTargets()
        self.ensureControlMode(wpilib.CANTalon.ControlMode.Position)
        if not self.previousDriveMode == 3:
            self.zeroEncoderTargets()
        self.calcWheels(magnitude, direction, turn)
        self.scaleToMaxJeffMode()
        self.incrementEncoderTargets()
        self.ensureSafeDistance()
        self.setWheelsJeffMode()
        self.previousDriveMode = 3

    def invertDrive(self):
        self.invert *= -1

    def setWheelOffset(self, angleInRadians):
        self.wheelOffset = angleInRadians

    def setMaxVelocity(self, velocity):
        self.maxVelocity = velocity

    #DO NOT USE THESE FUNCTIONS

    def calcWheels(self, magnitude, direction, turn):
        self.stores = [0.0, 0.0, 0.0, 0.0]
        self.addStrafe(magnitude, direction)
        self.addTurn(turn)
        self.scaleNumbers()
        #self.setWheels()

    def addStrafe(self, magnitude, direction):
        if magnitude > 1.0:
            fixedMagnitude = 1.0
        else:
            fixedMagnitude = magnitude
        self.stores[0] += fixedMagnitude * (math.sin(direction + self.wheelOffset)) * -1 #FL
        #self.stores[0] += fixedMagnitude
        self.stores[1] += fixedMagnitude * (math.sin((direction - self.wheelOffset))) #FR
        self.stores[2] += fixedMagnitude * (math.sin((direction - self.wheelOffset))) * -1 #BL
        self.stores[3] += fixedMagnitude * (math.sin((direction + self.wheelOffset))) #FR

    def addTurn(self, turn):
        for i in range (0,4):
            self.stores[i] += turn

    def scaleNumbers(self):
        largest = max(self.stores)
        if largest > 1:
            for number in self.stores:
                number = number / largest

    def incrementEncoderTargets(self):
        self.encoderTargets[0] += self.stores[0] * self.invert
        self.encoderTargets[1] += self.stores[1] * self.invert
        self.encoderTargets[2] += self.stores[2] * self.invert
        self.encoderTargets[3] += self.stores[3] * self.invert

    def setWheels(self):
        self.FL.set(self.stores[0] * self.invert)
        self.FR.set(self.stores[1] * self.invert)
        self.BL.set(self.stores[2] * self.invert)
        self.BR.set(self.stores[3] * self.invert)
        #print(str(self.stores[0])+ "     "+str(self.stores[1]) + "     "+ str(self.stores[2])+ "     " + str(self.stores[3]))

    def setWheelsJeffMode(self):
        self.FL.set(self.encoderTargets[0])
        self.FR.set(self.encoderTargets[1])
        self.BL.set(self.encoderTargets[2])
        self.BR.set(self.encoderTargets[3])

    def scaleToMax(self):
        for i in range (0,4):
            self.stores[i] *= self.maxVelocity

    def scaleToMaxJeffMode(self):
        for i in range (0,4):
            self.stores[i] *= self.maxVelocity / 5.0

    def ensureControlMode(self, controlMode):
        if self.FL.getControlMode() == self.FR.getControlMode() == self.BL.getControlMode() == self.BR.getControlMode() == controlMode:
            return
        print("SETTING CONTROL MODE")
        self.FL.changeControlMode(controlMode)
        self.FR.changeControlMode(controlMode)
        self.BL.changeControlMode(controlMode)
        self.BR.changeControlMode(controlMode)

    def logCurrent(self):
        print("FL Current: " + str(self.FL.getOutputCurrent()))
        print("FR Current: " + str(self.FR.getOutputCurrent()))
        print("BL Current: " + str(self.BL.getOutputCurrent()))
        print("BR Current: " + str(self.BR.getOutputCurrent()))

    def zeroEncoderTargets(self):
        self.encoderTargets[0] = self.FL.getEncPosition()
        self.encoderTargets[1] = self.FR.getEncPosition()
        self.encoderTargets[2] = self.BL.getEncPosition()
        self.encoderTargets[3] = self.BR.getEncPosition()

    def ensureSafeDistance(self):
        if abs(self.FL.getEncPosition() - self.encoderTargets[0]) > self.maxVelocity * 2.5:
            self.encoderTargets[0] = self.FL.getEncPosition()
        if abs(self.FR.getEncPosition() - self.encoderTargets[1]) > self.maxVelocity * 2.5:
            self.encoderTargets[1] = self.FR.getEncPosition()
        if abs(self.BL.getEncPosition() - self.encoderTargets[2]) > self.maxVelocity * 2.5:
            self.encoderTargets[2] = self.BL.getEncPosition()
        if abs(self.BR.getEncPosition() - self.encoderTargets[3]) > self.maxVelocity * 2.5:
            self.encoderTargets[3] = self.BR.getEncPosition()

    def enableTalons(self):
        self.FL.enable()
        self.FR.enable()
        self.BL.enable()
        self.BR.enable()

    def disableTalons(self):
        self.FL.disable()
        self.FR.disable()
        self.BL.disable()
        self.BR.disable()

