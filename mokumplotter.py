from mokum import Simulation
import pylab

def plotFuel(simulation, fileName = 'fuel'):
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
		pylab.plot(range(len(planeToFuel[plane])), planeToFuel[plane], label = str(plane))

	pylab.title("Fuel in planes over the course of the simulation.")
	pylab.legend(loc = "upper right")
	pylab.xlabel("Time (min)")
	pylab.ylabel("Fuel (km)")
	pylab.ylim(bottom = 0)
	pylab.savefig(fileName)
	pylab.clf()

	print "Finished plotting fuel."

def plotPassengerKilometers(simulation, fileName = 'passengerkilometers'):
	"""
	produces a plot of the passenger kilometers in the planes over the 
	simulation with timesteps of 1 minute.
	"""

	print "Plotting passenger kilometers, this might take a while depending on the size of the simulation."

	planes = simulation.getPlanes()
	planeToPassengerKilometers = {plane : [] for plane in planes}

	# note: producing a simulationLog is expensive, so make that your outer loop.
	for time in range(int(simulation.getEndTime())):
		simulationLog = simulation.getSimulationLogAt(time)
		planeToLog = simulationLog.getPlaneToLog()

		for plane in planes:
			planeToPassengerKilometers[plane].append(planeToLog[plane].getPassengerKilometers())

	for plane in planes:
		pylab.plot(range(len(planeToPassengerKilometers[plane])), planeToPassengerKilometers[plane], label = str(plane))

	pylab.title("Passenger kilometers by planes over the course of the simulation.")
	pylab.legend(loc = "upper left")
	pylab.xlabel("Time (min)")
	pylab.ylabel("Passenger Kilometers")
	pylab.ylim(bottom = 0)
	pylab.savefig(fileName)
	pylab.clf()
	
	print "Finished plotting passenger kilometers."