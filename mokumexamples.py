from __future__ import division

from mokum import Simulation, Trip
import mokumplotter as plotter
import random
import mokumgui as gui

if __name__ == "__main__":

	# initialize the simulation, all data is loaded from files
	simulation = Simulation()

	planes = simulation.getPlanes() # all the planes in the simulation
	connections = simulation.getConnections() # all the connections in the simulation
	locations = simulation.getLocations() # all the locations in the simulation

	# ================================================================== #
	#                                                                    #
	#                              EXAMPLES!                             #
	#                                                                    #
	# ================================================================== #

	# Get the state of simulation after 100 minutes and 15 seconds:
	simLog = simulation.getSimulationLogAt(100.25)

	# Lets check which planes are flying at time 100.25.
	for planeLog in simLog.getPlaneLogs():
		trip = planeLog.getTrip()
		plane = planeLog.getPlane()

		# To see whether a plane is flying we just need to check
		# if the log contains a trip.
		if trip is None:
			print "Plane %s is not flying!" %(plane)
		else:
			print "Plane %s is flying on trip: %s!" %(plane, trip)

	# So that is how you get data from the simulation. Now to insert data into
	# the simulation you have to modify the files in the resources folder.
	# See the readme for the syntax.
	# There is an exception however, trips can be added and removed dynamically!
	# The simulation object has already read the files in the resources folder,
	# so lets remove one trip of one of the planes.

	# First lets pick a plane
	plane = planes[0]

	# For comparison lets see what passengerkilometers the plane makes before
	# removing one of its trips. We can do that in two ways, either by creating
	# the planelog for just this plane, or by creating a log of complete
	# simulation. Both ways are shown below.

	endTime = simulation.getEndTime()
	
	# 1. Create just the planelog for this plane
	planeLog = plane.getPlaneLogAt(endTime)

	# 2. Create an entire simulationlog and pick our planelog from it.
	simLog = simulation.getSimulationLogAt(endTime)
	planeLog = simLog.getPlaneLog(plane)

	# So what passengerkilometers does this plane make?
	print "Passengerkilometers made %f by %s." %(planeLog.getPassengerKilometers(), plane)

	# Now Lets pick a trip and remove it.
	trip = plane.getTrips()[0]
	isTripRemoved = plane.removeTrip(trip)
	if isTripRemoved:
		print "Trip " + str(trip) + " removed succesfully!"
	else:
		print "Trip " + str(trip) + " was not removed." 

	# Okay, so the trip is gone, how many passengerkilometers
	# does the plane make now? The old planelog is no longer valid as
	# we just modified the simulation, thus we have to create a new one.
	planeLog = plane.getPlaneLogAt(endTime)
	print "Passengerkilometers made %f by %s." %(planeLog.getPassengerKilometers(), plane)

	# But wait, the trip we just removed was actually the first trip.
	# So the start location will no longer match the end location. We probably
	# have to check this. For this the preSimulation exists, which runs 
	# the entire simulation but searches for errors and checks to see if 
	# constraints are matched.
	try:
		simulation.preSimulation()
	except ValueError, e:
		print "Oh no, constraints aren't being matched: " + str(e)

	# So we just broke the simulation. Lets go fix it. 
	# Lets put the trip back.
	plane.addTrip(trip)

	# Lets quickly check if the simulation still matches the constraints.
	simulation.preSimulation()

	# Yup all good. Okay, so we removed an existing trip and put it back.
	# Now lets add a new trip.
	# First we have to create a new trip.
	# In order to create a new trip we need a few things namely:
	# 1. a unique name
	# 2. a start time (in minutes)
	# 3. a connection where the trip travels over
	# 4. passengers, a dictionary with connections as keys and
	# an integer indicating number of passengers
	# 5. a boolean refuel indicating whether the plane should refuel
	# Lets go and get all that. 

	# First a unique name, I suggest you stick
	# to some convention for instance just numbering your trips like so,
	# then we can get a name like so:
	name = "trip" + str(len(simulation.getTrips()) + 1)

	# A starttime, difficult as our plane already has some trips
	# planned, so lets calculate when the last one ends, and start
	# the new trip at this time.
	# You have to pass a plane to get an endtime, planes can fly
	# at different speeds, atleast the simulation allows it.
	lastTrip = plane.getTrips()[-1]
	startTime = lastTrip.getEndTime(plane)

	# Now we need a connection, its important that our plane is at
	# the start location of the connection.	Else the pre simulation
	# will raise an exception. So lets get that.
	connections = simulation.getConnectionsByStart(lastTrip.getEndLocation())

	# Now lets just take a connection, and to spice it up: randomly.
	# Note the import random at the top of this file, i just create
	# an object of the class Random and use its choice function.
	randomGen = random.Random()
	connection = randomGen.choice(connections)

	# Okay, random is pretty awfull for demonstration purposes.
	# So lets seed the Random object so we get consistent results!
	randomGen.seed(0)
	connection = randomGen.choice(connections)

	# Three down, two to go. Passengers, we can take extra passengers.
	# Meaning if the plane flies from Madrid to Berlin, the plane can 
	# also take some extra passengers to Amsterdam. These extra passengers
	# remain in the plane, untill the plane lands on the correct location
	# thus in this case Amsterdam. But to simplify things now, lets just
	# take some passengers for our connection.
	# Okay, first lets see how many passengers the plane can take, remember
	# there might be some extra passengers already loaded on the plane as 
	# just explained above.
	# Okay first we need a planelog.
	planeLog = plane.getPlaneLogAt(startTime)

	# Lets get the numbers.
	numPassengersOnPlane = planeLog.getNumPassengers()
	maxPassengers = plane.getMaxPassengers()
	
	# Now lets construct the passengers dictionary, and fill our plane up.
	passengers = {connection : maxPassengers - numPassengersOnPlane}

	# What if, we are requesting more passengers than there actually
	# willing to travel. Okay lets fix this. For this we need a 
	# connectionLog. As planes fly over connections, less and less
	# passengers are willing to fly. So we need this log.
	# Note: the connection log needs all the planes, for it to
	# create a correct log.
	conLog = connection.getConnectionLogAt(startTime, planes)

	# Right, now lets see how many passengers are willing to travel,
	# I call these potential passengers.
	potentialPassengers = conLog.getPotentialPassengers()

	# Now lets fix our possible mistake.
	if passengers[connection] > potentialPassengers:
		passengers[connection] = potentialPassengers

	# Okay, four down, one to go. This one is tricky. As we will probably
	# not want to refuel after our trip, but rather before. Only this
	# is not set in this trip, but the previous!
	# So lets set this if needed.
	if planeLog.getFuel() < connection.getDistance():
		lastTrip.setRefuel(True)

	# Well, the problem is by changing this refuel the startTime of this
	# trip has changed, so we need to adjust it.
	startTime = lastTrip.getEndTime(plane)

	# Now lets set the refuel for the trip we are about to create on false.
	refuel = False

	# Alright. The new trip!
	trip = Trip(name, startTime, connection, passengers, refuel)

	# Lets add this to the plane, and see if all is still good.
	plane.addTrip(trip)

	try:
		simulation.preSimulation()
	except ValueError, e:
		print "Oh no, constraints aren't being matched: " + str(e)

	# Yes, we need another trip, as the end location does not match
	# the start location anymore. But hey, it's just a proof of concept!
	# So lets just remove the trip we added.
	plane.removeTrip(trip)
	
	# If our modified flightplan turned out be a success we can save it by calling:
	#simulation.saveToFiles()
	# Please note that this will overwrite the existing files: trips.txt and 
	# passengersontrip.txt (make a backup!)
	
	# If you want to make a fresh start you can call:
	#simulation.clearFiles()
	# This will wipe trips.txt and passengersontrip.txt

	# Okay, well. We need some results, don't we? Lets plot stuff!
	# Note: I commented this code, as it takes some time depending 
	# on how many planes are implemented, how long the simulation has to
	# run etc. etc. .

	# creates a plot of the fuel consumption of each plane saved in fuel.png
	#plotter.plotFuel(simulation) 

	# creates a plot of the passenger kilometers made by each plane 
	# saved in passengerkilometers.png
	#plotter.plotPassengerKilometers(simulation)

	# Okay, that's some plotting done. Now lets use the 
	# Graphical User Interface (GUI).
	# Note: I commented this code, as you would get a frame on your screen
	# every time you run these examples (and it kind of spoils it).
	#gui.run(simulation)


	# Good Luck!