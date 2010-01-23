# -*- coding: utf-8 -*-
"""
Unts module: environment; contains variables used to govern the simulation.
"""
class Environment(object):
	"""
	A collection of values that control the rules of a system.
	"""
	#Simulation
	FIELD_WIDTH = None #: Controls the width of the field.
	FIELD_HEIGHT = None #: Controls the height of the field.
	RANDOM_SEED = None #: Keep this constant to reproduce the same events in repeat runs.
	DECISION_FREQUENCY = None #: Used to cause agents to make decisions n% of the time; this can lead to dramatic speedups in exchange for stupider logic.
	
	#General
	MIN_BUILD_DISTANCE = None #: No colony's hills may be built closer than this many spaces.
	
	#Pathfinding
	WANDER_VARIANCE = None #: The probability that an agent will deviate from its current heading with each step.
	
	#Reproduction
	GENERATION_MINIMUM = None #: A new brood must be at least this big, relative to the previous one, for reproduction to occur; used to prevent waste.
	REPRODUCTION = None #: The number of ticks between reproductive cycles.
	REPRODUCTION_DELAY = None #: If a new brood would be too small, wait for this many ticks before trying again; prompts "LIFE GOES ON!" behaviour.
	RESOURCES_RESERVE = None #: The higher this is, the fewer excess resources will be required for a new unt to be spawned beyond the colony's previous values.
	RESTART_FACTOR = None #: The number of unts to spawn for each hill of a dead colony to bring it back to life.
	
	#Signals
	SIGNALS_DISPERSION_FACTOR = None #: How much of a pheromone persists after each cycle.
	SIGNALS_COLLISION_FACTOR = None #: How effectively like pheromones stack.
	
	#Threats
	KILL_TIME_ARCHITECT = None #: How long a threat will idle after killing an architect.
	KILL_TIME_WARRIOR = None #: How long a threat will idle after killing a warrior.
	KILL_TIME_WORKERS = None #: How long a threat will idle after killing a worker.
	
	#Resources
	FOOD_COLOUR = (0.75, 0.75, 0.75) #: The colour of food resources.
	WATER_COLOUR = (0.95, 0.95, 0.95) #: The colour of water resources.
	
	#Walls
	SPONGE_COLOUR = (0.65, 0.65, 0.65) #: The colour of a sponge.
	WALL_COLOUR = (0.0, 0.0, 0.0) #: The colour of a wall.
	
	PREDATORS = {
	 'colour': (0.2, 0.2, 0.2) #: The colour of a predator.
	} #: A set of attributes that are applied to each newly created predator.
	HUNTERS = {
	 'colour': (0.5, 0.5, 0.5) #: The colour of a hunter.
	} #: A set of attributes that are applied to each newly created hunter.
	STALKERS = {
	 'colour': (0.8, 0.8, 0.8) #: The colour of a stalker.
	} #: A set of attributes that are applied to each newly created stalker.
	
	def __init__(self, config_data):
		"""
		Initializes this Environment object.
		
		@type config_data: dict
		@param config_data: A dictionary containing the variables with which
		    this Environment object will be initialized.
		"""
		self.FIELD_WIDTH = config_data.get('field_width')
		self.FIELD_HEIGHT = config_data.get('field_height')
		self.RANDOM_SEED = config_data.get('random_seed')
		self.DECISION_FREQUENCY = config_data.get('decision_frequency')
		
		self.MIN_BUILD_DISTANCE = config_data.get('min_build_distance')
		
		self.WANDER_VARIANCE = config_data.get('wander_variance')
		
		self.GENERATION_MINIMUM = config_data.get('generation_minimum')
		self.REPRODUCTION = config_data.get('reproduction')
		self.REPRODUCTION_DELAY = config_data.get('reproduction_delay')
		self.RESOURCES_RESERVE = config_data.get('resources_reserve')
		self.RESTART_FACTOR = config_data.get('restart_factor')
		
		self.SIGNALS_DISPERSION_FACTOR = config_data.get('signals_dispersion_factor')
		self.SIGNALS_COLLISION_FACTOR = config_data.get('signals_collision_factor')
		
		self.KILL_TIME_ARCHITECT = config_data.get('kill_time_architect')
		self.KILL_TIME_WARRIOR = config_data.get('kill_time_warrior')
		self.KILL_TIME_WORKER = config_data.get('kill_time_worker')
		
		threat = config_data.get('predators')
		self.PREDATORS['health_points'] = threat.get('health_points')
		self.PREDATORS['nourishment'] = threat.get('nourishment')
		self.PREDATORS['sight'] = threat.get('sight')
		self.PREDATORS['lifespan'] = threat.get('lifespan')
		
		threat = config_data.get('hunters')
		self.HUNTERS['health_points'] = threat.get('health_points')
		self.HUNTERS['nourishment'] = threat.get('nourishment')
		self.HUNTERS['sight'] = threat.get('sight')
		self.HUNTERS['lifespan'] = threat.get('lifespan')
		self.HUNTERS['pheromones'] = threat.get('pheromones')
		
		threat = config_data.get('stalkers')
		self.STALKERS['health_points'] = threat.get('health_points')
		self.STALKERS['nourishment'] = threat.get('nourishment')
		self.STALKERS['sight'] = threat.get('sight')
		self.STALKERS['lifespan'] = threat.get('lifespan')
		self.STALKERS['smell'] = threat.get('smell')
		
