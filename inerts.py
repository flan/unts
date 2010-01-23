# -*- coding: utf-8 -*-
"""
Unts module: inerts; contains objects that remain stationary.
"""
from shared import *
import shared
import breve
import agents

class Inert(shared.Traceable, breve.Stationary):
	"""
	An abstract class defining anything that exists on the field in a stationary,
	permanent state.
	"""
	def __init__(self):
		"""
		Inert is meaningless by itself, so instantiating it will result in an
		exception.
		
		@raise Exception: Always.
		"""
		raise Exception("Unable to instantiate Inert.")
		
	def _init(self, position):
		"""
		Sets up Inert properties.
		
		@type position: tuple
		@param position: The (x, y) co-ordinates of this object.
		"""
		shared.Traceable._init(self, position)
		
		(x, y) = position
		breve.Stationary.__init__(self)
		self.move(breve.vector(x, y, 0))
		
	def plant(self, field):
		"""
		Places this object in the specified field.
		
		@type field: map.Field
		@param field: The field in which this object is to be placed.
		
		@return: Nothing.
		"""
		field.addObject(self)
		
		
class Hill(Inert):
	"""
	A hill is home to unts; it serves as a gathering place and an anchor for the
	expansion of a colony.
	"""
	_colony = None #: The colony with which this hill is associated.
	_builders = None #: A list of all builders currently attached to this hill.
	_warriors = None #: A list of all warriors currently attached to this hill.
	_workers = None #: A list of all corkers currently attached to this hill.
	_warriors_killed = 0 #: The number of warriors dispatched from this hill that were slain since the last generation.
	_workers_killed = 0 #: The number of workers dispatched from this hill that were slain since the last generation.
	_workers_lastgen = 0 #: The number of warriors spawned at this hill in the last generation.
	_warriors_lastgen = 0 #: The number of workers spawned at this hill in the last generation.
	_food_gathered = 0 #: The amount of food gathered by this hill since the last generation.
	_water_gathered = 0 #: The amount of water gathered by this hill since the last generation.
	_workers_unsuccessful = 0 #: The number of workers that came back empty-handed since the last generation.
	_workers_returned = 0 #: The number of workers that came back since the last generation.
	
	def __init__(self, colony, position):
		"""
		Creates a new Hill.
		
		@type colony: colony.Colony
		@param colony: The colony to which this hill is attached.
		@type position: tuple
		@param position: The (x, y) co-ordinates at which this hill exists.
		"""
		Inert._init(self, position)
		self._builders = []
		self._warriors = []
		self._workers = []
		self._colony = colony
		colony.addHill(self)
		
		self.setShape(breve.createInstances(breve.Cube, 1).initWith(breve.vector(0.75, 0.75, 0.75)))
		(c_r, c_g, c_b) = colony.HILL_COLOUR
		self.setColor(breve.vector(c_r, c_g, c_b))
		
	def addResource(self, payload):
		"""
		Deposits resources at this hill.
		
		@type payload: tuple
		@param payload: A resource constant identifying the type of resource being
		    deposited and the amount of the resource being deposited. payload may
		    be None if nothing was harvested; the worker will still go through the
		    depositing motions.
		    
		@return: Nothing.
		"""
		self._workers_returned += 1
		if payload:
			(resource, quantity) = payload
			if resource == RESOURCE_FOOD:
				self._colony.addFood(quantity)
				self._food_gathered += quantity
			else:
				self._colony.addWater(quantity)
				self._water_gathered += quantity
		else:
			self._workers_unsuccessful += 1
			
	def addUnt(self, unt):
		"""
		Attaches an unt to this hill; this happens because unts always return to
		the nearest hill, which serves to optimize workforce distribution in a
		colony.
		
		@type unt: agents.Unt
		@param unt: The unt being attached.
		
		@return: Nothing.
		"""
		if type(unt) == agents.Builder:
			self._builders.append(unt)
		elif type(unt) == agents.Warrior:
			self._warriors.append(unt)
		elif type(unt) == agents.Worker:
			self._workers.append(unt)
		self._colony.addUnt(unt)
		
	def generateUnts(self, workers, warriors, builders):
		"""
		Creates new unts to be attached to this hill.
		
		@type workers: int
		@param workers: The number of new workers to spawn.
		@type warriors: int
		@param warriors: The number of new warriors to spawn.
		@type builders: int
		@param builders: The number of new builders to spawn.
		
		@return: Nothing.
		"""
		for i in range(workers):
			agents.Worker(self)
		for i in range(warriors):
			agents.Warrior(self)
		self._builders = [] #Prevent generation overlap.
		for i in range(builders):
			agents.Builder(self)
			
		self._workers_lastgen = workers
		self._warriors_lastgen = warriors
		
	def getColony(self):
		return self._colony
		
	def getBuilders(self):
		"""
		Returns the builders attached to this hill.
		
		@rtype: list
		@return: The builders attached to this hill.
		"""
		return self._builders[:]
		
	def getFoodGathered(self):
		"""
		Returns the amount of food gathered by this hill in the last generation.
		
		@rtype: number
		@return: The amount of food gathered by this hill in the last generation.
		"""
		return self._food_gathered
		
	def getPriority(self, food_gathered, water_gathered, unt_count):
		"""
		Determines this hill's priority score, which is used to decide which hills
		get how many unts out of the total number available in the colony's brood.
		
		@type food_gathered: int
		@param food_gathered: The total amount of food gathered by the colony in
		    the last generation.
		@type water_gathered: int
		@param water_gathered: The total amount of water gathered by the colony in
		    the last generation.
		@type unt_count: int
		@param unt_count: The total amount of unts currently alive in the colony.
		
		@rtype: float
		@return: The hill's priority score.
		"""
		priority_control = self._colony.IMPORTANCE_EXPANSION * len(self._builders)
		priority_survival = self._colony.IMPORTANCE_TERRITORY * (self._workers_killed + self._warriors_killed)
		priority_race = self._colony.IMPORTANCE_RESOURCES * ((self._food_gathered / food_gathered) + (self._water_gathered / water_gathered))
		priority_size = self._colony.IMPORTANCE_GROWTH * (self.getUntCount() / unt_count)
		
		return priority_control + priority_survival + priority_race + priority_size
		
	def getUntCount(self):
		"""
		Returns the number of unts attached to this hill.
		
		@rtype: int
		@return: The number of unts attached to this hill.
		"""
		return len(self._builders) + len(self._warriors) + len(self._workers)
		
	def getUnts(self):
		"""
		Returns the unts attached to this hill.
		
		@rtype: list
		@return: The unts attached to this hill.
		"""
		return self._builders + self._warriors + self._workers
		
	def getWarriorCount(self):
		"""
		Returns the number of warriors attached to this hill.
		
		@rtype: int
		@return: The number of warriors attached to this hill.
		"""
		return len(self._warriors)
		
	def getWarriors(self):
		"""
		Returns the warriors attached to this hill.
		
		@rtype: list
		@return: The warriors attached to this hill.
		"""
		return self._warriors[:]
		
	def getWaterGathered(self):
		"""
		Returns the amount of water gathered by this hill in the last generation.
		
		@rtype: number
		@return: The amount of water gathered by this hill in the last generation.
		"""
		return self._water_gathered
		
	def getWorkerCount(self):
		"""
		Returns the number of workers attached to this hill.
		
		@rtype: int
		@return: The number of workers attached to this hill.
		"""
		return len(self._workers)
		
	def getWorkers(self):
		"""
		Returns the workers attached to this hill.
		
		@rtype: list
		@return: The workers attached to this hill.
		"""
		return self._workers[:]
		
	def removeUnt(self, unt, killed=False):
		"""
		Detaches an unt from this hill.
		
		@type unt: agents.Unt
		@param unt: The unt being detached.
		@type killed: bool
		@param killed: True if this unt was killed on the field; False if this
		    unt attached itself to another hill or died of natural causes.
		
		@return: Nothing.
		"""
		if type(unt) == agents.Builder:
			self._builders.remove(unt)
		elif type(unt) == agents.Warrior:
			self._warriors.remove(unt)
			if killed:
				self._warriors_killed += 1
		elif type(unt) == agents.Worker:
			self._workers.remove(unt)
			if killed:
				self._workers_killed += 1
		self._colony.removeUnt(unt)
		
	def spawnGeneration(self, unts_new):
		"""
		Determines how to divy up the number of new unts this hill will spawn. 
		
		Note:: Older versions of this algorithm had an architect-related glitch
		that would cause each hill to spawn an architect when the colony was dead
		because the calculation was based on >=, not >.
		
		@type unts_new: int
		@param unts_new: The number of new unts that this hill has to allocate.
		
		@return: Nothing.
		"""
		killed = self._workers_killed + self._warriors_killed
		available = unts_new - killed
		if unts_new == 1:
			self.generateUnts(1, 0, 0)
		elif killed > available:
			self.generateUnts(
			 int(unts_new * (float(self._workers_killed) / killed)),
			 int(unts_new * (float(self._warriors_killed) / killed)),
			 0
			)
		else:
			target_workers = int(((1 - (self._workers_unsuccessful / (self._workers_returned or 1))) * self._colony.WORKERS['growth']) * (self._workers_lastgen or 1))
			target_warriors = int(self._calculateInsecurity(killed) * (self._warriors_lastgen or 1))
			if target_workers + target_warriors <= available:
				unts_workers = self._workers_killed + target_workers
				unts_warriors = self._warriors_killed + target_warriors
				self.generateUnts(
				 unts_workers,
				 unts_warriors,
				 available - unts_workers - unts_warriors
				)
			else:
				targets = (target_workers + target_warriors)
				self.generateUnts(
				 int(self._workers_killed + available * (float(target_workers) / targets)),
				 int(self._warriors_killed + available * (float(target_warriors) / targets)),
				 0
				)
				
		#Spawn architect?
		if len(self._builders) > self._colony.ARCHITECTS['spawning_builder_ratio'] * self.getUntCount():
			agents.Architect(self)
			
		#Reset performance counters.
		self._workers_killed = 0
		self._warriors_killed = 0
		self._food_gathered = 0
		self._water_gathered = 0
		self._workers_unsuccessful = 0
		self._workers_returned = 0
		
	def summonBuilders(self):
		"""
		Causes this hill to scrap all of its builders and returns the number that
		used to exist. This is done so that an architect-spawned hill will have
		an initial unt complement.
		
		@rtype: int
		@return: The number of builders formerly associated with this hill.
		"""
		count = len(self._builders)
		for builder in self._builders:
			self.removeUnt(builder)
		return count
		
	def _calculateInsecurity(self, killed):
		"""
		Determines the insecurity co-efficient used to control the rate of growth
		or decay applied to this hill's warrior complement in the new generation.
		
		@type killed: int
		@param killed: The number of unts killed after being dispatched from this
		    hill in the last generation.
		
		@rtype: number
		@return: The insecurity co-efficient of this hill.
		"""
		if killed == 0: #safe
			if len(self._warriors) < self.getUntCount() * self._colony.WARRIORS['population_minimum']:
				return 1
			else:
				return self._colony.WARRIORS['decay']
		else: #unsafe
			return self._colony.WARRIORS['growth'] + (killed / (len(self._workers) + len(self._warriors) + killed))
			
			
class Pheromone(shared.Traceable):
	"""
	A signal that allows agents to communicate information.
	"""
	_exists = True #: False once this pheromone has dispersed and is awaiting deletion.
	_colony = None #: The colony with which this pheromone is associated, if any.
	_intensity = None #: The current strength of this pheromone.
	_type = None #: A signal constant indicating the natur of the message communicated by this pheromone.
	
	def __init__(self, type, colony, intensity, position):
		"""
		Creates a new Pheromone.
		
		@type type: int
		@param type: The signal constant that describes the message communicated
		    by this pheromone.
		@type colony: colony.Colony
		@param colony: The colony with which this pheromone is associated, or None
		    if it is associated with a threat.
		@type position: tuple
		@param position: The (x, y) co-ordinates of this pheromone.
		"""
		shared.Traceable._init(self, position)
		
		self._type = type
		self._colony = colony
		self._intensity = intensity
		
	def boostIntensity(self, amount):
		"""
		Causes this pheromone's strenght to be increased when it is joined by
		another like emission.
		
		@type amount: number
		@param amount: The intensity of the joining pheromone.
		
		@return: Nothing.
		"""
		self._intensity += amount * ENVIRONMENT.SIGNALS_COLLISION_FACTOR
		
	def disperse(self):
		"""
		Causes this pheromone to cease to exist in any meaningful capacity.
		
		@rtype: number
		@return: The intensity of this pheromone.
		"""
		if self._exists:
			self._exists = False
			return self._intensity
		return 0
		
	def exists(self):
		"""
		Indicates whether this pheromone has dispersed or not.
		
		@rtype: bool
		@return: True as long as this pheromone is still coherent.
		"""
		return self._exists
		
	def isVisible(self):
		return self._exists
		
	def getColony(self):
		return self._colony
		
	def getIntensity(self):
		"""
		Indicates the absolute strength of this pheromone.
		
		@rtype: number
		@return: The strength of this pheromone.
		"""
		return self._intensity
		
	def getType(self):
		"""
		Indicates the nature of this pheromone.
		
		@rtype: int
		@return: The signal constant associated with this pheromone's message.
		"""
		return self._type
		
	def tick(self):
		"""
		Causes this pheromone to decay.
		
		@return: Nothing.
		"""
		self._intensity *= ENVIRONMENT.SIGNALS_DISPERSION_FACTOR
		if self._intensity < 1:
			self.disperse()
			
			
class Resource(object):
	"""
	An abstract class the defines all resources that can exist within the system.
	"""
	_capacity = None #: The maximum capacity of this resource instance.
	_replenishment = None #: The percentage-based rate at which this resource instance replenishes itself.
	_cooldown = None #: The number of ticks required before this resource replenishes itself.
	_ticks = None #: The number of ticks remaining before this resource replenishes itself.
	_quantity = None #: The current number of resources held within this instance.
	
	def __init__(self):
		"""
		Resource is meaningless by itself, so instantiating it will result in an
		exception.
		
		@raise Exception: Always.
		"""
		raise Exception("Unable to instantiate Resource.")
		
	def _init(self, config_data, position):
		"""
		Sets up Resource properties.
		
		@type config_data: dict
		@param config_data: A collection of variables used to instantiate this
		    resource.
		@type position: tuple
		@param position: The (x, y) co-ordinates at which this object exists.
		"""
		Inert._init(self, position)
		self._quantity = self._capacity = config_data.get('capacity')
		self._replenishment = config_data.get('replenishment')
		self._ticks = self._cooldown = config_data.get('cooldown')
		RESOURCES.append(self)
		
		self.setShape(breve.createInstances(breve.Cube, 1).initWith(breve.vector(0.5, 0.5, 0.5)))
		
	def getType(self):
		"""
		Returns the enumeration constant associated with this resource.
		
		@rtype: int
		@return: A resource enumeration constant.
		"""
		pass
		
	def harvest(self, max):
		"""
		Allows a worker to harvest this resource. If this resource does not have
		enough material to fully satisfy the request, what's left is returned
		instead.
		
		@type max: number
		@param max: The amount of resources to try to harvest.
		
		@rtype: number
		@return: The amount of resources harvested.
		"""
		harvested = max
		if max >= self._quantity:
			harvested = self._quantity
			self._quantity = 0
		else:
			self._quantity -= max
		return harvested
		
	def tick(self):
		"""
		Determines whether it is time to replenish this resource.
		
		@return: Nothing.
		"""
		self._ticks -= 1
		if not self._ticks:
			self._ticks = self._cooldown
			self._quantity += self._capacity * self._replenishment
			if self._quantity > self._capacity:
				self._quantity = self._capacity
		self.setTransparency(float(self._quantity) / self._capacity)
		
		
class Food(Resource, Inert):
	"""
	Food is harvested by workers to keep their colonies alive.
	"""
	def __init__(self, config_data, position):
		"""
		Creates a new food instance.
		
		@type config_data: dict
		@param config_data: A collection of variables used to instantiate this
		    resource.
		@type position: tuple
		@param position: The (x, y) co-ordinates at which this object exists.
		"""
		Resource._init(self, config_data, position)
		
		(c_r, c_g, c_b) = ENVIRONMENT.FOOD_COLOUR
		self.setColor(breve.vector(c_r, c_g, c_b))
		
	def getType(self):
		return RESOURCE_FOOD
		
class Water(Resource, Inert):
	"""
	Water is harvested by workers to keep their colonies alive.
	"""
	def __init__(self, config_data, position):
		"""
		Creates a new water instance.
		
		@type config_data: dict
		@param config_data: A collection of variables used to instantiate this
		    resource.
		@type position: tuple
		@param position: The (x, y) co-ordinates at which this object exists.
		"""
		Resource._init(self, config_data, position)
		
		(c_r, c_g, c_b) = ENVIRONMENT.WATER_COLOUR
		self.setColor(breve.vector(c_r, c_g, c_b))
		
	def getType(self):
		return RESOURCE_WATER
		
		
class BaseWall(Inert):
	"""
	An abstract type that defines all walls that can exist within the system.
	"""
	def __init__(self):
		"""
		BaseWall is meaningless by itself, so instantiating it will result in an
		exception.
		
		@raise Exception: Always.
		"""
		raise Exception("Unable to instantiate BaseWall.")
		
	def _init(self, position):
		"""
		Sets up BaseWall properties.
		
		@type position: tuple
		@param position: The (x, y) co-ordinates at which this object exists.
		"""
		Inert._init(self, position)
		WALLS.append(self)
		
		self.setShape(breve.createInstances(breve.Cube, 1).initWith(breve.vector(0.33, 0.33, 0.33)))
	
class Sponge(BaseWall):
	"""
	Sponges absorb all pheromones that pass through them, but they do not
	impede sight or movement.
	"""
	def __init__(self, position):
		"""
		Builds a new Sponge instance.
		
		@type position: tuple
		@param position: The (x, y) co-ordinates at which this object exists.
		"""
		BaseWall._init(self, position)
		
		(c_r, c_g, c_b) = ENVIRONMENT.SPONGE_COLOUR
		self.setColor(breve.vector(c_r, c_g, c_b))
		
class Wall(Sponge):
	"""
	Walls extend sponges by impeding both sight and movement.
	"""
	def __init__(self, position):
		"""
		Builds a new Wall instance.
		
		@type position: tuple
		@param position: The (x, y) co-ordinates at which this object exists.
		"""
		BaseWall._init(self, position)
		
		(c_r, c_g, c_b) = ENVIRONMENT.WALL_COLOUR
		self.setColor(breve.vector(c_r, c_g, c_b))
		
