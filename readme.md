<h3> How To Run </h3>

- Install python 2.7, do not install 3.x!

With Graphical User Interface (GUI).
- run mokumgui.py by opening it in Idle for instance, or by typing python mokumgui.py in cmd or console.

Without GUI.
- run mokum.py by opening it in Idle for instance, or by typing python mokumgui.py in cmd or console.

Note the no-gui variant does not produce much output, but you can use it for debugging!

<h3> Filestructures </h3>

WARNING do not end a file with a blank line!

<h5> config.txt </h5>
This where you put the configuration of the simulation. Currently there are five options: 

* starttime=0 % start time of the simulation
* endtime=1440 % end time of the simulation
* noflystart=120 % start time of period in which planes may not take off or land
* noflyend=360 % end time of period in which planes may not take off or land
* home=Amsterdam % home location of MokumAirlines
 
Be carefull with the syntax, for instance Amsterdam must be typed exactly the same way as it is in locations.txt.

<h5> connections.txt </h5>
Opening this file might make your head explode, but it is actually quite simple for a computer to understand. This file represents the distances between locations with a table/matrix (pick your own terminology) which is symmetric across the diagonal. Every i-th row/column poses as the i-th location in locations.txt, and the numbers represent the distance between the two.

<h5> locations.txt </h5>
This file contains all the locations (surprise). A location is represented as:
* x-coordinate,y-coordinate,id,name

Be carefull with the syntax, for instance the way you write the name of a location matters for other files.

<h5> passengers.txt</h5>
Yup, just like connections.txt. Only now the table/matrix does not represent the distance between two locations, but instead the number of passengers willing to travel between the two.

<h5> trips.txt </h5>
This contains all the (plane) trips for the simulation. So your schedule should fit in here. A trip is represented as:
* tripName,startTime(float),planeName,startLocationName,endLocationName,refuel(bool)

Yet again, be carefull with the syntax! For instance a planeName must match a name in planes.txt. What is refuel? Simple: should the plane refuel at the end of this trip yes? then 1, no? then 0.

<h5> planes.txt </h5>
This file contains all the planes for the simulation. Please note the GUI of the simulator only supports up to six planes and does not accept 0 planes! Now how are planes represented in planes.txt? Like so:
* name,maxPassengers,type,speed,maxFuel

Syntax, syntax, syntax! The name of the plane here determines the name in the other files or vice versa. I guess it depends on how you look at it. Quick clarification: maxPassengers = maximum number of passengers that fit in the plane, type = the type of the plane for instance boeing737, speed = avarage speed of the plane, maxFuel = maximum number of kilometers a plane can fly. Remember to refuel!

<h5> passengersontrip.txt </h5>
You might have noticed the lack of passengers in trips. That is because a trip does not determine the passsengers. For instance you might have a trip from Amsterdam to Athene while stopping in Berlin on the way. You could then have passengers hop on in Amsterdam for Athene, but the first trip the plane is going to undertake is to Berlin. The simulation handles this by keeping a different file containing the number of passengers hopping on for a destination on each trip. passengersontrip.txt is that file! How does the representation work?

* tripName,numPassengers,endLocation

Anyone for a game of hangman? I got a word with six letters. Quick clarification: numPassengers is the number of passengers that hop on the plane at the start of the trip, endLocation = the destination of those passengers. Please note that if the plane does not pass the destination the passengers want to go to. They will remain in the plane.
