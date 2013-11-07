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
    def __init__(self, simulation, master=None):
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
        
        self.currentPlaneNum = 0
        self.currentPlane = self.planes[self.currentPlaneNum]
        
        self.planeToColor = {}
        for i in range(len(self.planes)):
            self.planeToColor[self.planes[i]] = colors[i]
            
        self.planeFigures = []
        
        self.createWidgets()

    def start(self):
        self.mainloop()

    def restartSimulation(self):
        if self.time == self.endTime:
            self.time = self.startTime
            app.after(100, app.run)
        else:
            self.time = self.startTime

    def run(self):
        if self.time < self.endTime:
            self.drawSimulationAt()
            self.time += 1
            self.after(1, self.run)

    def createWidgets(self):
        self.quitButton = tk.Button(self, text = 'Quit', command = self.quit)
        self.quitButton.grid(row = 0, column = 0)
        
        self.restartButton = tk.Button(self, text = "Restart", command = self.restartSimulation)
        self.restartButton.grid(row = 0, column = 1)
        
        self.timeLabel = tk.Label(self, text="time " + str(self.time))
        self.timeLabel.grid(row = 0, column = 4)
        
        self.canvas = tk.Canvas(self, width=450, height=450)
        self.canvas.grid(row = 1, column = 0, columnspan = 5, rowspan = 1)
        self.canvas.create_image(10, 10, image = image, anchor = 'nw')
        
        self.createPlaneTable()
        #self.updatePlaneTable(plane)
    
    def createPlaneTable(self):
        plane = self.currentPlane
        
        frame = tk.Frame(width = 100, height = 450, bg="black", colormap="new")
        frame.grid(row = 0, column = 4) # TODO weird location?
        self.table = frame
        self.tableEntries = []
        
        self.nextPlaneButton = tk.Button(self.table, text = "Next Plane", command = self.nextPlane)
        self.nextPlaneButton.grid(row = 1, column = 0, columnspan = 2, sticky = "nsew", padx = 1, pady = 1)
        
        label = tk.Label(self.table, text = str(plane), borderwidth = 0, width = 10)
        label.grid(row = 0, column = 0, columnspan = 2, sticky = "nsew", padx = 1, pady = 1)
        
        self.tableTitle = label
        
        # passengers as list of tuples [(endLocation, numPassengers)]
        passengers = plane.getPassengersAt(self.time).items()
        passengersLength = len(passengers)
        
        for i in range(passengersLength):
            currentRow = []
            passenger = passengers[i]
            
            for j in range(2):
                label = tk.Label(self.table, text = str(passenger[j]), borderwidth = 0, width = 10)
                label.grid(row = i + 2, column = j, sticky = "nsew", padx = 1, pady = 1)
                currentRow.append(label)
            self.tableEntries.append(currentRow)
        
        for i in range(passengersLength, numTableRows):
            currentRow = []
            
            for j in range(2):
                label = tk.Label(frame, text = "", borderwidth = 0, width = 10)
                label.grid(row = i + 2, column = j, sticky = "nsew", padx = 1, pady = 1)
                currentRow.append(label)
            self.tableEntries.append(currentRow)
            
    def updatePlaneTable(self):
        plane = self.currentPlane
        
        self.tableTitle.config(text = str(plane))
        
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
                
        self.table.update()
            
    def drawSimulationAt(self):
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
        self.timeLabel.config(text = "time " + str(self.time))
        self.timeLabel.update()
        
        # TODO, does not need to be updated every iteration.
        self.updatePlaneTable()
        
    def nextPlane(self):
        self.currentPlaneNum = (self.currentPlaneNum + 1) % len(self.planes)
        self.currentPlane = self.planes[self.currentPlaneNum]
        self.updatePlaneTable()
        
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