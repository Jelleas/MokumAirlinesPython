from __future__ import division

from mokum import Simulation
import mokumplotter as plotter

if __name__ == "__main__":

	# initialize the simulation, all data is loaded from files
	simulation = Simulation() 

	planes = simulation.getPlanes() # all the planes in the simulation
	connections = simulation.getConnections() # all the connections in the simulation
	locations = simulation.getLocations() # all the locations in the simulation
	
	# ================================================================== #
	#                                                                    #
	#                         YOUR CODE GOES HERE!                       #
	#                                                                    #
	# ================================================================== #