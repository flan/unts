# -*- coding: utf-8 -*-
"""
Unts module: colony; contains instances of colonies, which contain hills and
unts.
"""
from shared import *
import agents

import math

class Colony(object):
	"""
	A colony to which unts and related things like hills and pheromones may
	belong.
	"""
	PHEROMONES = None #: The intensity of pheromones dropped to indicate the presence of resources.
	PHEROMONES_GRADIENT = None #: The rate of exponential decay that gets applied to the pheromones dropped as a worker returns from a resource.
	PHEROMONES_ATTACK = None #: The intensity of pheromones dropped to indicate the presence of danger.
	LIFESPAN = None #: The number of ticks that unts in this colony will live beyond the reproduction tick-count.
	IMPORTANCE_EXPANSION = None #: Higher values give spawning priority to hills that are more likely to produce an architect.
	IMPORTANCE_GROWTH = None #: Higher values give spawning priority to hills that comprise large amounts of the colony's population.
	IMPORTANCE_RESOURCES = None #: Higher values give spawning priority to hills that yeild more resources.
	IMPORTANCE_TERRITORY = None #: Higher values give spawning priority to hills that are under attack, since gaining dominance will subdue rivals.
	HILL_COLOUR = None #: The colour of this colony's hills.
	ARCHITECTS = None #: A dictionary containing properties common to all of this colony's architects.
	BUILDERS = None #: A dictionary containing properties common to all of this colony's builders.
	WARRIORS = None #: A dictionary containing properties common to all of this colony's warriors.
	WORKERS = None #: A dictionary containing properties common to all of this colony's workers.
	
	_consumption_food = 0 #: A cached total representing the amount of food that all unts can possibly consume.
	_consumption_water = 0 #: A cached total representing the amount of water that all unts can possibly consume.
	_available_food = None #: The total amount of food that this colony has in reserve.
	_available_water = None #: The total amount of water that this colony has in reserve.
	_hills = None #: The hills that exist under this colony.
	_reproduction = None #: The number of ticks left until this colony tries to reproduce again.
	_architects = None #: The architects this colony currently has in play.
	
	def __init__(self, config_data):
		"""
		Initializes this colony based on the configuration data supplied.
		
		@type config_data: dict
		@param config_data: A collection of configuration variables used to
		    initialize this colony.
		"""
		self.ARCHITECTS = {
		 'size': 0.25
		}
		self.BUILDERS = {
		}
		self.WARRIORS = {
		 'size': 0.5
		}
		self.WORKERS = {
		 'size': 0.25
		}
		
		self.PHEROMONES = config_data.get('pheromones')
		self.PHEROMONES_GRADIENT = config_data.get('pheromones_gradient')
		self.PHEROMONES_ATTACK = config_data.get('pheromones_attack')
		self.LIFESPAN = config_data.get('lifespan')
		
		self.IMPORTANCE_EXPANSION = config_data.get('importance_expansion')
		self.IMPORTANCE_GROWTH = config_data.get('importance_growth')
		self.IMPORTANCE_RESOURCES = config_data.get('importance_resources')
		self.IMPORTANCE_TERRITORY = config_data.get('importance_territory')
		
		self.HILL_COLOUR = config_data.get('hill_colour')
		
		unt = config_data.get('architects')
		self.ARCHITECTS['energy'] = unt.get('energy')
		self.ARCHITECTS['sight'] = unt.get('sight')
		self.ARCHITECTS['colour'] = unt.get('colour')
		self.ARCHITECTS['spawning_builder_ratio'] = unt.get('spawning_builder_ratio')
		
		unt = config_data.get('builders')
		self.BUILDERS['energy'] = unt.get('energy')
		self.BUILDERS['consumption_food'] = unt.get('consumption_food')
		self.BUILDERS['consumption_water'] = unt.get('consumption_water')
		
		unt = config_data.get('warriors')
		self.WARRIORS['energy'] = unt.get('energy')
		self.WARRIORS['consumption_food'] = unt.get('consumption_food')
		self.WARRIORS['consumption_water'] = unt.get('consumption_water')
		self.WARRIORS['decay'] = unt.get('decay')
		self.WARRIORS['escort'] = unt.get('escort')
		self.WARRIORS['growth'] = unt.get('growth')
		self.WARRIORS['population_minimum'] = unt.get('population_minimum')
		self.WARRIORS['sight'] = unt.get('sight')
		self.WARRIORS['smell'] = unt.get('smell')
		self.WARRIORS['colour'] = unt.get('colour')
		
		unt = config_data.get('workers')
		self.WORKERS['energy'] = unt.get('energy')
		self.WORKERS['consumption_food'] = unt.get('consumption_food')
		self.WORKERS['consumption_water'] = unt.get('consumption_water')
		self.WORKERS['carrying_capacity'] = unt.get('carrying_capacity')
		self.WORKERS['boldness'] = unt.get('boldness')
		self.WORKERS['escort'] = unt.get('escort')
		self.WORKERS['growth'] = unt.get('growth')
		self.WORKERS['no_focus'] = unt.get('no_focus')
		self.WORKERS['stochastic_probability'] = unt.get('stochastic_probability')
		self.WORKERS['sight'] = unt.get('sight')
		self.WORKERS['smell'] = unt.get('smell')
		self.WORKERS['colour'] = unt.get('colour')
		
		self._available_food = self._seed_food = config_data.get('food')
		self._available_water = self._seed_water = config_data.get('water')
		
		self._hills = []
		self._architects = []
		self._reproduction = ENVIRONMENT.REPRODUCTION
		
	def addFood(self, amount):
		"""
		Adds food to this colony's resource stockpile.
		
		@type amount: number
		@param amount: The amount of food being added.
		
		@return: Nothing.
		"""
		self._available_food += amount
		
	def addHill(self, hill):
		"""
		Adds a hill to this colony.
		
		@type hill: inerts.Hill
		@param hill: The hill ot be added.
		
		@return: Nothing.
		"""
		self._hills.append(hill)
		
	def addUnt(self, unt):
		"""
		Adds a new unt to this colony's statistics.
		
		@type unt: agents.Unt
		@param unt: The unt being added to this colony.
		
		@return: Nothing.
		"""
		if type(unt) is agents.Architect:
			self._architects.append(unt)
		else:
			self._consumption_food += unt.getConsumptionFood()
			self._consumption_water += unt.getConsumptionWater()
			
	def addWater(self, amount):
		"""
		Adds water to this colony's resource stockpile.
		
		@type amount: number
		@param amount: The amount of water being added.
		
		@return: Nothing.
		"""
		self._available_water += amount
		
	def getArchitects(self):
		"""
		Returns a list of all architects that belong to this colony.
		
		@rtype: list
		@return: A list of agents.Architect objects.
		"""
		return self._architects[:]
		
	def getConsumptionFood(self):
		"""
		Returns the total amount of food that could conceivably be consumed by
		all unts in this colony.
		
		@rtype: number
		@return: The total food-consumption-capacity of this colony's unts.
		"""
		return self._consumption_food
		
	def getConsumptionWater(self):
		"""
		Returns the total amount of water that could conceivably be consumed by
		all unts in this colony.
		
		@rtype: number
		@return: The total water-consumption-capacity of this colony's unts.
		"""
		return self._consumption_water
		
	def getFood(self):
		"""
		Returns the total amount of food that this colony has.
		
		@rtype: number
		@return: The total amount of food that this colony has.
		"""
		return self._available_food
		
	def getHills(self):
		"""
		Returns a list of all hills belonging to this colony.
		
		@rtype: list
		@return: A list of inerts.Hill objects.
		"""
		return self._hills[:]
		
	def getRiskFood(self):
		"""
		Gets a risk-assessment value related to this colony's available food
		versus potential consumption values, which is used to determine which
		resource to prioritize. Lower values mean less of a need for food.
		
		@rtype: number
		@return: This colony's food-risk value.
		"""
		return -(self._available_food - (self._consumption_food * 2))
		
	def getRiskWater(self):
		"""
		Gets a risk-assessment value related to this colony's available water
		versus potential consumption values, which is used to determine which
		resource to prioritize. Lower values mean less of a need for water.
		
		@rtype: number
		@return: This colony's water-risk value.
		"""
		return -(self._available_water - (self._consumption_water * 2))
		
	def getUntCount(self):
		"""
		Returns the number of unts that belong to this colony.
		
		@rtype: int
		@return: The number of unts that belong to this colony.
		"""
		unts = len(self._architects)
		for hill in self._hills:
			unts += hill.getUntCount()
		return unts
		
	def getUnts(self):
		"""
		Returns a list of all unts that belong to this colony.
		
		@rtype: list
		@return: A list of agents.Unt objects.
		"""
		unts = self._architects[:]
		for hill in self._hills:
			unts += hill.getUnts()
		return unts
		
	def getWater(self):
		"""
		Returns the total amount of water that this colony has.
		
		@rtype: number
		@return: The total amount of water that this colony has.
		"""
		return self._available_water
		
	def getWorkerToWarriorRatio(self):
		"""
		Returns the ratio of workers to warriors within this colony.
		
		@rtype: float
		@return: The ratio of workers to warriors as a percentage.
		"""
		workers = 0
		warriors = 0
		for hill in self._hills:
			workers += hill.getWorkerCount()
			warriors += hill.getWarriorCount()
			
		if not workers and not warriors:
			return 1.0
		return float(workers) / (workers + warriors)
		
	def removeFood(self, amount):
		"""
		Removes food from this colony's stockpile.
		
		@type amount: number
		@param amount: The amount of food being removed.
		
		@rtype: bool
		@return: True if this colony had enough resources to cover the withdrawl.
		"""
		if self._available_food > 0:
			self._available_food -= amount
			return True
		return False
		
	def removeUnt(self, unt):
		"""
		Removed an unt from this colony's statistics.
		
		@type unt: agents.Unt
		@param unt: The unt being removed from this colony.
		
		@return: Nothing.
		"""
		if type(unt) is agents.Architect:
			self._architects.remove(unt)
		else:
			self._consumption_food -= unt.getConsumptionFood()
			self._consumption_water -= unt.getConsumptionWater()
			
	def removeWater(self, amount):
		"""
		Removes water from this colony's stockpile.
		
		@type amount: number
		@param amount: The amount of water being removed.
		
		@rtype: bool
		@return: True if this colony had enough resources to cover the withdrawl.
		"""
		if self._available_water > 0:
			self._available_water -= amount
			return True
		return False
		
	def tick(self):
		"""
		Executes housekeeping tasks that need to be performed every iteration.
		
		Right now, this is just a matter of checking to see whether it is time
		for the colony to reproduce, and determining how large a brood to produce
		if it is time and it is possible.
		
		@return: Nothing.
		"""
		self._reproduction -= 1
		if not self._reproduction:
			surplus_food = (self._available_food - self._consumption_food) * ENVIRONMENT.RESOURCES_RESERVE
			surplus_water = (self._available_water - self._consumption_water) * ENVIRONMENT.RESOURCES_RESERVE
			existing_unts = self.getUntCount()
			unts_new = (min(surplus_food, surplus_water) * existing_unts)
			if not existing_unts: #Restart the colony.
				unts_new = len(self._hills) * ENVIRONMENT.RESTART_FACTOR
				if self._available_food <= 0:
					self._available_food = self._seed_food
				if self._available_water <= 0:
					self._available_water = self._seed_water
			elif unts_new < 0:
				unts_new = 0
				
			if existing_unts and unts_new < ENVIRONMENT.GENERATION_MINIMUM * existing_unts:
				self._reproduction = ENVIRONMENT.REPRODUCTION_DELAY
			else: #Proceed with the "LIFE GOES ON!" strategy, or go normally. Whichev'.
				self._reproduction = ENVIRONMENT.REPRODUCTION
				self._reproduce(unts_new)
				
	def _reproduce(self, unts_new):
		"""
		Determines which hills will got how much of the new brood, and causes them
		to spawn a new generation as needed.
		
		@type unts_new: int
		@param unts_new: The number of new unts to be allocated amongst this
		    colony's hills.
		
		@return: Nothing.
		"""
		food_gathered = 0
		water_gathered = 0
		population = 0
		for hill in self._hills:
			food_gathered += hill.getFoodGathered()
			water_gathered += hill.getWaterGathered()
			population += hill.getUntCount()
			
		priority_sum = 0
		hills = []
		for hill in self._hills:
			priority = hill.getPriority((food_gathered or 1), (water_gathered or 1), (population or 1))
			priority_sum += priority
			hills.append((priority, hill))
			
		for (priority, hill) in hills:
			hill.spawnGeneration(int(math.ceil((float(priority) / (priority_sum or 1)) * unts_new)) or 1)
			
