import math

configFilePath = "resources/config.txt"
locationsFilePath = "resources/locations.txt"
connectionsFilePath = "resources/connections.txt"
tripsFilePath = "resources/trips.txt"
planesFilePath = "resources/planes.txt"
passengersFilePath = "resources/passengers.txt"

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
    - A plane can fly up to maximum number of kilometers based on fuel (specified in planes.txt). (checked in runtime)
    - A plane must wait at least 1 hour after landing. (checked in runtime)
    - A plane must wait one extra hour if the plane refuels. (checked in runtime)
    
    Limitations:
    - Detours are impossible.
    - Once a frame has been created, it cannot be undone and/or recreated. 
    - The simulation cannot be changed in runtime.
    """
    
    def __init__(self, dimensions):
        self.map = Map(dimensions)
        self.flightPlan = FlightPlan()
        self.startTime = defaultStartTime
        self.endTime = defaultEndTime
        self.noFlyStart = defaultNoFlyStart
        self.noFlyEnd = defaultNoFlyEnd
        
        self.timeToSimulationLog = {}
        
        self.home = None
        self._loadData()
        if self.home == None:
            raise ValueError("No home location set in config.txt.")
        
    def run(self):
        """
        Run simulation from begin time to end time.     
        """
        planes = self.flightPlan.getPlanes()
        for time in range(self.startTime, self.endTime):
            self.getSimulationLogAt(time) # automatically creates a simulationLog if it does not exist.
            for plane in planes:
                print plane, "time", time, plane.getCoordsAt(time), plane.getFuelAt(time)

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
               
        simulationLog = self.timeToSimulationLog.get(time, None)
        if simulationLog == None:
            if time != 0:
                self.getSimulationLogAt(time - 1) # create SimulationLogs for all previous states.
            simulationLog = SimulationLog(self, time, self.flightPlan.getPlaneToLogAt(time), self.flightPlan.getConnectionToLogAt(time))
            self.timeToSimulationLog[time] = simulationLog
            
        return simulationLog
    
    def getStartTime(self):
        return self.startTime
    
    def getEndTime(self):
        return self.endTime
    
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
        self._interpretTrips(tripsFile.read())
        tripsFile.close()
    
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
                    raise ValueError("Unknown location: " + value + " set as home in config.txt.")
           
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
        self.flightPlan.addPlanes([Plane(name, maxPassengers, planeType, self.home, speed, flightRange)\
                                    for name, maxPassengers, planeType, speed, flightRange in planesList])

    def _interpretTrips(self, tripString):
        tripsList = [line.split(',') for line in tripString.split("\n")]
        
        nameToPlane = {}
        for plane in self.flightPlan.getPlanes():
            nameToPlane[plane.getName()] = plane
              
        for startTime, planeName, origin, destination, numPassengers, refuel in tripsList:
            plane = nameToPlane.get(planeName, None)
            if plane != None:
                startLocation = self.map.getLocationByName(origin)
                endLocation = self.map.getLocationByName(destination)
                if startLocation != None and endLocation != None:
                    connection = startLocation.getConnection(endLocation)
                    if connection != None:
                        plane.addTrip(Trip(startTime, connection, numPassengers, int(refuel)))
                    else:
                        raise ValueError("Connection between: " + str(origin) + ", " + str(destination) + " does not exist.")
                else:
                    raise ValueError("Either one of the following locations is unknown in map: " + str(origin) + ", " + str(destination))
            else:
                raise ValueError("Unknown plane: " + str(planeName) + " in trips.txt.")
            
        for plane in nameToPlane.values():
            trips = plane.getTrips()
            if len(trips) > 0:
                passedHome = False
                minTime = self.endTime
                maxTime = self.startTime
                
                for trip in trips:
                    startTime = trip.getStartTime()
                    endTime = startTime + plane.calcTimeTakenOverTrip(trip)
                    
                    if startTime < minTime:
                        startTrip = trip
                        minTime = startTime
                    
                    if startTime > maxTime:
                        endTrip = trip
                        maxTime = startTime
                    
                    if trip.getStartLocation() == self.home or trip.getEndLocation() == self.home:
                        passedHome = True
                    
                    if self.noFlyStart <= startTime <= self.noFlyEnd or\
                     self.noFlyStart <= endTime <= self.noFlyEnd:
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
                    raise ValueError("Plane: " + str(plane) + " did not pass home atleast once.")
                
                maxTime += plane.calcTimeTakenOverTrip(endTrip)
                
                if maxTime > self.endTime:
                    raise ValueError("Plane: " + str(plane) + " started trip: " + str(endTrip) + " but this trip ends at: " +\
                                     str(maxTime) + " which is beyond end time of simulation: " + str(self.endTime))

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
        self.time = int(time)
        self.planeToLog = planeToLog
        self.connectionToLog = connectionToLog
        
    def getSimulation(self):
        return self.simulation
        
    def getTime(self):
        return self.time
    
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
            raise ValueError("Connection: " + str(connection) + "already exists in the flightplan.")
     
    def addConnections(self, connections):
        for connection in connections:
            self.addConnection(connection)
    
    def addPlane(self, plane):
        if plane not in self.planes:
            self.planes.append(plane)
        else:
            raise ValueError("Plane: " + str(plane) + "already exists in the flightplan.")
        
    def addPlanes(self, planes):
        for plane in planes:
            self.addPlane(plane)
    
    def getConnections(self):
        return self.connections
          
    def getPlanes(self):
        return self.planes
    
    def getConnectionToLogAt(self, time):
        connectionToLog = {}
        for connection in self.connections:
            connectionToLog[connection] = connection.getConnectionLogAt(time)
        return connectionToLog
    
    def getPlaneToLogAt(self, time):
        planeToLog = {}
        for plane in self.planes:
            planeToLog[plane] = plane.getPlaneLogAt(time)
        return planeToLog

class Plane(object):
    """
    Representation of a plane, which can travel over planned trips.
    The plane keeps track of its states ...,i-1,i,i+1,... in planeLogs.
    """
    
    def __init__(self, name, maxPassengers, planeType, home, speed, maxFuel):
        self.name = str(name)
        self.maxPassengers = int(maxPassengers)
        self.planeType = str(planeType)
        self.speed = int(speed)
        self.maxFuel = int(maxFuel)
        self.home = str(home)
        self.trips = {} #startTimeToTrip
        self.timeToPlaneLog = {}
        
    def __str__(self):
        return self.name
        
    def setLocation(self, location):
        self.location = location
        
    def addTrip(self, trip):
        if trip.getNumPassengers() > self.maxPassengers:
            raise ValueError("Plane: " + str(self) + " cannot carry more than " + str(self.maxPassengers) +\
                              " Passengers, requested: " + str(trip.getNumPassengers()))
        
        startTime = trip.getStartTime()
        self.trips[startTime] = trip
        
    def getCoordsAt(self, time):
        return self.getPlaneLogAt(time).getCoords()
    
    def getFuelAt(self, time):
        return self.getPlaneLogAt(time).getFuel()
        
    def getPlaneLogAt(self, time):
        """
        Recursively calculate the plane log at time. As the current state i of the plane is dependent on state i-1,
        we backtrack till a known state and calculate upwards from there. For example if time = 500 and no state is known,
        all 0-499 states are calculated. All plane logs created are stored.
        :param time: requested time, int > 0
        :returns: log containing the data of the plane at the requested time.
        :rtype: PlaneLog
        """
        time = int(time)
        if time < 0:
            raise ValueError("This is not the delorean, plane: " + str(self) + " cannot go to time: " + str(time))     
        
        return self._getPlaneLogAtRec(time)
        
    def _getPlaneLogAtRec(self, time):
        """
        Recursively calculate the plane log at time. As the current state i of the plane is dependent on state i-1,
        we backtrack till a known state and calculate upwards from there. For example if time = 500 and no state is known,
        all 0-499 states are calculated. All planelogs created at states are stored.
        :param time: requested time, int > 0 (unchecked)
        :returns: log containing the data of the plane at the requested time.
        :rtype: PlaneLog
        """
        
        planelog = self.timeToPlaneLog.get(time, None)
        
        # base case
        if time == 0:
            if planelog == None:
                startTime = min(self.trips.keys())
                trip = self.trips[startTime]
                
                if startTime == time:
                    connection = trip.getConnection()
                    
                    # substract passengers boarding plane from possible passengers on connection.
                    connection.substractPotentialPassengers(trip.getNumPassengers(), time) 
                    self.timeToPlaneLog[time] = PlaneLog(self, time, self.maxFuel, trip.getConnection().getStartLocation().getCoords(), trip)
                else:
                    self.timeToPlaneLog[time] = PlaneLog(self, time, self.maxFuel, trip.getConnection().getStartLocation().getCoords(), None)
        
        # recursive step       
        elif planelog == None:        
            oldPlaneLog = self._getPlaneLogAtRec(time - 1)        
            
            newTrip = self.trips.get(time, None)
            if newTrip == None:
                self.timeToPlaneLog[time] = self._createNextPlaneLog(oldPlaneLog)
            else:
                # if last state was last minute of trip, calculate trip's end; set oldplanelog(i-1) to newplanlog(i)
                # for last minute changes (pun intended). Else trip collision occurred, raise exception.
                if oldPlaneLog.getTrip() != None:
                    newPlaneLog = self._createNextPlaneLog(oldPlaneLog)
                    if newPlaneLog.getTrip() == None:
                        oldPlaneLog = newPlaneLog
                    else:
                        raise ValueError("Trip collision with plane: " + str(self) + " at time: " + str(time) +\
                                         ", trip: " + str(newPlaneLog.getTrip()) + " collided with " + str(newTrip))

                connection = newTrip.getConnection()
                startLocation = connection.getStartLocation()
                
                if oldPlaneLog.getCoords() != startLocation.getCoords():
                    raise ValueError("plane: " + str(self) + ", Start coords of new trip: " + str(startLocation.getCoords()) +\
                                      " does not match current coords: " + str(oldPlaneLog.getCoords()))
 
                # substract passengers boarding plane from possible passengers on connection.
                connection.substractPotentialPassengers(newTrip.getNumPassengers(), time) 
                self.timeToPlaneLog[time] = PlaneLog(self, time, oldPlaneLog.getFuel(), startLocation.getCoords(), newTrip)
        
        return self.timeToPlaneLog[time]
    
    def _createNextPlaneLog(self, oldPlaneLog):
        """
        Creates a new planelog at i dependent on the previous planelog at i-1 given. NOTE it is solely
        based on the previous planelog, thus new Trips planned at i are not taken into account! Depending
        on the trip at i-1 new coordinates for the plane are calculated and fuel is adjusted in
        'real time', meaning not just at the end of the trip. At the end of a trip, fuel is cast
        to an integer for ease of calculation in planning, however during the trip fuel is represented
        as a floating point number.
        :param oldPlaneLog: previous planelog at time i-1
        :returns: new planelog at time i based on time i-1
        :rtype: PlaneLog
        """
        
        oldCoords = oldPlaneLog.getCoords()
        time = oldPlaneLog.getTime() + 1
        oldTrip = oldPlaneLog.getTrip()
        
        if oldTrip == None:
            return PlaneLog(self, time, oldPlaneLog.getFuel(), oldCoords, None)
        
        oldConnection = oldTrip.getConnection()
        oldStartCoords = oldConnection.getStartLocation().getCoords()
        oldEndCoords = oldConnection.getEndLocation().getCoords()
        oldLandTime = oldPlaneLog.getLandTime()

        # if end already reached, check if still busy with trip; return new PlaneLog
        if oldLandTime >= 0:
            tripStopTime = oldLandTime + waitAtAirport
            if oldTrip.getRefuel():
                tripStopTime += waitAtRefuel
            if time == tripStopTime:
                if oldTrip.getRefuel():
                    return PlaneLog(self, time, self.maxFuel, oldCoords, None)
                else:
                    return PlaneLog(self, time, oldPlaneLog.getFuel(), oldCoords, None)
            else:
                return PlaneLog(self, time, oldPlaneLog.getFuel(), oldCoords, oldTrip, oldLandTime)
            
        # else, calculate new coords on trip; return new PlaneLog
        else:   
            distance = oldConnection.getDistance()
            # Pythagoras, hurray!
            actualDistance = math.sqrt((oldEndCoords[0] - oldStartCoords[0])**2 + (oldEndCoords[1] - oldStartCoords[1])**2)
            speed = (self.speed / 60.0)
            actualSpeed = (speed / distance) * actualDistance # coords do not match the distance in trips, hence actualSpeed
            x = oldEndCoords[0] - oldStartCoords[0]
            y = oldEndCoords[1] - oldStartCoords[1]
            alpha = math.atan2(y, x)
            
            # x_i, y_i = x_(i-1) + speed * cos(alpha), y_(i-1) + speed * sin(alpha)
            newCoords = (oldCoords[0] + actualSpeed * math.cos(alpha), oldCoords[1] + actualSpeed * math.sin(alpha))
            
            hasLanded = False
                     
            # if plane flew over the end location, set coords to match end location, thus plane has landed.
            # adjust fuel spend to match actual distance travelled, thus not 'wasting' fuel.
            if self._isBetween(oldStartCoords, newCoords, oldEndCoords):
                newCoords = oldEndCoords
                newFuel = self.getPlaneLogAt(oldTrip.getStartTime()).getFuel() - oldConnection.getDistance()
                hasLanded = True
            else:
                newFuel = oldPlaneLog.getFuel() - speed
            
            if newFuel < 0:
                raise ValueError("Plane: " + str(self) + " crashed at time: " + str(time) + ", reason fuel: " + str(newFuel))
            
            if hasLanded:
                return PlaneLog(self, time, newFuel, newCoords, oldTrip, landTime = time)
            else:
                return PlaneLog(self, time, newFuel, newCoords, oldTrip)
       
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
         
    def getMaxPassengers(self):
        return self.maxPassengers
                
    def getMaxFuel(self):
        return self.maxFuel
            
    def getTrips(self):
        return self.trips.values()
    
    def getName(self):
        return self.name

    def getSpeed(self):
        return self.speed
    
    def getPlaneType(self):
        return self.planeType
    
    def getHome(self):
        return self.home
    
    def calcTimeTakenOverTrip(self, trip):
        time = trip.getDistance() / (self.speed / 60.0) + waitAtAirport
        if trip.getRefuel():
            time += waitAtRefuel
        return int(time + 0.5)

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
    
    def __init__(self, plane, time, fuel, coords, trip, landTime = -1):
        self.plane = plane
        self.time = int(time)
        self.fuel = fuel # cutoff to int at end of trips.
        self.coords = coords
        self.trip = trip
        self.landTime = landTime
        
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
    
    def getLandTime(self):
        return self.landTime

class Trip(object):
    def __init__(self, startTime, connection, numPassengers, refuel):
        self.startTime = int(startTime)
        self.connection = connection
        self.refuel = bool(refuel)
        self.numPassengers = int(numPassengers)
        
    def __str__(self):
        return "starttime: " + str(self.startTime) + ", " + str(self.connection)
        
    def getStartTime(self):
        return self.startTime
    
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
    
    def getNumPassengers(self):
        return self.numPassengers
    
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
        self.timeToConnectionLog = {0:ConnectionLog(self, 0, int(potentialPassengers))}
        
    def __str__(self):
        return str(self.startLocation) + " --" + str(self.distance) + "--> " + str(self.endLocation) 
        
    def substractPotentialPassengers(self, numPassengers, time):
        connectionLog = self.getConnectionLogAt(time)
        potentialPassengers = connectionLog.getPotentialPassengers()
        newPotentialPassengers = potentialPassengers - numPassengers
        if newPotentialPassengers >= 0:
            self.timeToConnectionLog[time] = ConnectionLog(self, time, newPotentialPassengers)
        else:
            raise ValueError("Illegal passenger substraction in connection: " + str(self) + ", tried to substract " +\
                              str(numPassengers) + " from " + str(potentialPassengers))
        
    def getDistance(self):
        return self.distance
    
    def getStartLocation(self):
        return self.startLocation
    
    def getEndLocation(self):
        return self.endLocation
    
    def getLocations(self):
        return self.startLocation, self.endLocation
    
    def getPotentialPassengersAt(self, time):
        connectionLog = self.getConnectionLogAt(time)
        return connectionLog.getPotentialPassengers()
    
    def getConnectionLogAt(self, time):
        timeKeys = sorted(self.timeToConnectionLog.keys())
        i = 0
        for timeKey in timeKeys[1:]:
            if time < timeKey:
                break  
            i += 1
        return self.timeToConnectionLog[timeKeys[i]]
#    def getPassengerKilometer(self):
#        return self.potenialPassengers * self.distance

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