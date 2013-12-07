from __future__ import division
import math

resourcesFilePath = "resources"
configFilePath = resourcesFilePath + "/config.txt"
locationsFilePath = resourcesFilePath + "/locations.txt"
connectionsFilePath = resourcesFilePath + "/connections.txt"
tripsFilePath = resourcesFilePath + "/trips.txt"
planesFilePath = resourcesFilePath + "/planes.txt"
passengersFilePath = resourcesFilePath + "/passengers.txt"
passengersOnTripFilePath = resourcesFilePath + "/passengersontrip.txt"

waitAtAirport = 60
waitAtRefuel = 60
defaultStartTime = 0 # if starttime set in config.txt, this is unused.
defaultEndTime = 1440 # if endtime set in config.txt, this is unused.
defaultNoFlyStart = 120 # if noflystart set in config.txt, this is unused.
defaultNoFlyEnd = 360 # if noflyend set in config.txt, this is unused.

class Simulation(object):
    """
    A flight simulation in which planes fly from location to location.
    The simulation is divided in frames at discrete time steps of 1 minute.
    For one day consisting of 1440 minutes, 1440 frames are made.
    The state of each object in each frame is stored in its corresponding Log. All
    Objects of which these logs are made, have access to these logs. If one wants to
    examine a frame, simply request a SimulationLog which grants access to all others
    logs, and thus captures the frame.
    The Simulation can be run completely by calling the run method or partially by 
    requesting a SimulationLog at a certain point in time by calling the getSimulationLogAt
    method. Do note that as frame i is dependent on frame i-1, frame i-1 must thus exist. 
    If it does not, it is created. For example:
    Requesting a frame at time = 300 or by setting startTime = 300, all previous
    time = 0,1,...,298,299 frames are created.
    
    Data location:
    - Configuration of simulation can be found in config.txt
    - All connections can be found in connections.txt
    - All locations can be found in locations.txt
    - All passengers per connection can be found in passengers.txt
    - All planes can be found in planes.txt
    - All trips can be found in trips.txt
    
    Requirements:
    - Begin and end point of a plane are the same. (checked)
    - The plane passes home (specified in config.txt) at least once. (checked)
    - A plane does not land or take off between 2.00 - 6.00 am. (checked)
    - A plane can carry up to maximum number of passengers (specified in planes.txt). (checked)
    - A plane can fly up to maximum number of kilometers based on fuel (specified in planes.txt). 
    (checked in runtime or pre simulation)
    - A plane must wait at least 1 hour after landing. (checked in runtime or pre-simulation)
    - A plane must wait one extra hour if the plane refuels. (checked in runtime or pre-simulation)
    
    Limitations:
    - Once a frame has been created, it cannot be undone and/or recreated. 
    - The simulation cannot be changed in runtime.
    - A plane cannot be stalled in air to wait for the no fly zone to pass.
    """
    
    def __init__(self, dimensions):
        self.map = Map(dimensions)
        self.flightPlan = FlightPlan()
        self.startTime = defaultStartTime
        self.endTime = defaultEndTime
        self.noFlyStart = defaultNoFlyStart
        self.noFlyEnd = defaultNoFlyEnd
        
        self.home = None
        self._loadData()
        if self.home == None:
            raise ValueError("No home location set in config.txt.")
        
        self._testPlanes() # mandatory test, as the simulation will not check for this.
        
    def run(self):
        """
        Run simulation from begin time to end time.     
        """
        planes = self.flightPlan.getPlanes()
        for time in range(self.startTime, self.endTime):
            simulationLog = self.getSimulationLogAt(time)
            for plane in planes:
                planeLog = simulationLog.getPlaneLog(plane)
                print plane, "time", time, planeLog.getCoords(), planeLog.getFuel()

    def getSimulationLogAt(self, time):
        """
        Get the SimulationLog at time. If no SimulationLog exists, one is created.
        As SimulationLog at time i is depended on time i-1, i-1 is also created. Example:
        if time = 300, states at time = 0,1,...,298,299 are created.
        Because of this, this function serves a double purpose as it can also be used to run
        the simulation partially.
        :param time: requested time, int > 0 and < endTime,
        :returns: log containing the data of the simulation at the requested time.
        :rtype: SimulationLog
        """
        if time > self.endTime:
            raise ValueError("Requesting simulationLog at time: " + str(time) +\
                              " which is beyond endtime: " + str(self.endTime))
        if time < 0:
            raise ValueError("Requesting simulationLog at time: " + str(time) +\
                              " which is < 0.")
               
        return SimulationLog(self, time, self.flightPlan.getPlaneToLogAt(time), self.flightPlan.getConnectionToLogAt(time))

    def getStartTime(self):
        return self.startTime
    
    def getEndTime(self):
        return self.endTime
    
    def getPlanes(self):
        return self.flightPlan.getPlanes()
    
    def getConnections(self):
        return self.flightPlan.getConnections()
    
    def getLocations(self):
        return self.map.getLocations()
    
    def preSimulation(self):
        self._testPassengers()
        self._testFuel()
        self._testTrips()
        
    def _testPassengers(self):
        trips = self.flightPlan.getTrips()
        connectionToPassenger = {}
        
        # get all connections which also have a trip.
        for trip in trips:
            connections = trip.getPassengerConnections()
            
            for connection in connections:
                connectionToPassenger[connection] = connection.getPotentialPassengers()
        
        # calculate number of passengers taken from connections
        for trip in trips:
            connections = trip.getPassengerConnections()
            
            for connection in connections:
                connectionToPassenger[connection] -= trip.getNumPassengersTo(connection.getEndLocation())
                
                if connectionToPassenger[connection] < 0:
                    numPas = connectionToPassenger[connection] + trip.getNumPassengersTo(connection.getEndLocation())
                    raise ValueError("Illegal passenger subtraction in connection: " + str(connection) +\
                                      ", tried to subtract " + str(trip.getNumPassengers(connection)) +\
                                       " from " + str(numPas))
    
    def _testPlanes(self):
        for plane in self.flightPlan.getPlanes():
            trips = plane.getTrips()
            
            if len(trips) > 0:
                passedHome = False
                minTime = self.endTime
                maxTime = self.startTime
                
                for trip in trips:
                    startTime = trip.getStartTime()
                    endTime = startTime + plane.calcTimeInFlight(trip)
                    
                    if startTime < minTime:
                        startTrip = trip
                        minTime = startTime
                    
                    if startTime > maxTime:
                        endTrip = trip
                        maxTime = startTime
                    
                    if trip.getStartLocation() == self.home or trip.getEndLocation() == self.home:
                        passedHome = True
                    
                    if self.noFlyStart <= startTime < self.noFlyEnd or\
                     self.noFlyStart <= endTime < self.noFlyEnd:
                        raise ValueError("Plane: " + str(plane) + " with trip: " + str(trip) +\
                                         " tried to take off or land between noFlyStart: " +\
                                         str(self.noFlyStart) + " and noFlyEnd: " + str(self.noFlyEnd) +\
                                          ". It tried to take off at: " + str(startTime) +\
                                          "  and tried to land at: " + str(endTime))
                     
                if startTrip.getStartLocation() != endTrip.getEndLocation():
                    raise ValueError("Startpoint: " + str(startTrip.getStartLocation()) + " or endpoint: " +\
                                     str(endTrip.getEndLocation()) + " of plane: " + str(plane) +\
                                     " do not match.")
                
                if not passedHome:
                    raise ValueError("Plane: " + str(plane) + " did not pass home: " +\
                                      str(self.home) + " atleast once.")
                
                maxTime += plane.calcTimeTakenOverTrip(endTrip)
                
                if maxTime > self.endTime:
                    raise ValueError("Plane: " + str(plane) + " started trip: " + str(endTrip) + " but this trip ends at: " +\
                                     str(maxTime) + " which is beyond end time of simulation: " + str(self.endTime))
                    
    def _testFuel(self):
        """" for all planes, calculate fuel after each trip. Check if fuel <0 at any point """
        for plane in self.flightPlan.getPlanes():
            fuel = plane.getFuelAt(self.startTime)
            
            for trip in plane.getSortedTrips():
                fuel -= trip.getDistance()
                
                if fuel < 0:
                    raise ValueError("Fuel for plane: " + str(plane) + " reached <0 on trip:  " + str(trip))
                
                if trip.getRefuel():
                    fuel = plane.getFuelAt(0)
    
    def _testTrips(self):
        planes = self.flightPlan.getPlanes()
        
        for plane in planes:
            trips = plane.getTrips()
            tripStartEnd = []            
        
            for trip in trips:
                start = trip.getStartTime()
                end = start + plane.calcTimeTakenOverTrip(trip)
                tripStartEnd += [(start, end)]
            
            allTripIndexes = range(len(tripStartEnd))
            for i in allTripIndexes:
                start, end = tripStartEnd[i]
                restTripIndexes = allTripIndexes[:] # copy
                del restTripIndexes[i]
                
                for j in restTripIndexes:
                    startCheck, endCheck = tripStartEnd[j]
                    if startCheck <= start <= endCheck or startCheck <= end <= endCheck:
                        raise ValueError("Trip collision occured with plane: " + str(plane))
    
    def _loadData(self):
        locationsFile = open(locationsFilePath)
        self._interpretLocations(locationsFile.read())
        locationsFile.close()
        
        configFile = open(configFilePath)
        self._interpretConfig(configFile.read())
        configFile.close()
        
        connectionsFile = open(connectionsFilePath)
        passengersFile = open(passengersFilePath)
        self._interpretConnections(connectionsFile.read(), passengersFile.read())
        connectionsFile.close()
        passengersFile.close()
        
        planesFile = open(planesFilePath)
        self._interpretPlanes(planesFile.read())
        planesFile.close()
        
        tripsFile = open(tripsFilePath)
        passengersOnTripFile = open(passengersOnTripFilePath)
        self._interpretTrips(tripsFile.read(), passengersOnTripFile.read())
        tripsFile.close()
        passengersOnTripFile.close()
    
    def _interpretConfig(self, configString):
        configList = [line.split("=") for line in configString.split("\n")]
        for setting, value in configList:
            if setting == "starttime":
                self.startTime = int(value)
                
            elif setting == "endtime":
                self.endTime = int(value)
                
            elif setting == "noflystart":
                self.noFlyStart = int(value)
                
            elif setting == "noflyend":
                self.noFlyEnd = int(value)
                
            elif setting == "home":
                location = self.map.getLocationByName(value)
                if location != None:
                    self.home = location
                else:
                    raise ValueError("Unknown location: " + value + " set as home in " + configFilePath)
           
    def _interpretLocations(self, locationsString):
        locationsList = [line.split(",") for line in locationsString.split("\n")]
        self.map.addLocations([Location(name, locationId, (x, y)) for x, y, locationId, name in locationsList])
              
    def _interpretConnections(self, connectionsString, passengersString):
        connectionsList = [line.split(',') for line in connectionsString.split("\n")]
        passengersList = [line.split(',') for line in passengersString.split("\n")]
        
        idToLocation = {}
        for location in self.map.getLocations():
            idToLocation[location.getId()] = location
                    
        for i in range(len(connectionsList)):
            for j in range(len(connectionsList[i])):
                startLocation = idToLocation[i]
                endLocation = idToLocation[j]
                if startLocation != endLocation:
                    connection = Connection(startLocation, endLocation, connectionsList[i][j], passengersList[i][j])
                    self.flightPlan.addConnection(connection)
                    startLocation.addConnection(connection)

    def _interpretPlanes(self, planesString):
        planesList = [line.split(',') for line in planesString.split("\n")]
        planes = [Plane(name, maxPassengers, planeType, self.home, speed, flightRange)\
                                    for name, maxPassengers, planeType, speed, flightRange in planesList]
        self.flightPlan.addPlanes(planes)

    def _interpretTrips(self, tripString, passengersOnTripString):
        tripsList = [line.split(',') for line in tripString.split("\n")]
        passengersOnTripList = [line.split(',') for line in passengersOnTripString.split("\n")]
        
        nameToPlane = {}
        for plane in self.flightPlan.getPlanes():
            nameToPlane[plane.getName()] = plane
        
        tripNameToEndLocationToNumPassengers = {} # TODO better name?
        for tripName, numPassengers, endLocationName in passengersOnTripList:
  
            endLocation = self.map.getLocationByName(endLocationName)            
            if endLocation == None:
                raise ValueError("Unknown location: " + endLocationName + " in " + passengersOnTripFilePath)
            
            endLocationToNumPassengers = tripNameToEndLocationToNumPassengers.get(tripName, {})     
            if endLocationToNumPassengers.get(endLocation, None) != None:
                raise ValueError("Trip: " + tripName + " is mentioned twice with the same end location: " +\
                                  endLocationName + " in " + passengersOnTripFilePath)
                
            endLocationToNumPassengers[endLocation] = int(numPassengers)
            tripNameToEndLocationToNumPassengers[tripName] = endLocationToNumPassengers
        
        unknownTripNames = tripNameToEndLocationToNumPassengers.keys()
        knownTripNames = []
        
        for tripName, startTime, planeName, origin, destination, refuel in tripsList:
            plane = nameToPlane.get(planeName, None)
            if plane == None:
                raise ValueError("Unknown plane: " + str(planeName) + " in " + tripsFilePath)
        
            startLocation = self.map.getLocationByName(origin)
            endLocation = self.map.getLocationByName(destination)
            if startLocation == None or endLocation == None:
                raise ValueError("Either one of the following locations is unknown in map: " + str(origin) + ", " + str(destination))
                
            connection = startLocation.getConnection(endLocation)
            if connection == None:
                raise ValueError("Connection between: " + str(origin) + ", " + str(destination) + " does not exist.")
            
            # easier to ask for forgiveness than permission
            try:
                unknownTripNames.remove(tripName)
            except ValueError:
                pass
            
            if tripName in knownTripNames:
                raise ValueError("Duplicate trip name in " + tripsFilePath)
            
            knownTripNames.append(tripName)
            endLocationToNumPassengers = tripNameToEndLocationToNumPassengers.get(tripName, {})
            
            passengers = {}
            for passengerEndLocation in endLocationToNumPassengers.keys():
                passengerConnection = startLocation.getConnection(passengerEndLocation)
                
                if passengerConnection == None:
                    raise ValueError("No known connection between: " + str(startLocation) + " and: " +\
                                     str(passengerEndLocation) + " specified in " + str(passengersOnTripFilePath))
                
                passengers[passengerConnection] = endLocationToNumPassengers[passengerEndLocation]
            
            plane.addTrip(Trip(tripName, startTime, connection, passengers, int(refuel)))
        
        if len(unknownTripNames) > 0:
            raise ValueError("Unknown trip names: " + str(unknownTripNames) + " in " + passengersOnTripFilePath)
            

class SimulationLog(object):
    """
    State of a simulation at a given time.
    Contains: 
    - simulation Simulation
    - time int
    - planes list(Plane), all planes in the simulation.
    - connections list of Connection, all connections in the simulation.
    - planeLogs list of Planelog, logs of all the plane states at time.
    - connectionLogs list of ConnectionLog, logs of all the connection states at time.
    - planeToLog dict(Plane:PlaneLog), dictionary with keys all planes in the simulation
    and values all planeLogs in the simulation.
    - connectionToLog dict(Connection:ConnectionLog), dictionary with keys alls connection
    in the simulation and values all simulationLogs in the simulation.
    """
    
    def __init__(self, simulation, time, planeToLog, connectionToLog):
        self.simulation = simulation
        self.time = time
        self.planeToLog = planeToLog
        self.connectionToLog = connectionToLog
        
    def getSimulation(self):
        return self.simulation
        
    def getTime(self):
        return self.time
    
    def getPlaneLog(self, plane):
        return self.planeToLog.get(plane, None)

    def getPlaneToLog(self):
        return self.planeToLog
    
    def getConnectionToLog(self):
        return self.connectionToLog
    
    def getPlanes(self):
        return self.planeToLog.keys()
    
    def getConnections(self):
        return self.connectionToLog.keys()

    def getPlaneLogs(self):
        return self.planeToLog.values()
    
    def getConnectionLogs(self):
        return self.connectionToLog.values()

class FlightPlan(object):
    def __init__(self):
        self.planes = []
        self.connections = []
    
    def addConnection(self, connection):
        if connection not in self.connections:
            self.connections.append(connection)
        else:
            raise ValueError("Connection: " + str(connection) + " already exists in the flightplan.")
     
    def addConnections(self, connections):
        for connection in connections:
            self.addConnection(connection)
    
    def addPlane(self, plane):
        if plane not in self.planes:
            self.planes.append(plane)
        else:
            raise ValueError("Plane: " + str(plane) + " already exists in the flightplan.")
        
    def addPlanes(self, planes):
        for plane in planes:
            self.addPlane(plane)
    
    def getConnections(self):
        return self.connections
          
    def getPlanes(self):
        return self.planes
    
    def getConnectionToLogAt(self, time):
        return {con : con.getConnectionLogAt(time, self.planes) for con in self.connections}
    
    def getPlaneToLogAt(self, time):
        return {plane : plane.getPlaneLogAtNew(time) for plane in self.planes}

    def getTrips(self):
        trips = []
        for plane in self.planes:
            trips += plane.getTrips()
        return trips

class Plane(object):
    """
    Representation of a plane, which can travel over planned trips.
    """
    
    def __init__(self, name, maxPassengers, planeType, home, speed, maxFuel):
        self.name = str(name)
        self.maxPassengers = int(maxPassengers)
        self.planeType = str(planeType)
        self.speed = int(speed)
        self.maxFuel = int(maxFuel)
        self.home = home
        self.trips = {} # startTimeToTrip
        self.timeToPlaneLog = {}
        
    def __str__(self):
        return self.name
        
    def setLocation(self, location):
        self.location = location
        
    def addTrip(self, trip):
        if trip.getTotalNumPassengers() > self.maxPassengers:
            raise ValueError("Plane: " + str(self) + " cannot carry more than " + str(self.maxPassengers) +\
                              " Passengers, requested: " + str(trip.getTotalNumPassengers()))
        
        startTime = trip.getStartTime()
        self.trips[startTime] = trip
        
    def getCoordsAt(self, time):
        return self.getPlaneLogAtNew(time).getCoords()
        #return self.getPlaneLogAt(time).getCoords()
    
    def getFuelAt(self, time):
        return self.getPlaneLogAtNew(time).getFuel()
        #return self.getPlaneLogAt(time).getFuel()
        
    def getPassengersAt(self, time):
        return self.getPlaneLogAtNew(time).getPassengers()
        #return self.getPlaneLogAt(time).getPassengers()
    
    def getPassengerKilometersAt(self, time):
        return self.getPlaneLogAtNew(time).getPassengerKilometers()
        #return self.getPlaneLogAt(time).getPassengerKilometers()
    
    def getPlaneLogAtNew(self, time):
        """
        Get a PlaneLog of this plane at time.
        """
        if len(self.trips) == 0:
            raise ValueError("No trips planned for plane %s" %(self))

        # find all trips that have taken place plus the one taking place (if there is one)
        tripsSorted = sorted(self.trips.values(), key = lambda trip : trip.getStartTime())
        trips = filter(lambda trip : time >= trip.getStartTime(), tripsSorted)

        currentTrip = None # the trip the plane is undertaking right now at time.
        passengers = {}
        fuel = self.maxFuel
        passengerKilometers = 0

        # if no trips took place at time, set coords (to start coords). 
        # else: calculate new coords, adjust fuel etc.
        if len(trips) == 0:
            coords = self.calculatePlaneCoords(time, tripsSorted[0])
        else:
            coords = self.calculatePlaneCoords(time, trips[-1])

            # for all trips that took place at time, substract fuel.
            for trip in trips[:-1]:
                if trip.getRefuel():
                    fuel = self.maxFuel
                else:
                    fuel -= trip.getDistance()

                passengers = self._combinePassengers(passengers, trip.getPassengers())

                passengerKilometers += self.removePassengers(passengers, trip.getEndLocation())

            # the last trip, which might take place right now at time.
            trip = trips[-1]
            passengers = self._combinePassengers(passengers, trip.getPassengers())

            # if plane is in air at time, update fuel depending on distance.
            if time < trip.getEndTimeWithoutGroundTime(self):
                fuel -= (time - trip.getStartTime()) * (self.speed / 60)
                currentTrip = trip
            
            # if plane is still busy on a trip, but not in air adjust fuel.
            elif time < trip.getEndTime(self):
                fuel -= trip.getDistance()
                currentTrip = trip

            # else plane has finished last trip, check if it has refueled and adjust fuel.
            else:
                if trip.getRefuel():
                    fuel = self.maxFuel
                else:
                    fuel -= trip.getDistance()

                passengerKilometers += self.removePassengers(passengers, trip.getEndLocation())
        
        return PlaneLog(self, passengers, time, fuel, coords, currentTrip, passengerKilometers = passengerKilometers)

    def calculatePlaneCoords(self, time, trip):
        connection  =   trip.getConnection()
        endCoords   =   connection.getEndLocation().getCoords()
        startCoords =   connection.getStartLocation().getCoords()
        distance    =   connection.getDistance()
        startTime   =   trip.getStartTime()
     
        if time < startTime:
            return startCoords

        elif distance / self.speed * 60 < time - startTime:
            return endCoords

        else:
            x       =   endCoords[0] - startCoords[0]
            y       =   endCoords[1] - startCoords[1]
            alpha   =   math.atan2(y, x)
            
            # Pythagoras, hurray!
            actualDistance = math.sqrt(x**2 + y**2)
            
            speed = (self.speed / 60) * (time - startTime)
            actualSpeed = (speed / distance) * actualDistance # coords do not match the distance in trips, hence actualSpeed

            # x_i, y_i = x_(i-1) + speed * cos(alpha), y_(i-1)  speed * sin(alpha)
            return (startCoords[0] + actualSpeed * math.cos(alpha), startCoords[1] + actualSpeed * math.sin(alpha))

    def removePassengers(self, passengers, endLocation):
        passengerKilometers = 0

        for connection in passengers.copy():
            if connection.getEndLocation() == endLocation:
                passengerKilometers += passengers[connection] * connection.getDistance()
                del passengers[connection]

        return passengerKilometers

    # source: http://stackoverflow.com/questions/328107/how-can-you-determine-a-point-is-between-two-other-points-on-a-line-segment   
    def _isBetween(self, a, b, c):
        """Check if c is on the line segment a, b"""
        epsilon = .001
        crossproduct = (c[1] - a[1]) * (b[0] - a[0]) - (c[0] - a[0]) * (b[1] - a[1])
        if abs(crossproduct) > epsilon : 
            return False
        
        dotproduct = (c[0] - a[0]) * (b[0] - a[0]) + (c[1] - a[1]) * (b[1] - a[1])
        if dotproduct < 0 : 
            return False
        
        squaredlengthba = (b[0] - a[0]) * (b[0] - a[0]) + (b[1] - a[1]) * (b[1] - a[1])
        if dotproduct > squaredlengthba: 
            return False
        
        return True
    
    def _combinePassengers(self, passengers1, passengers2):
        return dict((connection, passengers1.get(connection, 0) + passengers2.get(connection, 0))\
              for connection in set(passengers1)|set(passengers2))
        
    def _getTripWithStartBetween(self, lowerbound, upperbound):
        for startTime in self.trips:
            if lowerbound <= startTime < upperbound:
                return self.trips[startTime]
        return None
    
    def _arrivedAt(self, endLocation, passengers):
        passengerKilometers = 0
        for connection in passengers.keys():
            if endLocation == connection.getEndLocation():
                passengerKilometers += connection.getDistance() * passengers[connection]
                del passengers[connection]
        return passengerKilometers
    
    def getMaxPassengers(self):
        return self.maxPassengers
                
    def getMaxFuel(self):
        return self.maxFuel
            
    def getTrips(self):
        return self.trips.values()
    
    def getSortedTrips(self):
        startTimes = sorted(self.trips.keys())
        return [self.trips[startTime] for startTime in startTimes]
    
    def getName(self):
        return self.name

    def getSpeed(self):
        return self.speed
    
    def getPlaneType(self):
        return self.planeType
    
    def getHome(self):
        return self.home
    
    def calcTimeInFlight(self, trip):
        return trip.getDistance() / (self.speed / 60.0)
    
    def calcTimeTakenOverTrip(self, trip):
        time = self.calcTimeInFlight(trip) + waitAtAirport
        if trip.getRefuel():
            time += waitAtRefuel
        return time # int(time + 0.5)

class PlaneLog(object):
    """
    State of a plane at a given time (blackbox).
    Contains:
    - plane Plane
    - time int 
    - fuel in km float/int (if plane in the 'air', represented as float)
    - coords (int, int), coordinates of the plane
    - trip Trip, the trip the plane is currently taken, None if no trip.
    - landTime int, time plane has landed, -1 if plane not on trip or in the 'air'.
    """
    
    def __init__(self, plane, passengers, time, fuel, coords, trip, passengerKilometers = 0):
        self.plane = plane
        self.time = time
        self.fuel = fuel
        self.coords = coords
        self.trip = trip
        self.passengerKilometers = passengerKilometers
        self.passengers = passengers # {connection:numPassengers}
        
    def getPlane(self):
        return self.plane
        
    def getTrip(self):
        return self.trip
        
    def getTime(self):
        return self.time
    
    def getFuel(self):
        return self.fuel
    
    def getCoords(self):
        return self.coords
    
    def getPassengers(self):
        return self.passengers
    
    def getPassengerKilometers(self):
        return self.passengerKilometers
    
    def getNumPassengers(self, connection):
        return self.passengers.get(connection, 0)
    
    def getNumPassengersTo(self, endLocation):
        connectionsTo = []
        for connection in self.passengers.keys():
            if endLocation == connection.getEndLocation():
                connectionsTo.append(connection)
        return sum([self.passengers.get(connection, 0) for connection in connectionsTo])
    
    def getTotalNumPassengers(self):
        return sum(self.passengers.values())

class Trip(object):
    def __init__(self, name, startTime, connection, passengers, refuel):
        self.name = name
        self.startTime = float(startTime)
        self.connection = connection
        self.refuel = bool(refuel)
        self.passengers = passengers # connection to number of passengers
        
    def __str__(self):
        return "starttime: " + str(self.startTime) + ", " + str(self.connection)
        
    def getStartTime(self):
        return self.startTime

    def getEndTime(self, plane):
        endTime = self.getEndTimeWithoutGroundTime(plane)

        if self.refuel:
            endTime += 120
        else:
            endTime += 60

        return endTime
    
    def getEndTimeWithoutGroundTime(self, plane):
        return self.startTime + self.connection.getDistance() / plane.getSpeed() * 60

    def getRefuel(self):
        return self.refuel
    
    def getConnection(self):
        return self.connection
    
    def getDistance(self):
        return self.connection.getDistance()
    
    def getStartLocation(self):
        return self.connection.getStartLocation()
    
    def getEndLocation(self):
        return self.connection.getEndLocation()
    
    def getPassengers(self):
        return self.passengers
    
    def getNumPassengers(self, connection):
        return self.passengers.get(connection, 0)
    
    def getNumPassengersTo(self, endLocation):
        connectionsTo = []
        for connection in self.passengers.keys():
            if endLocation == connection.getEndLocation():
                connectionsTo.append(connection)
        return sum([self.passengers.get(connection, 0) for connection in connectionsTo])
    
    def getTotalNumPassengers(self):
        return sum(self.passengers.values())
    
    def getPassengerEndLocations(self):
        return [connection.GetEndLocation() for connection in self.passengers.keys()]
    
    def getPassengerConnections(self):
        return self.passengers.keys()
    
    def subtractPassengers(self):
        connections = self.getPassengerConnections()

        # subtract passengers boarding plane from possible passengers on connection.
        for connection in connections:
            connection.subtractPotentialPassengers(self.passengers[connection], self.startTime) 
    
class Map(object):
    def __init__(self, dimensions):
        self.dimensions = dimensions
        self.plain = [[None for i in range(dimensions[0])] for j in range(dimensions[1])]
        self.locations = []
        self.nameToLocations = {}
        
    def __str__(self):
        for i in range(self.dimensions[0]):
            print [str(self.plain[i][j]) for j in range(self.dimensions[1])]
        
    def addLocation(self, location):
        coords = location.getCoords()
        if 0 <= coords[0] <= self.dimensions[0] and 0 <= coords[1] <= self.dimensions[1]:
            if self.plain[coords[0]][coords[1]] == None:
                self.locations.append(location)
                self.plain[coords[0]][coords[1]] = location
                self.nameToLocations[location.getName()] = location
            else:
                raise ValueError("Coords: " + str(coords) + " already occupied by location: " + str(self.plain[coords[0]][coords[1]]))
        else:
            raise ValueError("Location: " + str(location) + " with coords: " + str(location.getCoords()) +\
                              " does not fit on map with dimensions " + str(self.dimensions))
            
    def addLocations(self, locations):
        for location in locations:
            self.addLocation(location)
            
    def getLocations(self):
        return self.locations
    
    def getLocationByName(self, name):
        return self.nameToLocations.get(name, None)
    
    def printLocations(self):
        print ', '.join([str(location) for location in self.locations])
            
class Connection(object):
    def __init__(self, startLocation, endLocation, distance, potentialPassengers):
        if startLocation == endLocation:
            raise ValueError("Connections from and to the same city cannot exist for city: " + str(startLocation) +\
                              "with id: " + str(startLocation.id()))
              
        self.startLocation = startLocation
        self.endLocation = endLocation
        self.distance = int(distance)
        self.potentialPassengers = int(potentialPassengers)
        
    def __str__(self):
        return str(self.startLocation) + " --" + str(self.distance) + "--> " + str(self.endLocation) 
        
    def getDistance(self):
        return self.distance
    
    def getStartLocation(self):
        return self.startLocation
    
    def getEndLocation(self):
        return self.endLocation
    
    def getLocations(self):
        return self.startLocation, self.endLocation
    
    def getPotentialPassengers(self):
        return self.potentialPassengers

    def getPotentialPassengersAt(self, time, planes):
        return self.getConnectionLogAt(time, planes).getPotentialPassengers()

    def getConnectionLogAt(self, time, planes):
        potentialPassengers = self.potentialPassengers

        for plane in planes:

            for trip in plane.getTrips():
                passengers = trip.getPassengers()

                if trip.getStartTime() < time:
                    potentialPassengers -= passengers.get(self, 0)

        return ConnectionLog(self, time, potentialPassengers)

class ConnectionLog(object):
    def __init__(self, connection, time, potentialPassengers):
        self.connection = connection
        self.potentialPassengers = potentialPassengers
        self.time = time
        
    def getConnection(self):
        return self.connection
    
    def getPotentialPassengers(self):
        return self.potentialPassengers
  
    def getTime(self):
        return self.time
  
class Location(object):
    def __init__(self, name, locationId, coords):
        self.name = str(name)
        self.id = int(locationId)
        self.coords = (int(coords[0]), int(coords[1]))
        self.connections = []
        self.endLocationToConnection = {}
        
    def __str__(self):
        return self.name;
        
    def getName(self):
        return self.name
    
    def getId(self):
        return self.id
    
    def getCoords(self):
        return self.coords
    
    def addConnection(self, connection):
        if type(connection) == Connection and self in connection.getLocations():
            endLocation = connection.getEndLocation()
            if self.endLocationToConnection.get(endLocation, True) == True:
                self.connections.append(connection)
                self.endLocationToConnection[connection.getEndLocation()] = connection
            else:
                raise ValueError("Connection with startLocation: " + str(self) + " endLocation: " +\
                                  str(endLocation) + " already exists. Duplicate connections.")
        else:
            raise ValueError("Connection " + str(connection) + " cannot be added, for connection is not of type Connection or\
             does not contain location: " + str(self))
        
    def addConnections(self, connections):
        for connection in connections:
            self.addConnection(connection)
        
    def getConnections(self):
        return self.connections
    
    def getConnection(self, endLocation):
        """
        Get connection from self to endLocation in constant time.
        returns connection, None if no connection found.
        """
        return self.endLocationToConnection.get(endLocation, None)
        
    def printConnections(self):
        print ', '.join([str(connection) for connection in self.connections])

if __name__ == "__main__":
    s = Simulation((500, 500));
    s.run()