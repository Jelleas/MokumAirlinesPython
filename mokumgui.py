import Tkinter as tk
import datetime as dt
#import threading
from mokum import *

master = tk.Tk()
colors = ["#ff0000", "#00ff00", "#0000ff", "#008000", "#ff00ff", "#00ffff"]
maxPlanes = len(colors)
deviationX = 10 # deviation from x-coord to image
deviationY = -30 # deviation from y-coord to image

class SimulationGUI(tk.Frame):              
    def __init__(self, simulation, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.simulation = simulation
        self.startTime = self.simulation.getStartTime()
        self.time = self.startTime
        self.endTime = self.simulation.getEndTime()                   
        self.createWidgets()
        
        planes = self.simulation.getSimulationLogAt(self.startTime).getPlaneToLog().keys()
        if len(planes) > maxPlanes:
            raise ValueError("Graphical simulation supports up to " + maxPlanes + " planes. " +\
                              str(len(planes)) + " planes given.")
        
        self.planeToColor = {}
        for i in range(len(planes)):
            self.planeToColor[planes[i]] = colors[i]
            
        self.figures = []
            
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
            self.drawSimulationAt(self.time)
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
        self.canvas.pack(expand = 'yes', fill = 'both')
        self.canvas.grid(columnspan=5)
        self.canvas.create_image(10, 10, image = image, anchor = 'nw')
        
    def drawSimulationAt(self, time):
        simulationLog = self.simulation.getSimulationLogAt(time) 
        planeToLog = simulationLog.getPlaneToLog()
        
        for figure in self.figures:
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
                self.figures.append(self.canvas.create_line(x1, y1, x2, y2, fill = self.planeToColor[plane], arrow = "last", width = 3.0))
            else:
                x, y = log.getCoords()
                x += deviationX
                y += deviationY
                self.figures.append(self.canvas.create_rectangle(x - 3, y - 3, x + 3, y + 3, fill = self.planeToColor[plane]))
            
        self.canvas.update()
        self.timeLabel.config(text = "time " + str(self.time))
        self.timeLabel.update()
            
image = tk.PhotoImage(file = "resources/europe.gif")
start = dt.datetime.now()
simulation = Simulation((500, 500))

simulation.preSimulation()
end = dt.datetime.now()
print "Time taken over presim", end - start
 
start = dt.datetime.now()
simulation.run()
end = dt.datetime.now()
 
print "Time taken over entire sim", end - start

app = SimulationGUI(simulation, master = master)
app.master.title('Mokum Airlines')
app.after(100, app.run)
app.start()

#simThread = threading.Thread(target = app.runSimulation)
#simThread.deamon = True
#simThread.start()
#
#guiThread = threading.Thread(target = app.start)
#guiThread.deamon = True
#guiThread.start()