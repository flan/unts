# -*- coding: utf-8 -*-
"""
Unts module: agents; contains objects that manipulate the system.
"""
from shared import *
import breve
import inerts
import map
import shared

import math

class Agent(shared.Traceable, breve.Stationary):
	"""
	An abstract superclass for any agent that can affect the system in some way.
	"""
	_alive = True #: True while this agent is alive.
	_life = None #: The number of ticks left in this agent's life.
	_sight = None #: Non-pheromone entities can be detected within this radius.
	_smell = None #: Pheromone entities are considered this much closer for inverse-square calculations.
	_orientation = None #: The direction this agent is facing.
	_status = STATUS_WANDERING #: The current behaviour of this agent.
	_target = None #: The shared.Traceable that this agent is following, if status is STATUS_FOLLOWING.
	
	def __init__(self):
		"""
		Agent is meaningless by itself, so instantiating it will result in an
		exception.
		
		@raise Exception: Always.
		"""
		raise Exception("Unable to instantiate Agent.")
		
	def _init(self, config_data):
		"""
		Sets up Agent properties.
		
		@type config_data: dict
		@param config_data: The data used to initialize an agent.
		"""
		self._life = config_data.get('lifespan')
		self._sight = config_data.get('sight') or 1
		self._smell = config_data.get('smell') or 1
		self._orientation = RANDOMIZER.choice(range(0, 360, 45))
		
		if not type(self) is Builder:
			shared.AGENTS.append(self)
			
	def act(self, old_field, new_field):
		"""
		Causes this agent to act when its turn comes up. In this function, the
		agent makes decisions about what to do next.
		
		@type old_field: map.Field
		@param old_field: The state-field from which information about the
		    environment will be read.
		@type new_field: map.Field
		@param new_field: The state-field to which this agent's information will
		    be written.
		
		@return: Nothing.
		"""
		pass
		
	def agentsInLoS(self, field, types=None, colony=None, invert_colony=False):
		"""
		Builds a list of all agents that this agent can see.
		
		Note:: The newer, per-agent-checking algorithm loses some of the precision
		found in the baseline specification of this system:: agents will move in a
		random turn-order each iteration, so decisions made based on the position
		of other agents will be affected by the random turn-order; this may give
		some agents an advantage in cases where others have gone first, but this
		is effectively balanced out by the uniform distribution of randomness over
		turn order, and the increases in processing speed justify the sacrifice.
		If you wish to have full precision, modify the code found in
		objectsInLoS() to check for agents instead. (It's basically just changing
		'object' into 'agent')
		
		@type field: map.Field
		@param field: The state-field from which information about the environment
		    will be read.
		@type types: sequence
		@param types: A filter that will be applied to limit the agents returned.
		    All agents will be returned if not specified.
		@type colony: colony.Colony
		@param colony: A filter that will be applied to limit the agents
		    returned. All agents will be returned if not specified.
		@type invert_colony: bool
		@param invert_colony: True if all colonies other than the one specified
		    should be returned.
		    
		@rtype: list
		@return: A list of all agents that can be seen, in order of increasing
		    distance.
		"""
		agents = []
		if self._sight == 1: #It's probably always faster to perform the per-agent check in all other cases.
			for space in field.getSpacesInSight(self._position, self._sight):
				agents += space.getAgents(types, colony)
		else:
			for agent in shared.AGENTS:
				if not agent is self:
					if types and type(agent) not in types:
						continue
					if colony:
						if invert_colony and agent.getColony() is colony:
							continue
						elif not invert_colony and not agent.getColony() is colony:
							continue
							
					agent_position = agent.getPosition()
					distance = map.calcDistance(self._position, agent_position)
					if self._sight >= distance and field.clearPath(self._position, agent_position, False)[0]:
						agents.append((distance, agent))
			if agents:
				agents.sort()
				agents = [agent for (distance, agent) in agents]
		return agents
		
	def objectsInLoS(self, field, types=None, colony=None):
		"""
		Builds a list of all objects that this agent can see.
		
		@type field: map.Field
		@param field: The state-field from which information about the environment
		    will be read.
		@type types: sequence
		@param types: A filter that will be applied to limit the objects returned.
		    All objects will be returned if not specified.
		@type colony: colony.Colony
		@param colony: A filter that will be applied to limit the objects
		    returned. All objects will be returned if not specified.
		
		@rtype: list
		@return: A list of all objects that can be seen, in order of increasing
		    distance.
		"""
		objects = []
		for space in field.getSpacesInSight(self._position, self._sight):
			objects += space.getObjects(types, colony)
		return objects
		
	def pheromonesByStrength(self, field, types=None, colony=None):
		"""
		Builds a list of all pheromones that this agent can smell.
		
		@type field: map.Field
		@param field: The state-field from which information about the environment
		    will be read.
		@type types: sequence
		@param types: A filter that will be applied to limit the pheromones
		    returned. All pheromones will be returned if not specified.
		@type colony: colony.Colony
		@param colony: A filter that will be applied to limit the pheromones
		    returned. All pheromones will be returned if not specified.
		
		@rtype: list
		@return: A list of all pheromones that can be sensed, in order of
		    decreasing perceived intensity.
		"""
		pheromones = []
		
		for pheromone in field.getPheromones():
			if types and pheromone.getType() not in types:
				continue
			pheromone_colony = pheromone.getColony()
			if colony and pheromone_colony and not pheromone_colony is colony:
				continue
				
			pheromone_position = pheromone.getPosition()
			distance = map.calcDistance(self._position, pheromone_position)
			intensity = map.calcInverseSquare(distance, self._smell, pheromone.getIntensity())
			if intensity > 1 and field.clearPath(self._position, pheromone_position, True)[0]:
				pheromones.append((intensity, pheromone))
		if pheromones:
			pheromones.sort()
			pheromones = [pheromone for (intensity, pheromone) in pheromones]
			pheromones.reverse()
			
		return pheromones
		
	def canSense(self, target, field):
		"""
		Indicates whether the specified target can be sensed by this agent.
		
		@type target: shared.Traceable
		@param target: The target being evaluated.
		@type field: map.Field
		@param field: The state-field from which information about the environment
		    will be read.
		
		@rtype: bool
		@return: True if the target can be sensed.
		"""
		if type(target) is inerts.Hill:
			return True
			
		if isinstance(target, Agent) and not target.isVisible():
			return False
			
		pheromone = type(target) is inerts.Pheromone
		position = target.getPosition()
		if pheromone:
			if not target.exists():
				space = field.getSpace(position)
				if not space.getPheromones((target.getType(),), target.getColony()):
					return False
			else:
				if map.calcInverseSquare(map.calcDistance(self._position, position), self._smell, target.getIntensity()) < 1:
					return False
		else:
			if map.calcDistance(self._position, position) > self._sight:
				return False
		return field.clearPath(self._position, position, pheromone)[0]
		
	def die(self):
		"""
		Kills this agent if it is not already dead.
		
		@return: Nothing.
		"""
		self._alive = False
		if not type(self) is Builder:
			shared.AGENTS.remove(self)
			
	def getOrientation(self):
		"""
		Returns the angle this agent is facing.
		"""
		return self._orientation
		
	def isAlive(self):
		"""
		Indicates whether this agent is alive or not.
		
		@rtype: bool
		@return: True if this agent is alive.
		"""
		return self._alive
		
	def isThreat(self, agent):
		"""
		Indicates whether the specified agent constitues a threat to the current
		agent.
		
		@type agent: Agent
		@param agent: The agent to be evaluated.
		
		@rtype: bool
		@return: True if the other agent is something to be feared.
		"""
		return type(agent) == Warrior and not self.getColony() is agent.getColony()
		
	def isVisible(self):
		return self._alive
		
	def setOrientation(self, orientation):
		"""
		Causes this agent to face the newly specified direction.
		"""
		self._orientation = orientation % 360
		
	def tick(self):
		"""
		Causes this agnet's remaining lifespan to tick down.
		
		@rtype: bool
		@return: False if this tick ended the agent's life.
		"""
		self._life -= 1
		if not self._life:
			self.handleNaturalDeath()
			return False
		return True
		
	def _advance(self, field):
		"""
		Causes this agent to try to take a step forward. If the path is blocked,
		then a wall was enountered.
		
		@type field: map.Field
		@param field: The state-field from which information about the
		    environment will be read.
		
		@rtype: bool
		@return: True if the agent successfully advanced.
		"""
		target_space = field.getSpace(map.nextPositionByAngle(self._position, self._orientation))
		if not target_space or target_space.getObjects((inerts.Wall,)):
			#The edge of the map would be passed; treat this as a wall.
			return False
			
		self._position = (x, y) = target_space.getPosition()
		self.move(breve.vector(x, y, 0))
		return True #Movement succeeded.
		
	def _angleOffset(self, goal):
		"""
		Determines this angle that this agnet would have to turn to face the
		specified position.
		
		@type goal: tuple
		@param goal: The (x, y) co-ordinates being evaluated.
		
		@rtype: number
		@return: The angle that this agent would need to turn to face the goal.
		"""
		angle = (map.findAngle(self._position, goal) - self._orientation) % 360
		if angle >= 180:
			return 360 - angle
		return angle
		
	def _follow(self, target):
		"""
		Causes this agent to follow the specified target.
		
		@type target: shared. Traceable
		@param target: The target to be followed.
		
		@return: Nothing.
		"""
		self._status = STATUS_FOLLOWING
		self._target = target
		self.setOrientation(map.findAngle(self._position, target.getPosition()))
		
	def _move(self, old_field, new_field):
		"""
		Causes this agent to orient itself towards its goal (or update its target,
		if the system's rules require it to do so), and then choose its new location.
		
		@type old_field: map.Field
		@param old_field: The state-field from which information about the
		    environment will be read.
		@type new_field: map.Field
		@param new_field: The state-field to which this agent's information will
		    be written.
		
		@return: Nothing.
		"""
		if self._status == STATUS_FOLLOWING:
			if type(self._target) is inerts.Pheromone:
				self._moveFollowPheromone(old_field, new_field)
			else:
				self._moveFollow(new_field)
		elif self._status == STATUS_WANDERING:
			self._moveWander(new_field)
		elif isinstance(self, FieldUnt) and self.isReturning():
			self._moveReturn(old_field, new_field)
		else:
			self._advance(new_field)
			
	def _moveFollow(self, field):
		"""
		Causes this agent to orient itself towards its target and advance.
		
		@type field: map.Field
		@param field: The state-field from which information about the
		    environment will be read.
		
		@return: Nothing.
		"""
		if self.canSense(self._target, field):
			self.setOrientation(map.findAngle(self.getPosition(), self._target.getPosition()))
			
		if not self._advance(field): #The next space is inaccessible.
			self.setOrientation(self.getOrientation() + RANDOMIZER.choice((-90, -45, 45, 90)))
			self._advance(field) #Try again before waiting until the next cycle.
			
	def _moveFollowPheromone(self, old_field, new_field):
		"""
		Causes this agent to orient itself towards the pheromone it was following,
		a successor pheromone in the same place, or the next-best pheromone in
		range, depending on the state of the field.
		
		@type old_field: map.Field
		@param old_field: The state-field from which information about the
		    environment will be read.
		@type new_field: map.Field
		@param new_field: The state-field to which this agent's information will
		    be written.
		
		@return: Nothing.
		"""
		if self._position == self._target.getPosition(): #Destination reached.
			if self._status == STATUS_TRACING:
				self._status = STATUS_RETURNING
			else:
				self._status = STATUS_WANDERING
		else: #Adjust orientation and advance.
			self.setOrientation(map.findAngle(self.getPosition(), self._target.getPosition()))
			if not self._advance(new_field): #The next space is inaccessible.
				#Look for the next-best signal in LoS.
				signals = self.pheromonesByStrength(old_field, (self._target.getType(),), self._target.getColony())
				if signals:
					self._follow(signals[0])
					self._advance(new_field) #Try again before waiting until the next cycle.
					
	def _moveReturn(self, old_field, new_field):
		"""
		Causes this agent to orient itself towards the nearest hill and advance,
		applying wall-based pathfinding logic when necessary.
		
		Note:: Yes, I know only FieldUnts need this function. It was just easier
		this way.
		
		@type old_field: map.Field
		@param old_field: The state-field from which information about the
		    environment will be read.
		@type new_field: map.Field
		@param new_field: The state-field to which this agent's information will
		    be written.
		
		@return: Nothing.
		"""
		if self._status == STATUS_DETOURING:
			nearest_hill = self.locateNearestHill()
			if new_field.clearPath(self.getPosition(), nearest_hill.getPosition()):
				self.setOrientation(map.findAngle(self.getPosition(), nearest_hill.getPosition()))
			else: #Look for signals that suggest nearby paths.
				signals = [pheromone for pheromone in self.pheromonesByStrength((RESOURCE_FOOD, RESOURCE_WATER), self.getColony()) if -90 < self._angleOffset(pheromone.getPosition()) < 90]
				if signals:
					self._follow(signals[0])
		elif self._status == STATUS_BACKTRACKING:
			spaces = [space for space in new_field.getSpace(self._position).getMoore() if space.isOpen() and angleOffest(self, space.getPosition()) not in (0, 180)]
			if spaces: #It's possible to change course, so do it.
				self.setOrientation(map.findAngle(self._position, RANDOMIZER.choice(spaces).getPosition()))
				self._status = STATUS_DETOURING
				
		if not self._advance(new_field):
			self._moveReturnWall(new_field)
			
	def _moveReturnWall(self, field):
		"""
		Applies wall-based pathfinding logic to this agent's trek back to the
		nearest hill.
		
		Note:: Yes, I know only FieldUnts need this function. It was just easier
		this way.
		
		@type field: map.Field
		@param field: The state-field from which information about the
		    environment will be read.
		
		@return: Nothing.
		"""
		open_spaces = [space for space in field.getSpace(self._position) if space.isOpen()]
		fork_paths = [space for space in open_spaces if -90 < self._angleOffset(space.getPosition()) < 90]
		if not fork_paths: #Try any path that doesn't involve going backwards. 
			fork_paths = [space for space in open_spaces if not self._angleOffset(space.getPosition()) == 180]
		if fork_paths:
			self.setOrientation(map.findAngle(self._position, RANDOMIZER.choice(fork_paths).getPosition()))
			self._status = STATUS_DETOURING
		else: #This is a dead end.
			self.setOrientation(self._orientation + 180)
			self._status = STATUS_BACKTRACKING
			
	def _moveWall(self, field, paths):
		"""
		Applies wall-based pathfinding logic to this agent's movement.
		
		@type field: map.Field
		@param field: The state-field from which information about the
		    environment will be read.
		@type paths: list
		@param paths: A collection of spaces to which the agent can move.
		
		@return: Nothing.
		"""
		if paths:
			self.setOrientation(map.findAngle(self._position, RANDOMIZER.choice(paths).getPosition()))
		else:
			self.setOrientation(self._orientation + 180)
			
	def _moveWander(self, field):
		"""
		Causes this agent to proceed with a wandering streategy, handling
		wall-based pathfinding is necessary.
		
		@type field: map.Field
		@param field: The state-field from which information about the
		    environment will be read.
		
		@return: Nothing.
		"""
		if RANDOMIZER.random() < ENVIRONMENT.WANDER_VARIANCE:
			self.setOrientation(self._orientation + RANDOMIZER.choice((-45, 45)))
			
		if not self._advance(field): #Handle with wall-collision logic.
			paths = [space for space in field.getSpace(self.getPosition()).getMoore() if space.isOpen()]
			self._moveWall(field, paths)
			
			
class Threat(Agent):
	"""
	Threats exist solely to make life miserable for unts. They eat them and reproduce.
	"""
	_health_points = None #: The amount of damage this threat can take before it dies.
	_unts_consumed = 0 #: The number of unts this threat has managed to consume.
	_nourishment = None #: The number of unts that must be consumed per additional child spawned.
	_cooldown = None #: The number of ticks this threat must wait before it can move again.
	
	def __init__(self):
		"""
		Threat is meaningless by itself, so instantiating it will result in an
		exception.
		
		@raise Exception: Always.
		"""
		raise Exception("Unable to instantiate Threat.")
		
	def _init(self, config_data, position):
		"""
		Sets up Threat properties.
		
		@type config_data: dict
		@param config_data: A collection of variables needed to initialise this
		    threat.
		@type position: tuple
		@param position: The (x, y) co-ordinates of this threat.
		"""
		Agent._init(self, config_data)
		shared.Traceable._init(self, position)
		
		self._health_points = config_data.get('health_points')
		self._nourishment = config_data.get('nourishment')
		self._position = (x, y) = position
		
		breve.Stationary.__init__(self)
		self.move(breve.vector(x, y, 0))
		self.setShape(breve.createInstances(breve.Sphere, 1).initWith(0.75))
		(c_r, c_g, c_b) = config_data['colour']
		self.setColor(breve.vector(c_r, c_g, c_b))
		
	def act(self, old_field, new_field):
		if self._status == STATUS_KILLING:
			self._cooldown -= 1
			if not self._cooldown:
				self._status = STATUS_RETREATING
			else: #Hold position.
				return
				
		if RANDOMIZER.random() < ENVIRONMENT.DECISION_FREQUENCY:
			if self._status == STATUS_WANDERING:
				prey = self.agentsInLoS(old_field, (Architect, Warrior, Worker))
				if len(prey) == 1 or (len(prey) > 1 and not [agent for agent in prey if type(agent) is Warrior]):
					self._follow(prey[0])
			elif self._status == STATUS_FOLLOWING:
				if not old_field.exists(self._target):
					self._status = STATUS_WANDERING
				else:
					threats = self.agentsInLoS(old_field, (Warrior,))
					if self._health_points == 1 or len(threats) > 1 or (len(threats) == 1 and not self._target in threats):
						self._status = STATUS_WANDERING
			elif self._status == STATUS_RETREATING:
				if not self.pheromonesByStrength(old_field, (SIGNAL_THREAT,)):
					self._status = STATUS_WANDERING
				else:
					threats = self.agentsInLoS(old_field, (Warrior,))
					if threats:
						self.setOrientation(map.findAngle(self.getPosition(), threats[0].getPosition()) + 180)
						
		self._move(old_field, new_field)
		
		if self._status == STATUS_FOLLOWING:
			if not type(self._target) is inerts.Pheromone:
				if map.calcDistance(self._position, self._target.getPosition()) <= 2:
					self._attack(self._target, new_field)
		elif self._status == STATUS_WANDERING:
			self._speciesAction(old_field, new_field)
			
	def defend(self):
		"""
		If this threat is alive, it will take damage and it will be evaluated for
		death.
		
		@rtype: bool
		@return: True if this threat survived.
		"""
		if not self._alive:
			return False
			
		self._health_points -= 1
		if not self._health_points:
			self.die()
			return False
		self._unts_consumed += 1
		return True
		
	def die(self):
		"""
		Causes this threat to die.
		
		@return: Nothing.
		"""
		if self._alive:
			Agent.die(self)
			THREATS.remove(self)
			self.erase()
			
	def erase(self):
		"""
		Removes this threat from the system.
		
		Note:: breve doesn't actually have a facility for removing objects, so
		this function can only hope that breve has a garbage collector.
		
		@return: Nothing.
		"""
		self.makeInvisible()
		
	def handleNaturalDeath(self):
		"""
		Causes this threat to reproduce and die.
		
		@return: Nothing.
		"""
		for i in range(self._countChildren()):
			THREATS.append(self.__class__(self.getPosition()))
		self.die()
		
	def _attack(self, target, field):
		"""
		Causes this threat to attack the target, causing the target's death. This
		threat may die as a side-effect of attacking, if it's low on health and
		attacks a warrior.
		
		@type target: agents.Unt
		@param target: The target being attacked.
		@type field: map.Field
		@param field: The state-field to which information about the
		    environment will be written.
			
		@return: Nothing.
		"""
		if type(target) is Warrior:
			self._cooldown = ENVIRONMENT.KILL_TIME_WARRIOR
			self.defend()
		else:
			if type(target) is Architect:
				self._cooldown = ENVIRONMENT.KILL_TIME_ARCHITECT
			elif type(target) is Worker:
				self._cooldown = ENVIRONMENT.KILL_TIME_WORKER
			self._unts_consumed += 1
		self._status = STATUS_KILLING
		target.die(field)
		
	def _countChildren(self):
		"""
		Returns the number of children that this threat can spawn.
		
		@rtype: int
		@return: The number of children that this threat can spawn.
		"""
		return (self._unts_consumed / self._nourishment) + 1
		
	def _speciesAction(self, old_field, new_field):
		"""
		Causes this threat to perform its species-specific action.
		
		@type old_field: map.Field
		@param old_field: The state-field from which information about the
		    environment will be read.
		@type new_field: map.Field
		@param new_field: The state-field to which this agent's information will
		    be written.
		
		@return: Nothing.
		"""
		pass
		
		
class Predator(Threat):
	"""
	A predator is a threat that just wanders and kills.
	"""
	def __init__(self, position):
		"""
		Creates a new Predator.
		
		@type position: tuple
		@param position: The (x, y) co-ordinates of this threat.
		"""
		config_data = ENVIRONMENT.PREDATORS
		Threat._init(self, config_data, position)
		
		
class Hunter(Threat):
	"""
	A hunter is a threat that deposits pheromones to lure workers towards its
	location.
	"""
	def __init__(self, position):
		"""
		Creates a new Hunter.
		
		@type position: tuple
		@param position: The (x, y) co-ordinates of this threat.
		"""
		config_data = ENVIRONMENT.HUNTERS
		Threat._init(self, config_data, position)
		
	def _speciesAction(self, old_field, new_field):
		new_field.getSpace(self._position).addPheromone(RANDOMIZER.choice((RESOURCE_FOOD, RESOURCE_WATER)), None, ENVIRONMENT.HUNTERS['pheromones'])
		
		
class Stalker(Threat): #STALKER!
	"""
	A stalker is a threat that follows pheromones to find workers.
	"""
	def __init__(self, position):
		"""
		Creates a new Stalker.
		
		@type position: tuple
		@param position: The (x, y) co-ordinates of this threat.
		"""
		config_data = ENVIRONMENT.STALKERS
		Threat._init(self, config_data, position)
		
	def _speciesAction(self, old_field, new_field):
		leads = self.pheromonesByStrength(old_field, (RESOURCE_FOOD, RESOURCE_WATER))
		if leads:
			self._follow(leads[0])
			
			
class Unt(Agent):
	"""
	Unts are the stars of this system, modeled after ants, but with a number of
	liberaties taken for the sake of getting something working.
	"""
	_energy = None #: The number of ticks this unt can last in the field before dying.
	_max_energy = None #: The maximum number of this that this unt can survive in the field.
	_consumption_food = None #: The maximum amount of food that this unt can consume.
	_consumption_water = None #: The maximum amount of water that this unt can consume.
	_hill = None #: The hill to which this unt is attached.
	
	def __init__(self):
		"""
		Unt is meaningless by itself, so instantiating it will result in an
		exception.
		
		@raise Exception: Always.
		"""
		raise Exception("Unable to instantiate Unt.")
		
	def _init(self, config_data, hill):
		"""
		Sets up Unt properties.
		
		@type config_data: dict
		@param config_data: A collection of variables needed to initialise this
		    unt.
		@type hill: inerts.Hill
		@param hill: The hill to which this unt is attached.
		"""
		config_data['lifespan'] = ENVIRONMENT.REPRODUCTION + hill.getColony().LIFESPAN
		Agent._init(self, config_data)
		shared.Traceable._init(self, hill.getPosition())
		
		self._energy = self._max_energy = config_data.get('energy')
		self._consumption_food = config_data.get('consumption_food')
		self._consumption_water = config_data.get('consumption_water')
		self._setHill(hill)
		
	def act(self, old_field, new_field):
		if self.exist():
			self._act(old_field, new_field)
			
	def die(self, field=None):
		"""
		Causes this unt to die.
		
		@type field: inerts.Field
		@param field: The field to which attack pheromones will be written.
		    Additionally, the presence of this value indicates that the death was
		    not peaceful.
		
		@return: Nothing.
		"""
		if self._alive:
			Agent.die(self)
			killed = not field is None
			if field:
				colony = self.getColony()
				field.getSpace(self._position).addPheromone(SIGNAL_THREAT, colony, colony.PHEROMONES_ATTACK)
			self._hill.removeUnt(self, killed)
			self.erase()
			
	def erase(self):
		"""
		Removes this unt from the system.
		
		Note:: breve doesn't actually have a facility for removing objects, so
		this function can only hope that breve has a garbage collector.
		
		@return: Nothing.
		"""
		pass
		
	def exist(self):
		"""
		Indicates whether this unt exists.
		
		@rtype: bool
		@return: True if this unt exists.
		"""
		if not self._alive:
			return False
			
		if self._energy <= 0: #Starved to death.
			self.die()
			return False
		else:
			self._energy -= 1
			return True
			
	def getColony(self):
		return self._hill.getColony()
		
	def getConsumptionFood(self):
		"""
		Returns this unt's food-consumption capacity.
		
		@rtype: number
		@return: The amount of food this unt can eat.
		"""
		return self._consumption_food
		
	def getConsumptionWater(self):
		"""
		Returns this unt's water-consumption capacity.
		
		@rtype: number
		@return: The amount of water this unt can drink.
		"""
		return self._consumption_water
		
	def getHill(self):
		"""
		Returns the hill to which this unt is attached.
		"""
		return self._hill
		
	def handleNaturalDeath(self):
		"""
		Causes this unt to die peacefully.
		
		@return: Nothing.
		"""
		self.die()
		
	def isThreat(self, agent):
		return isinstance(agent, Threat) or Agent.isThreat(self, agent)
		
	def locateNearestHill(self, field):
		"""
		Finds the closest hill that belongs to this unt's colony.
		
		@type field: map.Field
		@param field: The state-field from which information about the
		    environment will be read.
		
		@rtype: inerts.Hill
		@return: The closest hill.
		"""
		space = field.getSpace(self._position)
		hills = [(space.calcDistance(hill.getPosition()), hill) for hill in self.getColony().getHills()]
		hills.sort()
		return hills[0][1]
		
	def objectsInLoS(self, field, types=None, colony=None):
		if colony is self.getColony() and types == (inerts.Hill,):
			objects = []
			for hill in self.getColony().getHills():
				distance = map.calcDistance(self._position, hill.getPosition())
				if self._sight >= distance:
					objects.append((distance, hill))
			if objects:
				objects.sort()
				objects = [obj for (distance, obj) in objects]
			return objects
		else:
			return Agent.objectsInLoS(self, field, types, colony)
			
	def _act(self, old_field, new_field):
		"""
		Causes this agent to make decisions about what to do next.
		
		@type old_field: map.Field
		@param old_field: The state-field from which information about the
		    environment will be read.
		@type new_field: map.Field
		@param new_field: The state-field to which this agent's information will
		    be written.
		
		@return: Nothing.
		"""
		pass
		
	def _recoverEnergy(self):
		"""
		Causes this unt to consume as many resources as it needs to be able to
		recover its strength.
		
		@return: Nothing.
		"""
		colony = self.getColony()
		energy_factor = 1 - (float(self._energy) / self._max_energy)
		restored_halves = 0
		
		if colony.removeFood(self._consumption_food * energy_factor):
			restored_halves += 1
		if colony.removeWater(self._consumption_water * energy_factor):
			restored_halves += 1
			
		self._energy += int(math.ceil((energy_factor / 2) * restored_halves * self._max_energy))
		
	def _setHill(self, hill):
		"""
		Attaches this unt to the specified hill, if it is not already so attached.
		
		@type hill: inerts.Hill
		@param hill: The hill to which this unt is being attached.
		
		@return: Nothing.
		"""
		if not self._hill is hill:
			if self._hill:
				self._hill.removeUnt(self)
			self._hill = hill
			hill.addUnt(self)
			
			
class Builder(Unt):
	"""
	Builders are essentially reservists that only get used when an architect
	creates a new hill. They can be seen as a sign of a hill's maturity because
	an architect won't spawn unless there are enough builders relative to workers
	and warriors, suggesting that the environment is stable.
	"""
	def __init__(self, hill):
		"""
		Creates a new Builder.
		
		@type hill: inerts.Hill
		@param hill: The hill to which this unt is attached.
		"""
		config_data = hill.getColony().BUILDERS
		Unt._init(self, config_data, hill)
		
	def _act(self, old_field, new_field):
		if self._energy <= 0:
			self._recoverEnergy()
			
	def isVisible(self):
		return False
		
		
class BreveUnt(Unt):
	"""
	A BreveUnt is an unt that has some presence within breve.
	"""
	def __init__(self):
		"""
		BreveUnt is meaningless by itself, so instantiating it will result in an
		exception.
		
		@raise Exception: Always.
		"""
		raise Exception("Unable to instantiate BreveUnt.")
		
	def _init(self, config_data):
		"""
		Sets up BreveUnt properties.
		
		@type config_data: dict
		@param config_data: A collection of variables needed to initialise this
		    unt.
		"""
		breve.Stationary.__init__(self)
		(x, y) = self._position
		self.move(breve.vector(x, y, 0))
		self.setShape(breve.createInstances(breve.Sphere, 1).initWith(config_data.get('size')))
		(c_r, c_g, c_b) = config_data.get('colour')
		self.setColor(breve.vector(c_r, c_g, c_b))
		
		self.hide()
		
	def erase(self):
		self.hide()
		
	def hide(self):
		"""
		Causes breve to stop rendering this unt.
		
		@return: Nothing.
		"""
		self.setTransparency(0)
		self.makeInvisible()
		
	def show(self):
		"""
		Causes breve to render this unt.
		
		@return: Nothing.
		"""
		self.setTransparency(1)
		self.makeVisible()
		
		
class Architect(BreveUnt):
	"""
	Architects are pacemakers that build hills to expand a colony's influence.
	"""
	_role = None #: The role the architect is performing, indicating which resource it seeks.
	
	def __init__(self, hill):
		"""
		Creates a new Architect.
		
		@type hill: inerts.Hill
		@param hill: The hill to which this unt is attached.
		"""
		config_data = hill.getColony().ARCHITECTS
		config_data['consumption_food'] = 0
		config_data['consumption_water'] = 0
		Unt._init(self, config_data, hill)
		
		colony = self.getColony()
		risk_food = colony.getRiskFood()
		risk_water = colony.getRiskWater()
		if risk_food > risk_water:
			self._role = RESOURCE_FOOD
		elif risk_water > risk_food:
			self._role = RESOURCE_WATER
			
		BreveUnt._init(self, config_data)
		self.show()
		
	def _act(self, old_field, new_field):
		self._move(old_field, new_field)
		
		if not [hill for hill in self.getColony().getHills() if map.calcDistance(self.getPosition(), hill.getPosition()) < ENVIRONMENT.MIN_BUILD_DISTANCE]:
			if self._role == RESOURCE_FOOD:
				self._scoutHill(old_field, new_field, (inerts.Food,))
			elif self._role == RESOURCE_WATER:
				self._scoutHill(old_field, new_field, (inerts.Water,))
			else:
				self._scoutHill(old_field, new_field, (inerts.Food, inerts.Water))
				
	def _buildHill(self, field):
		"""
		Causes this architect to create a new hill.
		
		@type field: map.Field
		@param field: The state-field to which information about the
		    environment will be written.
		
		@return: Nothing.
		"""
		colony = self.getColony()
		hill = inerts.Hill(colony, self._position)
		field.addObject(hill)
		
		unts_available = self._hill.summonBuilders()
		workers = int(unts_available * colony.getWorkerToWarriorRatio())
		warriors = unts_available - workers
		hill.generateUnts(workers, warriors, 0)
		
	def _scoutHill(self, old_field, new_field, types):
		"""
		Causes this architect to determine whether it has found a good site to
		build a hill. If so, the architect builds one and dies.
		
		@type old_field: map.Field
		@param old_field: The state-field from which information about the
		    environment will be read.
		@type new_field: map.Field
		@param new_field: The state-field to which information about the
		    environment will be written.
		@type types: sequence
		@param types: A list of resource types that this architect is looking for.
		
		@return: Nothing.
		"""
		if self.objectsInLoS(old_field, types):
			self._buildHill(new_field)
			self.die()
			
			
class FieldUnt(BreveUnt):
	"""
	A FieldUnt is an unt that performs tasks on the field repeatedly.
	"""
	_returning = False #: True if this unt is returning to a hill.
	_resting = True #: True if this unt is waiting to be dispatched.
	
	def __init__(self):
		"""
		FieldUnt is meaningless by itself, so instantiating it will result in an
		exception.
		
		@raise Exception: Always.
		"""
		raise Exception("Unable to instantiate FieldUnt.")
		
	def act(self, old_field, new_field):
		if self._resting:
			self.dispatch()
			new_field.getSpace(self._position).addAgent(self)
		else:
			if not self._returning and float(self._energy - 1) / self._max_energy <= 0.5: #Need to recover.
				self._follow(self.locateNearestHill(new_field))
				self._returning = True
			Unt.act(self, old_field, new_field)
			
	def arrive(self, hill):
		"""
		Called when this unt arrives at a hill.
		
		@type hill: inerts.Hill
		@param hill: The hill at which this unt arrived.
		
		@return: Nothing.
		"""
		self._setHill(hill)
		self._resting = True
		self._returning = False
		self.hide()
		
	def dispatch(self):
		"""
		Called when this unt leaves a hill.
		
		@return: Nothing.
		"""
		self._status = STATUS_WANDERING
		self._orientation = RANDOMIZER.randint(0, 359)
		self._resting = False
		self._recoverEnergy()
		self.show()
		
	def isResting(self):
		"""
		Indicates whether this unt is resting in a hill.
		
		@rtype: bool
		@return: True if this unt is resting in a hill.
		"""
		return self._resting
		
	def isReturning(self):
		"""
		Indicates whether this unt is returning to a hill.
		
		@rtype: bool
		@return: True if this unt is returning to a hill.
		"""
		return self._returning
		
	def isVisible(self):
		return not self._resting and Agent.isVisible(self)
		
	def _move(self, old_field, new_field):
		if self._returning and type(self._target) is inerts.Hill and self._position == self._target.getPosition():
			self.arrive(self._target)
		else:
			Agent._move(self, old_field, new_field)
			
			
class Warrior(FieldUnt):
	"""
	Warriors exist solely to protect workers.
	"""
	_escort = None #: True if this unt is serving as an escort, which keeps it near worker trails.
	
	def __init__(self, hill):
		"""
		Creates a new Warrior.
		
		@type hill: inerts.Hill
		@param hill: The hill to which this unt is attached.
		"""
		config_data = hill.getColony().WARRIORS
		Unt._init(self, config_data, hill)
		
		self._escort = RANDOMIZER.random() < config_data.get('escort')
		
		BreveUnt._init(self, config_data)
		
	def _act(self, old_field, new_field):
		if RANDOMIZER.random() < ENVIRONMENT.DECISION_FREQUENCY:
			if self._status == STATUS_FOLLOWING and not old_field.exists(self._target):
				self._status = STATUS_WANDERING
				
			if self._status == STATUS_WANDERING or (self._status == STATUS_FOLLOWING and not type(self._target) is inerts.Hill):
				self._determineNewStatus(old_field)
				
		self._move(old_field, new_field)
		
		if self._status == STATUS_FOLLOWING and isinstance(self._target, Agent):
			if map.calcDistance(self._position, self._target.getPosition()) <= 1:
				if not self._attack(self._target, new_field):
					self.die()
				elif not type(self._target) in (Worker, Architect):
					self._follow(self.locateNearestHill(new_field))
					self._returning = True
					
	def _attack(self, target, field):
		"""
		Causes this unt to attack the specified target. This unt may die if it
		attacks a threat that survives or if it attacks another warrior.
		
		@type target: Agent
		@param target: The target being attacked.
		@type field: inerts.Field
		@param field: The field to which information will be read.
		
		@rtype: bool
		@return: True if this unt survived.
		"""
		colony = self.getColony()
		field.getSpace(self._position).addPheromone(SIGNAL_THREAT, colony, colony.PHEROMONES_ATTACK)
		
		if isinstance(target, Threat):
			return not target.defend()
			
		target.die(field)
		return not type(target) is Warrior
		
	def _determineNewStatus(self, field):
		"""
		Causes this unt to reconsider its current status.
		
		@type field: inerts.Field
		@param field: The field to which information will be read.
		
		@return: Nothing.
		"""
		threats = [agent for agent in self.agentsInLoS(field, (Warrior, Predator, Hunter, Stalker)) if self.isThreat(agent)]
		if threats:
			self._follow(threats[0])
		else:
			threat_signals = self.pheromonesByStrength(field, (SIGNAL_THREAT,))
			if threat_signals:
				self._follow(threat_signals[0])
			else:
				foreigners = [agent for agent in self.agentsInLoS(field, (Worker, Architect), self.getColony(), True)]
				if foreigners: #See if there's a foreign worker nearby, and kill it if possible.
					self._follow(foreigners[0])
				else:
					if self._escort:
						signals = self.pheromonesByStrength(field, (RESOURCE_FOOD, RESOURCE_WATER))
						if signals:
							self._follow(signals[0])
							
							
class Worker(FieldUnt):
	"""
	Workers exists solely to gather resources for the colony.
	"""
	_boldness = None #: The boldness constant that dictates how this worker will result when oppressed.
	_carrying_capacity = None #: The maximum amount of resources that this worker can carry.
	_payload = None #: What this worker is carrying.
	_stochastic = None #: True if this worker will ignore pheromones.
	_role = None #: The resource constant that indicates what this worker hopes to find.
	_avoid = None #: A list of all entities that this worker should avoid.
	_pheromone_intensity = None #: The intensity of the pheromones that this worker will drop; makes use of exponential decay.
	
	def __init__(self, hill):
		"""
		Creates a new Worker.
		
		@type hill: inerts.Hill
		@param hill: The hill to which this unt is attached.
		"""
		config_data = hill.getColony().WORKERS
		Unt._init(self, config_data, hill)
		self._boldness = config_data.get('boldness')
		self._carrying_capacity = config_data.get('carrying_capacity')
		self._stochastic = RANDOMIZER.random() < config_data.get('stochastic_probaility')
		
		self._avoid = []
		
		BreveUnt._init(self, config_data)
		
	def arrive(self, hill):
		hill.addResource(self._payload)
		self._payload = None
		FieldUnt.arrive(self, hill)
		
	def dispatch(self):
		#Determine role.
		colony = self.getColony()
		risk_food = colony.getRiskFood()
		risk_water = colony.getRiskWater()
		
		if risk_food <= 0 and risk_water <= 0:
			if RANDOMIZER.random() < colony.WORKERS['no_focus']:
				self._role = None
			else:
				element_3 = None
				colony_food = colony.getFood()
				colony_water = colony.getWater()
				if colony_food < colony_water:
					element_3 = RESOURCE_FOOD
				elif colony_water < colony_food:
					element_3 = RESOURCE_WATER
				self._role = RANDOMIZER.choice((RESOURCE_FOOD, RESOURCE_WATER, element_3))
		elif risk_food > 0 and risk_water > 0:
			if RANDOMIZER.random() < float(risk_food) / (risk_food + risk_water):
				self._role = RESOURCE_FOOD
			else:
				self._role = RESOURCE_WATER
		elif risk_food > 0:
			if RANDOMIZER.random() < (risk_food / colony.getConsumptionFood()):
				self._role = RESOURCE_FOOD
			else:
				self._role = RANDOMIZER.choice((RESOURCE_WATER, None))
		elif risk_water > 0:
			if RANDOMIZER.random() < (risk_water / colony.getConsumptionWater()):
				self._role = RESOURCE_WATER
			else:
				self._role = RANDOMIZER.choice((RESOURCE_FOOD, None))
				
		FieldUnt.dispatch(self)
		
	def _act(self, old_field, new_field):
		if RANDOMIZER.random() < ENVIRONMENT.DECISION_FREQUENCY:
			dead_avoidances = []
			for avoid in self._avoid:
				if not self.canSense(avoid, old_field):
					dead_avoidances.append(avoid)
			for avoid in dead_avoidances:
				self._avoid.remove(avoid)
			dead_avoidances = None
			
			if self._status == STATUS_FOLLOWING and not old_field.exists(self._target):
				self._status = STATUS_WANDERING
				
			if self._status == STATUS_WANDERING or (self._status == STATUS_FOLLOWING and type(self._target) is inerts.Pheromone):
				self._determineNewStatus(old_field)
				
		harvested = None
		if self._returning:
			if self._payload:
				colony = self.getColony()
				intensity = int(colony.PHEROMONES * self._pheromone_intensity)
				if intensity:
					new_field.getSpace(self._position).addPheromone(self._payload[0], colony, intensity)
					self._pheromone_intensity *= self.getColony().PHEROMONES_GRADIENT
		elif not self._resting:
			if self._role == RESOURCE_FOOD:
				harvested = self._harvestResource(old_field, (inerts.Food,))
			elif self._role == RESOURCE_WATER:
				harvested = self._harvestResource(old_field, (inerts.Water,))
			else:
				harvested = self._harvestResource(old_field, (inerts.Food, inerts.Water))
				
		if not harvested:
			self._move(old_field, new_field)
			
	def _determineNewStatus(self, field):
		"""
		Causes this unt to reconsider its current status.
		
		@type field: inerts.Field
		@param field: The field from which information will be read.
		
		@return: Nothing.
		"""
		suicide_run = False
		threats = [agent for agent in self.agentsInLoS(field, (Warrior, Predator, Hunter, Stalker)) if self.isThreat(agent)]
		if threats:
			if self._boldness == BOLDNESS_AGGRESSIVE:
				self._follow(threats[0])
				self._avoid = []
				suicide_run = True
			elif self._boldness == BOLDNESS_PASSIVE:
				self._avoid.append(threats[0])
				
		if not suicide_run:
			threat_signals = self.pheromonesByStrength(field, (SIGNAL_THREAT,))
			if threat_signals:
				self._avoid.append(threat_signals[0])
				
			if not self._stochastic:
				if self._role == RESOURCE_FOOD:
					self._reactToPheromone(field, (RESOURCE_FOOD,))
				elif self._role == RESOURCE_WATER:
					self._reactToPheromone(field, (RESOURCE_WATER,))
				else:
					self._reactToPheromone(field, (RESOURCE_FOOD, RESOURCE_WATER))
					
	def _getStrongestResourceSignal(self, field, types):
		"""
		Looks for the strengest resource signal that this unt can sense and
		returns it.
		
		@type field: inerts.Field
		@param field: The field from which information will be read.
		@type types: sequence
		@param types: A list of pheromone types this unt will try to sense.
		
		@rtype: inerts.Pheromone
		@return: The strongest pheromone that could be sensed or None if there are
		    no sense-able pheromones.
		"""
		filtered_pheromones = []
		for pheromone in self.pheromonesByStrength(field, types, self.getColony()):
			angle = abs(map.findAngle(self._position, self.locateNearestHill(field).getPosition()) - map.findAngle(self._position, pheromone.getPosition()))
			if angle > 90 and angle < 270:
				filtered_pheromones.append(pheromone)
		if filtered_pheromones:
			return filtered_pheromones[0]
		return None
		
	def _harvestResource(self, field, types):
		"""
		Gathers material from an adjacent resource, if one exists.
		
		@type field: inerts.Field
		@param field: The field from which information will be read.
		@type types: sequence
		@param types: A list of resource types this unt will try to harvest from.
		
		@rtype: bool
		@return: True if resources were harvested.
		"""
		resources = self.objectsInLoS(field, types)
		if resources:
			resource = resources[0]
			position = resource.getPosition()
			if map.calcDistance(self.getPosition(), position) == 1:
				harvested = resource.harvest(self.getColony().WORKERS['carrying_capacity'])
				if harvested:
					self._payload = (resource.getType(), harvested)
					self._pheromone_intensity = 1.0
					self._returning = True
					self._avoid = []
					self._follow(self.locateNearestHill(field))
					return True
				else:
					self._avoid.append(resources[0])
					self._status = STATUS_WANDERING
			else:
				if not resources[0] in self._avoid:
					self._follow(resources[0])
		return False
		
	def _reactToPheromone(self, field, types):
		"""
		Causes this unt to sense pheromones and react accordingly.
		
		@type field: inerts.Field
		@param field: The field from which information will be read.
		@type types: sequence
		@param types: A list of pheromone types this unt will try to sense.
		
		@return: Nothing.
		"""
		signal = self._getStrongestResourceSignal(field, types)
		if signal:
			self._follow(signal)
			
	def _move(self, old_field, new_field):
		if self._returning or not self._avoid: #Behave normally.
			FieldUnt._move(self, old_field, new_field)
		else: #Scatter.
			paths = [space for space in new_field.getSpace(self._position).getMoore() if abs(map.findAngle(self._position, space.getPosition()) - map.findAngle(self._position, map.findClosestEntity(self._position, self._avoid)[0])) >= 90]
			if paths:
				self.setOrientation(map.findAngle(self._position, RANDOMIZER.choice(paths).getPosition()))
				self._advance(new_field)
			else: #Impossible to move away, so cower in fear.
				pass
				
	def _moveWall(self, field, paths):
		new_paths = [space for space in paths if abs(map.findAngle(self._position, space.getPosition()) - map.findAngle(self._position, self._hill.getPosition())) >= 90]
		Agent._moveWall(self, field, new_paths)
		
