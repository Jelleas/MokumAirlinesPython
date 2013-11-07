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
        if len(self.planes) > maxPlanes:
            raise ValueError("Graphical simulation supports up to " + maxPlanes + " planes. " +\
                              str(len(self.planes)) + " planes given.")
            
        if len(self.planes) == 0:
            raise ValueError("No planes to simulate.")
        
        self.planeToColor = {}
        for i in range(len(self.planes)):
            self.planeToColor[self.planes[i]] = colors[i]
            
        self.planeFigures = []
        
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
        if self.time == self.endTime:
            self.time = self.timeEntry.restartTime()
            app.after(10, app.run)
        else:
            self.time = self.timeEntry.restartTime()
    
    def pauseSimulation(self):
        self.isPaused = not self.isPaused
        
        if self.isPaused:
            self.pauseButton.config(text = "Resume")
        else:
            self.pauseButton.config(text = "Pause")
        
        self.timeEntry.pauseTimeEntry(self.isPaused)
        
        self.drawSimulation()
    
    def createWidgets(self):
        self.quitButton = tk.Button(self, text = 'Quit', command = self.quit)
        self.quitButton.grid(row = 0, column = 0)
        
        self.restartButton = tk.Button(self, text = "Restart", command = self.restartSimulation)
        self.restartButton.grid(row = 0, column = 1)
        
        self.pauseButton = tk.Button(self, text = "Pause", command = self.pauseSimulation)
        self.pauseButton.grid(row = 0, column = 2)
        
        self.canvas = tk.Canvas(self, width = 450, height = 450)
        self.canvas.grid(row = 1, column = 0, columnspan = 5, rowspan = 1)
        self.canvas.create_image(10, 10, image = image, anchor = 'nw')
        
        self.timeEntry = TimeEntry(self.isPaused, startTime = self.startTime, endTime = self.endTime,
                                    master = self, row = 0, column = 5)
        
        self.planeTable = PlaneTable(self.planeToColor, self.time, master = self, row = 1, column = 5)

    def drawSimulation(self):
        simulationLog = self.simulation.getSimulationLogAt(self.time) 
        planeToLog = simulationLog.getPlaneToLog()
        
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
                self.planeFigures.append(self.canvas.create_line(x1, y1, x2, y2, fill = self.planeToColor[plane], arrow = "last", width = 3.0))
            else:
                x, y = log.getCoords()
                x += deviationX
                y += deviationY
                self.planeFigures.append(self.canvas.create_rectangle(x - 3, y - 3, x + 3, y + 3, fill = self.planeToColor[plane]))
            
        self.canvas.update()

        self.planeTable.updatePlaneTable(self.time)

class TimeEntry(tk.Frame):
    def __init__(self, isPaused, startTime = 0, endTime = 1440, master = None, row = 0, column = 5):
        tk.Frame.__init__(self, master, colormap = "new")
        self.grid(row = row, column = column)
        self.master = master
        self.startTime = startTime
        self.time = self.startTime
        self.endTime = endTime
        self.isPaused = isPaused
        self._createTimeEntry()
        
    def _createTimeEntry(self):
        self.timeLabel = tk.Label(self, text = "time:")
        self.timeLabel.grid(row = 0, column = 0)
        
        self.timeEntry = tk.Entry(self)
        self.timeEntry.delete(0, tk.END)
        self.timeEntry.insert(0, "time " + str(self.time))
        
        if not self.isPaused:
            self.timeEntry.config(state = "readonly")
        
        self.timeEntry.grid(row = 0, column = 1)
        
        self.setButton = tk.Button(self, text = "Set", command = self.setTime)
        self.setButton.grid(row = 0, column = 2)
    
    def pauseTimeEntry(self, isPaused):
        if self.isPaused != isPaused:
            self.isPaused = isPaused
            
            if self.isPaused:
                self.timeEntry.config(state = tk.NORMAL)
            else:
                self.timeEntry.config(state = "readonly")
                self.setTime()
                
        return self.time
    
    def restartTime(self):
        self.time = self.startTime
        return self.time
    
    def nextTime(self):
        if self.startTime <= self.time + 1 < self.endTime:
            self.time += 1
            self._updateTimeEntry()
        return self.time
    
    def _updateTimeEntry(self):
        # TODO ugly solution, fix?
        if not self.isPaused:
            self.timeEntry.config(state = tk.NORMAL)
            self.timeEntry.delete(0, tk.END)
            self.timeEntry.insert(0, str(self.time))
            self.timeEntry.config(state = "readonly")
        else:
            self.timeEntry.delete(0, tk.END)
            self.timeEntry.insert(0, str(self.time))
            
        self.timeEntry.update()
    
    def getTime(self):
        return self.time
    
    def setTime(self):
        if self._isValidTime():
            self.time = int(self.timeEntry.get())
        else:
            raise ValueError("Illegal time: " + self.timeEntry.get() + " set.")
        
    def _isValidTime(self):
        try:
            time = int(self.timeEntry.get())
        except ValueError:
            return False
        
        if self.startTime <= time < self.endTime:
            return True
        else:
            return False
                
class PlaneTable(tk.Frame):
    def __init__(self, planeToColor, time = 0, master = None, row = 1, column = 5):
        tk.Frame.__init__(self, master, width = 100, height = 450, bg = "black", colormap = "new")
        self.grid(row = row, column = column)
        self.master = master
        self.planes = planeToColor.keys()
        self.planeToColor = planeToColor
        self.currentPlaneNum = 0
        self.currentPlane = self.planes[self.currentPlaneNum]
        self.time = time
        self._createPlaneTable()
        
    def nextPlane(self):
        self.currentPlaneNum = (self.currentPlaneNum + 1) % len(self.planes)
        self.currentPlane = self.planes[self.currentPlaneNum]
        self.updatePlaneTable(self.time)
        
    def _createPlaneTable(self):
        plane = self.currentPlane
        self.tableEntries = []
        
        self.nextPlaneButton = tk.Button(self, text = "Next Plane", command = self.nextPlane)
        self.nextPlaneButton.grid(row = 1, column = 0, columnspan = 2, sticky = "nsew", padx = 1, pady = 1)
        
        label = tk.Label(self, text = str(plane), borderwidth = 0, width = 10, fg = self.planeToColor[self.currentPlane])
        label.grid(row = 0, column = 0, columnspan = 2, sticky = "nsew", padx = 1, pady = 1)
        
        self.tableTitle = label
        
        # passengers as a list of tuples [(endLocation, numPassengers)]
        passengers = plane.getPassengersAt(self.time).items()
        passengersLength = len(passengers)
        
        for i in range(passengersLength):
            currentRow = []
            passenger = passengers[i]
            
            for j in range(2):
                label = tk.Label(self, text = str(passenger[j]), borderwidth = 0, width = 10)
                label.grid(row = i + 2, column = j, sticky = "nsew", padx = 1, pady = 1)
                currentRow.append(label)
            self.tableEntries.append(currentRow)
        
        for i in range(passengersLength, numTableRows):
            currentRow = []
            
            for j in range(2):
                label = tk.Label(self, text = "", borderwidth = 0, width = 10)
                label.grid(row = i + 2, column = j, sticky = "nsew", padx = 1, pady = 1)
                currentRow.append(label)
            self.tableEntries.append(currentRow)
                
    def updatePlaneTable(self, time):
        self.time = time
        
        plane = self.currentPlane
        
        self.tableTitle.config(text = str(plane), fg = self.planeToColor[self.currentPlane])
        
        # passengers as list of tuples [(endLocation, numPassengers)]
        passengers = plane.getPassengersAt(self.time).items()
        passengersLength = len(passengers)
        
        for i in range(passengersLength):
            currentRow = self.tableEntries[i]
            passenger = passengers[i]
            
            for j in range(2):
                tableEntry = currentRow[j]
                tableEntry.config(text = str(passenger[j]))
        
        for i in range(passengersLength, numTableRows):
            currentRow = self.tableEntries[i]
            
            for j in range(2):
                tableEntry = currentRow[j]
                tableEntry.config(text = "")
                
        self.update()
        
if __name__ == "__main__":
    start = dt.datetime.now()
    simulation = Simulation((500, 500))
    end = dt.datetime.now()
    print "Time taken over simulation initialization ", end - start
    
    start = dt.datetime.now()
    simulation.preSimulation()
    end = dt.datetime.now()
    print "Time taken over pre simulation", end - start
     
    start = dt.datetime.now()
    simulation.run() # pre computation of the entire simulation, speeds the visualization up
    end = dt.datetime.now()
    print "Time taken over simulation", end - start
    
    image = tk.PhotoImage(file = "resources/europe.gif")
    app = SimulationGUI(simulation, master = master)
    app.master.title('Mokum Airlines')
    app.after(100, app.run)
    app.start()