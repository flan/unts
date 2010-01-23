# -*- coding: utf-8 -*-
"""
Unts module: map; contains objects used to model the state of the system.
"""
from shared import *
import agents
import inerts
import math

FOUR_PI = 4 * math.pi #: A value needed for inverse-square calculations.

class Field(object):
	"""
	The map of a state of the system's execution.
	"""
	_grid = None #: The structure of spaces within this field.
	_pool = None #: All spaces within this field in an arbitrary linear ordering.
	_dimensions = None #: The (width, hight) dimesions of this field.
	_pheromones = None #: A list of all pheromones within this field.
	
	def __init__(self, dimensions):
		"""
		Creates a new Field.
		
		@type dimensions: tuple
		@param dimensions: The (width, height) dimensions of this field.
		"""
		self._dimensions = (x, y) = dimensions
		self._pool = []
		self._pheromones = []
		self._grid = tuple([tuple([Space() for i in range(x)]) for j in range(y)])
		for (y, row) in enumerate(self._grid):
			for (x, space) in enumerate(row):
				self._pool.append(space)
				space.initialize(self, (x, y))
		self._pool = tuple(self._pool) #Can't use sets in 2.3.
		
	def addObject(self, obj):
		"""
		A convenience function that adds an object to the the space it claims as
		its current position.
		
		@type obj: inerts.Inert
		@param obj: The object to be added.
		
		@return: Nothing.
		"""
		space = self.getSpace(obj.getPosition())
		if space:
			space.addObject(obj)
			
	def addPheromone(self, pheromone):
		"""
		Registers a new pheromone in this field's collection.
		
		@type pheromone: inerts.Pheromone
		@param pheromone: The pheromone to be registered.
		
		@return: Nothing.
		"""
		self._pheromones.append(pheromone)
		
	def clearPath(self, start, end, pheromone=False, path=None):
		"""
		Determines whether end can be reached from start.
		
		This is a recursive function, but its impact shouldn't be all that great.
		
		@type start: tuple
		@param start: The (x, y) co-ordinates at which pathfinding will begin.
		@type end: tuple
		@param end: The (x, y) co-ordinate that is being sought.
		@type pheromone: bool
		@param pheromone: True if sponges should be considered walls.
		@type path: list
		@param path: A variable used by recursion; do not specify.
		
		@rtype: tuple
		@return: A boolean variable denoting the success of the operation and a
		    list of all spaces traversed to get there. Note that the list of
		    spaces will be empty if there are no walls on the field, because all
		    paths will be clear by nature.
		"""
		if WALLS:
			if path is None:
				path = []
			path.append(self.getSpace(start))
			
			next = nextPositionByGoal(start, end)
			next_space = self.getSpace(next)
			if start == end or not next_space:
				return (True, path)
				
			if not next_space.isOpen(pheromone):
				return (False, path)
				
			return self.clearPath(next, end, pheromone, path)
		else:
			return (True, [])
			
	def exists(self, target):
		"""
		Determines whether an entity can be seen in this field.
		
		@type target: shared.Traceable
		@param target: The entity being evaluated.
		
		@rtype: bool
		@return True if the entity is visible.
		"""
		if not target.isVisible():
			return False
			
		if isinstance(target, agents.Agent):
			return target in self.getSpace(target.getPosition()).getAgents((type(target),), target.getColony())
		elif type(target) is inerts.Pheromone: #A pheromone.
			return not self.getSpace(target.getPosition()).getPheromones((target.getType(),), target.getColony()) == []
		else: #An object.
			return target in self.getSpace(target.getPosition()).getObjects((type(target),), target.getColony())
			
	def flowPheromones(self, field):
		"""
		Reads pheromones from the provided previous field and transposes an
		updated map into this one.
		
		@type field: Field
		@param field: The old field.
		
		@return: Nothing.
		"""
		pheromones_processed = 0
		for old_space in field.getAllSpaces():
			#Finalize distribution.
			old_space.sumPheromones()
			
			space = self.getSpace(old_space.getPosition())
			for pheromone in old_space.getPheromones():
				pheromone.tick()
				if pheromone.exists():
					space.setPheromone(pheromone)
				pheromones_processed += 1
		return pheromones_processed
		
	def getAllSpaces(self):
		"""
		Returns all spaces that comprise this field; order is not defined.
		
		@rtype: tuple
		@return: A collection of all spaces in this field.
		"""
		return self._pool
		
	def getDimensions(self):
		"""
		Returns the dimensions of this field.
		
		@rtype: tuple
		@return: The (width, height) dimensions of this field.
		"""
		return self._dimensions
		
	def getPheromones(self):
		"""
		Returns all pheromones present in this field.
		
		Caution:: The list returned is not a copy. Do not modify.
		
		@rtype: list
		@return: A list of all pheromones in this field.
		"""
		return self._pheromones#[:] (I'll trust myself 'cause duplicating this over and over would be super-expensive.
		
	def getSpace(self, position):
		"""
		Returns the requested space from this field.
		
		@type position: tuple
		@param position: The (x, y) co-ordinate of the space to be retrieved.
		
		@rtype: Space
		@return: The requested space or None if it is out of bounds.
		"""
		(x, y) = position
		(x_max, y_max) = self._dimensions
		if y >= 0 and x >= 0 and y < y_max and x < x_max:
			return self._grid[y][x]
		return None
		
	def getSpaces(self, position, sense_range):
		"""
		Builds a list of all spaces within a specified distance from the
		specified space. Returned spaces are sorted in order of proximity.
		
		@type position: tuple
		@param position: The (x, y) co-ordinates around which construction will
		    occur.
		@type sense_range: int
		@param sense_range: The distance limiter.
		
		@rtype: list
		@return: A list of all spaces in range of the specified position, ordered
		    by increasing distance.
		"""
		space = self.getSpace(position)
		if sense_range == 1: #No work necessary.
			return space.getVonNeumann() + space.getMooreNoOverlap()
			
		(x, y) = position
		spaces = [space]
		for i in range(1, sense_range + 1):
			spaces += self._getSpacesArc(x, y - i, 1, 1, i)
			spaces += self._getSpacesArc(x + i, y, -1, 1, i)
			spaces += self._getSpacesArc(x, y + i, -1, -1, i)
			spaces += self._getSpacesArc(x - i, y, 1, -1, i)
		return spaces
		
	def getSpacesByProximity(self, position):
		"""
		Returns all spaces that comprise this field; order is defined in terms of
		increasing distance relative to a specified point.
		
		@type position: tuple
		@param position: The (x, y) co-ordinates around which distance will be
		    calculated.
		
		@rtype: list
		@return: A collection of all spaces in this field.
		"""
		(x, y) = position
		current_space = self.getSpace(position)
		spaces_in_range = []
		for space in self._pool:
			spaces_in_range.append((current_space.calcDistance(space.getPosition()), space))
		spaces_in_range.sort() #2.3 is limited. :(
		return [space for (distance, space) in spaces_in_range]
		
	def getSpacesInSight(self, position, range):
		"""
		Builds a list, in increasing distance, of spaces within the specificed
		sight range.
		
		@type position: tuple
		@param position: The (x, y) co-ordinates around which sensing will occur.
		@type range: int
		@param range: The maximum distance at which spaces can be sensed.
		
		@rtype: list
		@return: The requested list of spaces.
		"""
		return self._getAccessibleSpaces(position, range, False)
		
	def getSpacesInSmell(self, position, range):
		"""
		Builds a list, in increasing distance, of spaces within the specificed
		smell range. This function is now unused, but it is kept in case a later
		extension needs it.
		
		@type position: tuple
		@param position: The (x, y) co-ordinates around which sensing will occur.
		@type range: int
		@param range: The maximum distance at which spaces can be sensed.
		
		@rtype: list
		@return: The requested list of spaces.
		"""
		return self._getAccessibleSpaces(position, range, True)
		
	def _getAccessibleSpaces(self, position, range, smell):
		"""
		Builds a list of all spaces that can be radially accessed from a given
		position.
		
		@type position: tuple
		@param position: The position around which spaces will be scanned.
		@type range: int
		@param range: The maximum distance of any space that will be returned.
		@type smell: bool
		@param smell: True if sensing based on pheromones.
		
		@rtype: list
		@return: A list of all spaces accessible from the current position,
		    ordered by increasing distance.
		"""
		spaces = self.getSpaces(position, range)
		if WALLS:
			max_spaces = len(spaces) - 1
			access_map = [None for space in spaces]
			
			reversed_spaces = spaces[:]
			reversed_spaces.reverse() #2.3 is made of old. :(
			for (i, space) in enumerate(reversed_spaces):
				if access_map[i] is None:
					#Work inward to reduce checks.
					(result, path) = self.clearPath(space.getPosition(), position, smell)
					for p_space in path:
						access_map[max_spaces - spaces.index(p_space)] = result
						
			access_map.reverse() #2.3 is made of old. :(
			return [space for (space, shadow) in zip(spaces, access_map) if shadow]
		else:
			return spaces
			
	def _getSpacesArc(self, x, y, x_offset, y_offset, sense_range):
		"""
		Returns a line of spaces from a given starting position in a certain
		direction.
		
		@type x: int
		@param x: The x-co-ordinate at which gathering will begin.
		@type y: int
		@param y: The y-co-ordinate at which gathering will begin.
		@type x_offset: int
		@param x_offset: The amount to add to x each iteration.
		@type y_offset: int
		@param y_offset: The amount to add to y each iteration.
		@type sense_range: int
		@param sense_range: The length of the line to build.
		
		@rtype: list
		@return: All spaces that exist along the constructed line.
		"""
		arc = []
		for i in range(sense_range): #Go 'til the start of the next axis.
			space = self.getSpace((x, y))
			if space:
				arc.append(space)
			x += x_offset
			y += y_offset
		return arc
		
		
class Space(object):
	"""
	A space within a Field. These contain information about the state of the
	system.
	"""
	_pheromones = None #: A list of all signals in this space.
	_pheromone_pool = None #:  dictionary used to gather pheromone data.
	_agents = None #: A list of all agents currently occupying this space.
	_objects = None #: A list of all inert objects occupying this space.
	_neighbourhood = None #: A list of neighbours in the Moore neighbourhood, arranged in clockwise fashion, starting at the top centre.
	_position = None #: The (x, y) position of this space in the field.
	_field = None #: The Field to which this space belongs.
	
	def __init__(self):
		"""
		Creates a new Space instance.
		"""
		self._pheromone_pool = {}
		self._agents = []
		self._objects = []
		self._pheromones = []
		
	def addAgent(self, agent):
		"""
		Adds an agent to this space.
		
		@type agent: agents.Agent
		@param agent: The agent to be added.
		
		@return: Nothing.
		"""
		self._agents.append(agent)
		
	def addObject(self, obj):
		"""
		Adds an object to this space.
		
		@type obj: inerts.Inert
		@param obj: The object to be added.
		
		@return: Nothing.
		"""
		self._objects.append(obj)
		
	def addPheromone(self, pheromone_type, pheromone_colony, pheromone_intensity):
		"""
		Creates a new pheromone and adds it to this space.
		
		@type pheromone_type: int
		@param pheromone_type: A signal enumeration constant denoting the type of
		    pheromone being added.
		@type pheromone_colony: colony.Colony
		@param pheromone_colony: The colony with which the pheromone is
		    associated, or None if it is associated with threats.
		@type pheromone_intensity: number
		@param pheromone_intensity: The strength of the pheromone being created.
		
		@return: Nothing.
		"""
		self.setPheromone(inerts.Pheromone(pheromone_type, pheromone_colony, pheromone_intensity, self._position))
		
	def calcDistance(self, position):
		"""
		Returns the distance between this space and an arbitrary position.
		
		This function is a convenience that saves a function call.
		
		@rtype: int
		@return: The distance between this space and the spoecified position.
		"""
		return calcDistance(self._position, position)
		
	def getAgents(self, types=None, colony=None):
		"""
		Returns all agents in this space that match the specified criteria.
		
		@type types: sequence
		@param types: A list of types by which the query should be filtered. If
		    not specified, all types will be considered valid.
		@type colony: colony.Colony
		@param colony: The colony by which the query should be filtered. If not
		    specified, all colonies will be considered valid.
		
		@rtype: list
		@return: A list of all agents in this space that match the specified
		    criteria.
		"""
		agents_l = self._agents[:]
		if types:
			agents_l = [agent for agent in agents_l if type(agent) in types]
		if colony:
			agents_l = [agent for agent in agents_l if agent.getColony() == colony]
			
		return [agent for agent in agents_l if agent.isVisible()]
		
	def getMoore(self):
		"""
		Returns all spaces immediately surrounding this space.
		
		@rtype: list
		@return: A list of the requested spaces.
		"""
		return [space for space in self._neighbourhood if space]
		
	def getMooreNoOverlap(self):
		"""
		Returns all spaces at immediate diagonals to this space.
		
		@rtype: list
		@return: A list of the requested spaces.
		"""
		return [space for (i, space) in enumerate(self._neighbourhood) if space and i % 2]
		
	def getObjects(self, types=None, colony=None):
		"""
		Returns all objects in this space that match the specified criteria.
		
		@type types: sequence
		@param types: A list of types by which the query should be filtered. If
		    not specified, all types will be considered valid.
		@type colony: colony.Colony
		@param colony: The colony by which the query should be filtered. If not
		    specified, all colonies will be considered valid.
		
		@rtype: list
		@return: A list of all objects in this space that match the specified
		    criteria.
		"""
		objects = self._objects[:]
		if types:
			objects = [obj for obj in objects if type(obj) in types]
		if colony:
			objects = [obj for obj in objects if obj.getColony() == colony]
			
		return objects
		
	def getPheromones(self, types=None, colony=None):
		"""
		Returns all pheromones in this space that match the specified criteria.
		
		@type types: sequence
		@param types: A list of types by which the query should be filtered. If
		    not specified, all types will be considered valid.
		@type colony: colony.Colony
		@param colony: The colony by which the query should be filtered. If not
		    specified, all colonies will be considered valid.
		
		@rtype: list
		@return: A list of all pheromones in this space that match the specified
		    criteria.
		"""
		pheromones = self._pheromones[:]
		if types:
			pheromones = [pheromone for pheromone in pheromones if pheromone.getType() in types]
		if colony:
			pheromones = [pheromone for pheromone in pheromones if not pheromone.getColony() or pheromone.getColony() == colony]
			
		return pheromones
		
	def getPosition(self):
		"""
		Indicates the position of this space.
		
		@rtype: tuple
		@return: The (x, y) co-ordinates of this space.
		"""
		return self._position
		
	def getVonNeumann(self):
		"""
		Returns all spaces immediately adjacent to this space.
		
		@rtype: list
		@return: A list of the requested spaces.
		"""
		return [space for (i, space) in enumerate(self._neighbourhood) if space and not i % 2]
		
	def initialize(self, field, position):
		"""
		Once every space in a field has been constructed, this function is used
		to build neighbourhood mappings.
		
		@type field: Field
		@param field: The field to which this Space belongs.
		@type position: tuple
		@param position: The (x, y) co-ordinates of this Space.
		
		@return: Nothing.
		"""
		self._position = (x, y) = position
		self._neighbourhood = (
		 field.getSpace((x, y - 1)),
		 field.getSpace((x + 1, y - 1)),
		 field.getSpace((x + 1, y)),
		 field.getSpace((x + 1, y + 1)),
		 field.getSpace((x, y + 1)),
		 field.getSpace((x - 1, y + 1)),
		 field.getSpace((x - 1, y)),
		 field.getSpace((x - 1, y - 1))
		)
		self._field = field
		
	def isOpen(self, pheromone=False):
		"""
		Indicates whether entities can pass through or be detected through this
		space.
		
		@type pheromone: bool
		@param pheromone: True if only pheromone entities should be considered.
		
		@rtype: bool
		@return: True if this space is open.
		"""
		if pheromone:
			return not self.getObjects((inerts.Sponge, inerts.Wall))
		return not self.getObjects((inerts.Wall,))
		
	def setPheromone(self, pheromone):
		"""
		Places a pheromone into this space.
		
		@type pheromone: inerts.Pheromone
		@param pheromone: The pheromone to be added.
		
		@return: Nothing.
		"""
		colony = self._pheromone_pool.get(pheromone.getColony())
		if colony is None:
			colony = {}
			self._pheromone_pool[pheromone.getColony()] = colony
			
		type = self._pheromone_pool.get(pheromone.getType())
		if type is None:
			type = []
			colony[pheromone.getType()] = type
			
		type.append(pheromone)
		
	def sumPheromones(self):
		"""
		Combines like pheromones into a single pheromone within this space,
		applying a linear stacking effect and reducing the number of things the
		system needs to keep track of.
		
		@return: Nothing.
		"""
		self._pheromones = []
		for (colony, types) in self._pheromone_pool.iteritems():
			for (type, pheromones) in types.iteritems():
				pheromones = [(pheromone.getIntensity(), pheromone) for pheromone in pheromones]
				pheromones.sort()
				
				lead_pheromone = pheromones[-1][1]
				for pheromone in pheromones[:-1]:
					lead_pheromone.boostIntensity(pheromone[1].disperse())
				self._pheromones.append(lead_pheromone)
				self._field.addPheromone(lead_pheromone)
		self._pheromone_pool = None
		
		
def calcDistance(p1, p2):
	"""
	Determines the distance between two positions by using the D&D algorithm.
	
	@type p1: tuple
	@param p1: The (x, y) co-ordinates of the first position.
	@type p2: tuple
	@param p2: The (x, y) co-ordinates of the second position.
	
	@rtype: int
	@return: The distance between the two positions.
	"""
	if p1 == p2:
		return 0
		
	(x1, y1) = p1
	(x2, y2) = p2
	abs_x = abs(x1 - x2)
	abs_y = abs(y1 - y2)
	if abs_x <= 1 and abs_y <= 1:
		return 1
		
	offset = 0
	if abs_x > 0 and abs_y > 0:
		offset = 1
	return abs_x + abs_y - offset
	
def calcInverseSquare(distance, sense_range, intensity):
	"""
	Determines the strength of a pheromone relative to an agent's position.
	
	Note:: Older versions of this algorithm would assign negative intensity to
	pheromones closer than sense_range. This produced undesirable results.
	
	@type distance: int
	@param distance: The distance between the agent and the pheromone.
	@type sense_range: number
	@param sense_range: The strength of the agent's sense of smell, used to
	    reduce the drop-off affecting distant pheromones or to intensify the
	    strength of those nearby.
	@type intensity: float
	@param intensity: The strength of the pheromone being evaluated.
	
	@rtype: float
	@return: The perceived intensity of the pheromone.
	"""
	radius = None
	if sense_range > distance:
		radius = distance / sense_range
	else:
		radius = distance - sense_range
		
	if radius <= 0:
		return intensity
	else:
		return intensity / (radius * FOUR_PI)
		
def findAngle(start, end):
	"""
	Determines the angle between two positions.
	
	Note:: Older versions of this algorithm worked in terms of floating-point
	values. Integers will now be returned because they are faster.
	
	@type start: tuple
	@param start: The (x, y) co-ordinates of the starting location.
	@type end: tuple
	@param start: The (x, y) co-ordinates of the ending location.
	
	@rtype: int
	@return: The angle between the two positions, with up being 0.
	"""
	(x1, y1) = start
	(x2, y2) = end
	adjacent = x2 - x1 
	opposite = y2 - y1
	
	if adjacent == 0:
		if opposite > 0:
			return 180
		else:
			return 0
	if opposite == 0:
		if adjacent > 0:
			return 90
		else:
			return 270
			
	#Did away with floating point math to increase speed at the cost of a tiny amount of accuracy. (Insignificant)
	angle = int((90 + math.degrees(math.atan(float(opposite) / adjacent))))
	if adjacent < 0:
		angle += 180
	return angle % 360
	
def findClosestEntity(start, entities):
	"""
	Searches through a list of entites to find the one closest to the provided
	position.
	
	@type start: tuple
	@param start: The (x, y) co-ordinate around which the search will be performed.
	@type entities: list
	@param entities: A list of shared.Traceable objects.
	
	@rtype: shared.Traceable
	@return: The closest entity to the specified position or None if no entities
	    are provided.
	"""
	if not entities:
		return None
		
	entity = entities[0]
	position = entity.getPosition()
	distance = calcDistance(start, position)
	for n_entity in entities[1:]:
		n_position = n_entity.getPosition()
		n_distance = calcDistance(start, n_position)
		if n_distance < distance:
			distance = n_distance
			position = n_position
			entity = n_entity
			
	return (position, entity)
	
def nextPositionByAngle(start, angle):
	"""
	Determines the co-ordinates of the next position that would be reached if
	an agent were to advance at the given angle.
	
	Note:: Older versions of this algorithm worked in terms of floating-point
	values. While such values are still accepted, they are discouraged and
	rounding errors are accepted in favour of speed. (The net result will be
	unchanged)
	
	@type start: tuple
	@param start: The (x, y) co-ordinates of the starting location.
	@type angle: number
	@param angle: The angle in which travel would take place.
	
	@rtype: tuple
	@return: The (x, y) co-ordinates of the next position that would be reached.
	"""
	(x, y) = start
	angle = angle
	
	if angle <= 22 or angle > 337:
		return (x, y - 1)
	if 22 < angle <= 67:
		return (x + 1, y - 1)
	if 67 < angle <= 112:
		return (x + 1, y)
	if 112 < angle <= 157:
		return (x + 1, y + 1)
	if 157 < angle <= 202:
		return (x, y + 1)
	if 202 < angle <= 247:
		return (x - 1, y + 1)
	if 247 < angle <= 292:
		return (x - 1, y)
	if 292 < angle <= 337:
		return (x - 1, y - 1)
	
def nextPositionByGoal(start, end):
	"""
	Determines which space is the next one along the line between start and end.
	
	@type start: tuple
	@param start: The (x, y) co-ordinates of the starting position.
	@type end: tuple
	@param end: The (x, y) co-ordinates of the goal position.
	
	@rtype: tuple
	@return: The next (x, y) co-ordinate that needs to be traversed to reach end.
	"""
	if start == end:
		return end
	return nextPositionByAngle(start, findAngle(start, end))
	
