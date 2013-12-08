from __future__ import division

import Tkinter as tk
import datetime as dt
from mokum import Simulation

master = tk.Tk()
colors = ["#ff0000", "#00ff00", "#0000ff", "#008000", "#ff00ff", "#00ffff"]
maxPlanes = len(colors)
deviationX = 10 # deviation from x coordinate to image
deviationY = -30 # deviation from y coordinate to image
numTableRows = 10

class SimulationGUI(tk.Frame):              
    def __init__(self, simulation, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.simulation = simulation
        self.startTime = self.simulation.getStartTime()
        self.time = self.startTime
        self.endTime = self.simulation.getEndTime()
        self.planes = self.simulation.getPlanes()
        self.simulationLog = self.simulation.getSimulationLogAt(self.time)

        if len(self.planes) > maxPlanes:
            raise ValueError("Graphical simulation supports up to " + str(maxPlanes) + " planes. " +\
                              str(len(self.planes)) + " planes given.")
            
        if len(self.planes) == 0:
            raise ValueError("No planes to simulate.")
        
        self.planeToColor = {}
        for i in range(len(self.planes)):
            self.planeToColor[self.planes[i]] = colors[i]
            
        self.planeFigures = []
        
        self.locations = self.simulation.getLocations()
        
        self.isPaused = False
        
        self.createWidgets()

    def start(self):
        self.mainloop()

    def run(self):
        if self.isPaused:
            time = self.timeEntry.getTime()
            if time != self.time:
                self.time = time
                self.drawSimulation()
        
        elif self.time < self.endTime:
            self.time = self.timeEntry.nextTime()
            self.drawSimulation()

        self.after(10, self.run)

    def restartSimulation(self):
        self.pause(False)
        self.time = self.timeEntry.restartTime()

    def togglePause(self):
        self.pause(not self.isPaused)

    def pause(self, isPaused):
        self.isPaused = isPaused
        
        if self.isPaused:
            self.pauseButton.config(text = "Resume")
        else:
            self.pauseButton.config(text = "Pause")
        
        self.timeEntry.pause(self.isPaused)
        
        self.drawSimulation()
    
    def createWidgets(self):
        self.quitButton = tk.Button(self, text = 'Quit', command = self.quit)
        self.quitButton.grid(row = 0, column = 0)
        
        self.restartButton = tk.Button(self, text = "Restart", command = self.restartSimulation)
        self.restartButton.grid(row = 0, column = 1)
        
        self.pauseButton = tk.Button(self, text = "Pause", command = self.togglePause)
        self.pauseButton.grid(row = 0, column = 2)
        
        self.canvas = tk.Canvas(self, width = 450, height = 450)
        self.canvas.grid(row = 1, column = 0, columnspan = 5, rowspan = 1)
        self.canvas.create_image(10, 10, image = image, anchor = 'nw')
        
        self.timeEntry = TimeEntry(self.isPaused, startTime = self.startTime, endTime = self.endTime,
                                    master = self)
        self.timeEntry.grid(row = 0, column = 5)
        
        self.planeTable = PlaneTable(self.planeToColor, self.simulationLog, master = self)
        self.planeTable.grid(row = 1, column = 5)

        self.locationTable = LocationTable(self.locations, self.simulationLog, master = self)
        self.locationTable.grid(row = 1, column = 6)

    def drawSimulation(self):
        self.simulationLog = self.simulation.getSimulationLogAt(self.time)
        planeToLog = self.simulationLog.getPlaneToLog()
        
        for figure in self.planeFigures:
            self.canvas.delete(figure)
       
        for plane, log in planeToLog.iteritems():
            trip = log.getTrip()
            if trip != None:
                x1, y1 = trip.getConnection().getStartLocation().getCoords()
                x2, y2 = log.getCoords()
                x1 += deviationX
                x2 += deviationX
                y1 += deviationY
                y2 += deviationY
                lineId = self.canvas.create_line(x1, y1, x2, y2, fill = self.planeToColor[plane],
                                                  arrow = "last", width = 3.0)
                self.planeFigures.append(lineId)
            else:
                x, y = log.getCoords()
                x += deviationX
                y += deviationY
                rectangleId = self.canvas.create_rectangle(x - 3, y - 3, x + 3, y + 3,
                                                            fill = self.planeToColor[plane])
                self.planeFigures.append(rectangleId)
            
        self.canvas.update()

        self.planeTable.updatePlaneTable(self.simulationLog)
        self.locationTable.updateLocationTable(self.simulationLog)

class TimeEntry(tk.Frame):
    def __init__(self, isPaused, startTime = 0, endTime = 1440, master = None):
        tk.Frame.__init__(self, master, colormap = "new")
        self.master = master
        self.startTime = startTime
        self.time = self.startTime
        self.endTime = endTime
        self.isPaused = isPaused
        self.timeStep = .1
        self._createTimeEntry()
        
    def _createTimeEntry(self):
        self.timeLabel = tk.Label(self, text = "time:")
        self.timeLabel.grid(row = 0, column = 0)
        
        self.slowDownButton = tk.Button(self, text = "<<", command = self.slowDown)
        self.slowDownButton.grid(row = 0, column = 1)

        self.timeEntry = tk.Entry(self, width = 15)
        self.timeEntry.delete(0, tk.END)
        self.timeEntry.insert(0, str(self.time))
        if not self.isPaused:
            self.timeEntry.config(state = "readonly")
        self.timeEntry.grid(row = 0, column = 2)
        self.timeEntry.bind("<Return>", self.onSetTime)
        
        self.timeStepEntry = tk.Entry(self, width = 10)
        self.timeStepEntry.delete(0, tk.END)
        self.timeStepEntry.insert(0, str(self.timeStep))
        if not self.isPaused:
            self.timeStepEntry.config(state = "readonly")
        self.timeStepEntry.grid(row = 0, column = 3)
        self.timeStepEntry.bind("<Return>", self.onSetTimeStep)

        self.speedUpButton = tk.Button(self, text = ">>", command = self.speedUp)
        self.speedUpButton.grid(row = 0, column = 4)
        
    def pause(self, isPaused):
        if self.isPaused != isPaused:
            self.isPaused = isPaused
            
            if self.isPaused:
                self.timeEntry.config(state = tk.NORMAL)
                self.timeStepEntry.config(state = tk.NORMAL)
            else:
                self.timeEntry.config(state = "readonly")
                self.timeStepEntry.config(state = "readonly")
                self.setTime()
                
        return self.time
    
    def restartTime(self):
        self.time = self.startTime
        return self.time
    
    def nextTime(self):
        if self.startTime <= self.time + self.timeStep < self.endTime:
            self.time += self.timeStep
            self._updateTimeEntry()
        return self.time
    
    def speedUp(self):
        self.timeStep += .1
        
        if -.1 < self.timeStep < .1:
            self.timeStep += .1

        self._updateTimeEntry()
        
    def slowDown(self):
        self.timeStep -= .1
        
        if -.1 < self.timeStep < .1:
            self.timeStep -= .1

        self._updateTimeEntry()
    
    def _updateTimeEntry(self):
        # TODO ugly solution, fix?
        if not self.isPaused:
            self.timeEntry.config(state = tk.NORMAL)
            self.timeEntry.delete(0, tk.END)
            self.timeEntry.insert(0, str(self.time))
            self.timeEntry.config(state = "readonly")

            self.timeStepEntry.config(state = tk.NORMAL)
            self.timeStepEntry.delete(0, tk.END)
            self.timeStepEntry.insert(0, str(self.timeStep))
            self.timeStepEntry.config(state = "readonly")
        else:
            self.timeEntry.delete(0, tk.END)
            self.timeEntry.insert(0, str(self.time))

            self.timeStepEntry.delete(0, tk.END)
            self.timeStepEntry.insert(0, str(self.timeStep))
            
        self.timeEntry.update()
    
    def getTime(self):
        return self.time
    
    def onSetTimeStep(self, event):
        self.setTimeStep()

    def setTimeStep(self):
        if self._isValidTimeStep():
            self.timeStep = float(self.timeStepEntry.get())
        else:
            raise ValueError("Illegal timestep " + self.timeStepEntry.get() + " set")

    def _isValidTimeStep(self):
        try:
            timeStep = float(self.timeStepEntry.get())
        except ValueError:
            return False

        epsilon = .00001
        return not -epsilon < timeStep < epsilon

    def onSetTime(self, event):
        self.setTime()
    
    def setTime(self):
        if self._isValidTime():
            self.time = float(self.timeEntry.get())
        else:
            raise ValueError("Illegal time: " + self.timeEntry.get() + " set.")
        
    def _isValidTime(self):
        try:
            time = float(self.timeEntry.get())
        except ValueError:
            return False
        
        return self.startTime <= time < self.endTime
                
class PlaneTable(tk.Frame):
    def __init__(self, planeToColor, simulationLog, master = None):
        tk.Frame.__init__(self, master, bg = "black", colormap = "new")
        self.master = master
        self.planes = planeToColor.keys()
        self.planeToColor = planeToColor
        self.currentPlaneNum = 0
        self.currentPlane = self.planes[self.currentPlaneNum]
        self.time = simulationLog.getTime()
        self.simulationLog = simulationLog
        self._createPlaneTable()
        
    def nextPlane(self):
        self._setPlane((self.currentPlaneNum + 1) % len(self.planes))
        
    def previousPlane(self):
        planesLength = len(self.planes)
        self._setPlane((planesLength + (self.currentPlaneNum - 1)) % planesLength)
        
    def _setPlane(self, planeNum):
        self.currentPlaneNum = planeNum
        self.currentPlane = self.planes[self.currentPlaneNum]
        self.updatePlaneTable(self.simulationLog)
        
    def _createPlaneTable(self):
        plane = self.currentPlane
        planeLog = self.simulationLog.getPlaneLog(plane)

        self.tableEntries = []
        
        self.titleLabel = tk.Label(self, text = str(plane), borderwidth = 0, fg = self.planeToColor[self.currentPlane])
        self.titleLabel.grid(row = 0, column = 0, columnspan = 2, sticky = "nsew", padx = 1, pady = 1)
        
        self.buttonFrame = tk.Frame(self)
        self.buttonFrame.grid(row = 1, column = 0, columnspan = 2, sticky = "nsew", padx = 1, pady = 1)
         
        self.previousPlaneButton = tk.Button(self.buttonFrame, text = "Previous Plane", command = self.previousPlane, width = 18)
        self.previousPlaneButton.grid(row = 0, column = 0, sticky = "nsew", padx = 1, pady = 1)
        
        self.nextPlaneButton = tk.Button(self.buttonFrame, text = "Next Plane", command = self.nextPlane, width = 18)
        self.nextPlaneButton.grid(row = 0, column = 1, sticky = "nsew", padx = 1, pady = 1)
       
        passengerKilometersString = str("Passenger Kilometers: %d" %(planeLog.getPassengerKilometers()))
        self.passengerKilometersLabel = tk.Label(self, text = passengerKilometersString, borderwidth = 0)
        self.passengerKilometersLabel.grid(row = 2, column = 0, columnspan = 2, sticky = "nsew", padx = 1, pady = 1)
        
        self.fuelLabel = tk.Label(self, text = str("Fuel: %.2f" %(planeLog.getFuel())), borderwidth = 0)
        self.fuelLabel.grid(row = 3, column = 0, columnspan = 2, sticky = "nsew", padx = 1, pady = 1)
        
        # passengers {connection:numPassengers} as list of tuples [(connection, numPassengers)]
        passengers = planeLog.getPassengers().items()
        passengersLength = len(passengers)
        
        for i in range(passengersLength):
            currentRow = []
            passenger = passengers[i]
            
            label = tk.Label(self, text = str(passenger[0]), borderwidth = 0, width = 30)
            label.grid(row = i + 4, column = 0, sticky = "nsew", padx = 1, pady = 1)
            currentRow.append(label)
            
            label = tk.Label(self, text = str(passenger[1]), borderwidth = 0, width = 6)
            label.grid(row = i + 4, column = 1, sticky = "nsew", padx = 1, pady = 1)
            currentRow.append(label)
            
            self.tableEntries.append(currentRow)
        
        for i in range(passengersLength, numTableRows):
            currentRow = []
            
            label = tk.Label(self, text = "", borderwidth = 0, width = 30)
            label.grid(row = i + 4, column = 0, sticky = "nsew", padx = 1, pady = 1)
            currentRow.append(label)
            
            label = tk.Label(self, text = "", borderwidth = 0, width = 5)
            label.grid(row = i + 4, column = 1, sticky = "nsew", padx = 1, pady = 1)
            currentRow.append(label)
            
            self.tableEntries.append(currentRow)
                
    def updatePlaneTable(self, simulationLog):
        self.simulationLog = simulationLog
        self.time = simulationLog.getTime()

        plane = self.currentPlane
        planeLog = self.simulationLog.getPlaneLog(plane)
        
        self.titleLabel.config(text = str(plane), fg = self.planeToColor[self.currentPlane])
        passengerKilometersString = str("Passenger Kilometers: %d" %(planeLog.getPassengerKilometers()))
        self.passengerKilometersLabel.config(text = passengerKilometersString)
        self.fuelLabel.config(text = str("Fuel: %.2f" %(planeLog.getFuel())))
        
        # passengers {connection:numPassengers} as list of tuples [(connection, numPassengers)]
        passengers = planeLog.getPassengers().items()
        passengersLength = len(passengers)
        
        for i in range(passengersLength):
            currentRow = self.tableEntries[i]
            passenger = passengers[i]
            
            for j in range(2):
                currentRow[j].config(text = str(passenger[j]))
        
        for i in range(passengersLength, numTableRows):
            currentRow = self.tableEntries[i]
            
            for j in range(2):
                currentRow[j].config(text = "")
                
        self.update()

# TODO, LocationTable makes the 'stupid' assumption every location has the same amount of connections, fix?  
class LocationTable(tk.Frame):
    def __init__(self, locations, simulationLog, master = None):
        tk.Frame.__init__(self, master, bg = "black", colormap = "new")
        self.master = master
        
        if len(locations) == 0:
            raise ValueError("No locations found to display, len(locations) == 0")
        
        self.locations = locations
        self.time = simulationLog.getTime()
        self.simulationLog = simulationLog
        self.currentLocationNum = 0
        self.currentLocation = self.locations[self.currentLocationNum]
        self.tableEntries = []
        
        self._createLocationTable()
        
    def _createLocationTable(self):
        self.titleLabel = tk.Label(self, text = str(self.currentLocation), borderwidth = 0)
        self.titleLabel.grid(row = 0, column = 0, columnspan = 2, sticky = "nsew", padx = 1, pady = 1)
        
        self.buttonFrame = tk.Frame(self)
        self.buttonFrame.grid(row = 1, column = 0, columnspan = 2, sticky = "nsew", padx = 1, pady = 1)
         
        self.previousLocationButton = tk.Button(self.buttonFrame, text = "Previous Location",
                                              command = self.previousLocation, width = 18)
        self.previousLocationButton.grid(row = 0, column = 0, sticky = "nsew", padx = 1, pady = 1)
        
        self.nextLocationButton = tk.Button(self.buttonFrame, text = "Next Location",
                                          command = self.nextLocation, width = 18)
        self.nextLocationButton.grid(row = 0, column = 1, sticky = "nsew", padx = 1, pady = 1)
        
        connectionToLog = self.simulationLog.getConnectionToLog()
        for i, connection in enumerate(self.currentLocation.getConnections()):
            currentRow = []
            
            label = tk.Label(self, text = str(connection), borderwidth = 0, width = 30)
            label.grid(row = i + 2, column = 0, sticky = "nsew", padx = 1, pady = 1)
            currentRow.append(label)
            
            label = tk.Label(self, text = str(connectionToLog[connection].getPotentialPassengers()),
                              borderwidth = 0, width = 6)
            label.grid(row = i + 2, column = 1, sticky = "nsew", padx = 1, pady = 1)
            currentRow.append(label)
            
            self.tableEntries.append(currentRow)
    
    def updateLocationTable(self, simulationLog):
        self.time = simulationLog.getTime()
        self.simulationLog = simulationLog
        self.titleLabel.config(text = str(self.currentLocation))
        
        connectionToLog = simulationLog.getConnectionToLog()

        for i, connection in enumerate(self.currentLocation.getConnections()):
            currentRow = self.tableEntries[i]
            
            currentRow[0].config(text = str(connection))
            currentRow[1].config(text = str(connectionToLog[connection].getPotentialPassengers()))
     
    def nextLocation(self):
        self._setLocation((self.currentLocationNum + 1) % len(self.locations))
        
    def previousLocation(self):
        locationsLength = len(self.locations)
        self._setLocation((locationsLength + (self.currentLocationNum - 1)) % locationsLength)
        
    def _setLocation(self, locationNum):
        self.currentLocationNum = locationNum
        self.currentLocation = self.locations[self.currentLocationNum]
        self.updateLocationTable(self.simulationLog)
        
if __name__ == "__main__":
    start = dt.datetime.now()
    simulation = Simulation((500, 500))
    end = dt.datetime.now()
    print "Time taken over simulation initialization ", end - start
    
    start = dt.datetime.now()
    simulation.preSimulation()
    end = dt.datetime.now()
    print "Time taken over pre simulation", end - start
     
    #start = dt.datetime.now()
    #simulation.run() # pre computation of the entire simulation, speeds the visualization up
    #end = dt.datetime.now()
    #print "Time taken over simulation", end - start
    
    image = tk.PhotoImage(file = "resources/europe.gif")
    gui = SimulationGUI(simulation, master = master)
    gui.master.title('Mokum Airlines')
    gui.after(100, gui.run)
    gui.start()