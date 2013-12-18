from __future__ import division

from mokum import Simulation
import mokumplotter as plotter

if __name__ == "__main__":

	# initialize the simulation, all data is loaded from files
	simulation = Simulation() 

	# pre compute the entire simulation, this will check all boundaries.
	simulation.preSimulation()

	planes = simulation.getPlanes() # all the planes in the simulation
	connections = simulation.getConnections() # all the connections in the simulation
	locations = simulation.getLocations() # all the locations in the simulation
	
	# ================================================================== #
	#                                                                    #
	#                         YOUR CODE GOES HERE!                       #
	#                                                                    #
	# ================================================================== #




	# ================================================================== #
	#                                                                    #
	#                              EXAMPLES!                             #
	#                                                                    #
	# ================================================================== #

	# creates a plot of the fuel consumption of each plane saved in fuel.png
	plotter.plotFuel(simulation) 

	# creates a plot of the passenger kilometers made by each plane 
	# saved in passengerkilometers.png
	plotter.plotPassengerKilometers(simulation)


	# Get the state of simulation after 100 minutes and 15 seconds:
	simLog = simulation.getSimulationLogAt(100.25)

	# Lets check what planes are flying at time 100.25.
	for planeLog in simLog.getPlaneLogs():
		trip = planeLog.getTrip()
		plane = planeLog.getPlane()

		# To see whether a plane is flying we just need to check
		# if the log contains a trip.
		if trip == None:
			print "Plane %s is not flying!" %(plane)
		else:
			print "Plane %s is flying on trip: %s!" %(plane, trip)