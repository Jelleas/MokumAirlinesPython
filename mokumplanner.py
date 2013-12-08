from __future__ import division

from mokum import Simulation
import pylab

def plotFuel(simulation):
	"""
	produces a plot of the fuel in the planes over the simulation with timesteps
	of 1 minute.
	"""

	print "Plotting fuel, this might take a while depending on the size of the simulation."

	planes = simulation.getPlanes()
	planeToFuel = {plane : [] for plane in planes}
	
	# note: producing a simulationLog is expensive, so make that your outer loop.
	for time in range(int(simulation.getEndTime())):
		simulationLog = simulation.getSimulationLogAt(time)
		planeToLog = simulationLog.getPlaneToLog()

		for plane in planes:
			planeToFuel[plane].append(planeToLog[plane].getFuel())

	for plane in planes:
		pylab.plot(range(len(planeToFuel[plane])), planeToFuel[plane], label=str(plane))

	pylab.title("Fuel in planes over the course of the simulation.")
	pylab.legend(loc="upper right")
	pylab.xlabel("Time (min)")
	pylab.ylabel("Fuel (km)")
	pylab.ylim(bottom = 0)
	pylab.savefig('fuel')

	print "Finished plotting fuel."

	pylab.show()

if __name__ == "__main__":

	# initialize the simulation, all data is loaded from files
	simulation = Simulation() 

	# pre compute the entire simulation, this will check all boundaries.
	simulation.preSimulation()

	planes = simulation.getPlanes() # all the planes in the simulation
	connections = simulation.getConnections() # all the connections in the simulation
	locations = simulation.getLocations() # all the locations in the simulation

	plotFuel(simulation)