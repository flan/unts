# -*- coding: utf-8 -*-
"""
Unts module: shared; contains common constants and variables.
"""
import random
import breve

import environment

RANDOMIZER = None #: A seeded random number generator.
ENVIRONMENT = None #: The simulation environment rules.

COLONIES = [] #: A list of all colonies in the system.
THREATS = [] #: A list of all threats in the system.
WALLS = [] #: A list of all obstacles in the system.
RESOURCES = [] #: A list of all resources in the system.
AGENTS = [] #: A list of all non-threat agents that the system needs to animate.

BOLDNESS_PASSIVE = 1 #: An enumeration constant signifying passive behaviour.
BOLDNESS_ASSERTIVE = 2 #: An enumeration constant signifying assertive behaviour.
BOLDNESS_AGGRESSIVE = 3 #: An enumeration constant signifying aggressive behaviour.

RESOURCE_FOOD = 1 #: An enumeration constant signifying food resources.
RESOURCE_WATER = 2 #: An enumeration constant signifying water resources.
SIGNAL_THREAT = 3 #: An enumeration constant signifying threat signals.

STATUS_WANDERING = 1 #: An enumeration constant indicating that an agent is wandering.
STATUS_FOLLOWING = 2 #: An enumeration constant indicating that an agent is following an entity.
STATUS_KILLING = 4 #: An enumeration constant indicating that an agent is killing another agent.
STATUS_RETREATING = 5 #: An enumeration constant indicating that an agent is escaping the scene of an attack.
STATUS_BACKTRACKING = 6 #: An enumeration constant indicating that an agent is backing out of a dead end.
STATUS_TRACING = 7 #: An enumeration constant indicating that an agent is trying to find a way around a wall by following pheromones.
STATUS_DETOURING = 8 #: An enumeration constant indicating that an agent is trying to find a way around a wall.

def initialize(config_data):
	"""
	Reads data from seed.py and uses it to initialize global constants.
	
	@type config_data: dict
	@param config_data: A dictionary containing information about the simulation
	    environment.
	"""
	global ENVIRONMENT
	ENVIRONMENT = environment.Environment(config_data)
	global RANDOMIZER
	RANDOMIZER = random.Random(ENVIRONMENT.RANDOM_SEED)
	
class Traceable(object):
	"""
	An abstract super-class for everything that can exist within a field in the
	system.
	"""
	_position = None #: The (x, y) co-ordinate of this entity.
	
	def __init__(self):
		"""
		Traceable is meaningless by itself, so instantiating it will result in an
		exception.
		
		@raise Exception: Always.
		"""
		raise Exception("Unable to instantiate Traceable.")
		
	def _init(self, position):
		"""
		Used to initialize this entity.
		
		@type position: tuple
		@param position: The (x, y) co-ordinate of this entity.
		"""
		self._position = position
		
	def getColony(self):
		"""
		Indicates which colony is associated with this entity, if any.
		
		@rtype: colony.Colony
		@return: A Colony object, or None if this entity has no association.
		"""
		return None
		
	def getPosition(self):
		"""
		Indicates where this entity currently resides.
		
		@rtype: tuple
		@return: The (x, y) co-ordinates of this entity.
		"""
		return self._position
		
	def isVisible(self):
		"""
		Indicates whether this entity can be seen by agents.
		
		@rtype: bool
		@return: True if this entity is visible to agents.
		"""
		return True
		