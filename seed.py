# -*- coding: utf-8 -*-
"""
Unts module: seed; contains variables used to initialize the simulation.
"""
import shared

environment = {
 #Simulation
 'field_width': 100, #Controls the width of the field.
 'field_height': 100, #Controls the height of the field.
 'random_seed': 0, #Keep this constant to reproduce the same events in repeat runs.
 'decision_frequency': 1.0, #Used to cause agents to make decisions n% of the time; this can lead to dramatic speedups in exchange for stupider logic.
 
 #General
 'min_build_distance': 20, #No colony's hills may be built closer than this many spaces.
 
 #Pathfinding
 'wander_variance': 0.1, #The probability that an agent will deviate from its current heading with each step.
 
 #Reproduction
 'generation_minimum': 0.25, #A new brood must be at least this big, relative to the previous one, for reproduction to occur; used to prevent waste.
 'reproduction': 500, #The number of ticks between reproductive cycles.
 'reproduction_delay': 50, #If a new brood would be too small, wait for this many ticks before trying again; prompts "LIFE GOES ON!" behaviour.
 'resources_reserve': 0.01, #The higher this is, the fewer excess resources will be required for a new unt to be spawned beyond the colony's previous values.
 'restart_factor': 5, #The number of unts to spawn for each hill of a dead colony to bring it back to life.
 
 #Signals
 #Note: Increasing these values will result in better swarm logic, but more processing time will be required as they linger longer.
 'signals_dispersion_factor': 0.8, #How much of a pheromone persists after each cycle.
 'signals_collision_factor': 0.25, #How effectively like pheromones stack.
 
 #Threats
 'kill_time_architect': 3, #How long a threat will idle after killing an architect.
 'kill_time_warrior': 5, #How long a threat will idle after killing a warrior.
 'kill_time_worker': 4, #How long a threat will idle after killing a worker.
 
 'predators': {
  'health_points': 3, #The amount of damage that can be absorbed.
  'nourishment': 4, #The number of unts that need to be consumed for an additional child to be spawned.
  'sight': 5, #The range that can be seen. Higher values mean more intelligence, but also more processing time.
  'lifespan': 125, #The number of ticks that make up this threat's lifecycle; reproduction occurs only if this value is reached.
 },
 'hunters': {
  'health_points': 2, #The amount of damage that can be absorbed.
  'nourishment': 4, #The number of unts that need to be consumed for an additional child to be spawned.
  'pheromones': 50, #The intensity of pheromones dropped while wandering.
  'sight': 4, #The range that can be seen. Higher values mean more intelligence, but also more processing time.
  'lifespan': 100, #The number of ticks that make up this threat's lifecycle; reproduction occurs only if this value is reached.
 },
 'stalkers': {
  'health_points': 2, #The amount of damage that can be absorbed.
  'nourishment': 4, #The number of unts that need to be consumed for an additional child to be spawned.
  'sight': 2, #The range that can be seen. Higher values mean more intelligence, but also more processing time.
  'smell': 3, #The range of pheromones that can be sensed. Higher values mean more intelligence, but also more processing time.
  'lifespan': 125, #The number of ticks that make up this threat's lifecycle; reproduction occurs only if this value is reached.
 }
}

colonies = (
 (
  {
   'pheromones': 75, #The intensity of pheromones dropped to indicate the presence of resources.
   'pheromones_gradient': 0.75, #The rate of exponential decay that gets applied to the pheromones dropped as a worker returns from a resource.
   'pheromones_attack': 100, #The intensity of pheromones dropped to indicate the presence of danger.
   
   'lifespan': 100, #The number of ticks that unts in this colony will live beyond the reproduction tick-count.
   
   'importance_expansion': 0.5, #Higher values give spawning priority to hills that are more likely to produce an architect.
   'importance_growth': 0.25, #Higher values give spawning priority to hills that comprise large amounts of the colony's population.
   'importance_resources': 1.0, #Higher values give spawning priority to hills that yeild more resources.
   'importance_territory': 0.5, #Higher values give spawning priority to hills that are under attack, since gaining dominance will subdue rivals.
   
   'hill_colour': (0, 0, 1.0),
   
   'architects': {
	 'energy': 75, #The number of ticks an architect may survive without eating.
	 'spawning_builder_ratio': 0.10, #The ratio of builders to non-builders that a hill must have to spawn an architect.
	 'sight': 10, #The range that can be seen. Architects will build a hill as soon as they find an appropriate resource within this range (if there are no friendly hills nearby).
	 'colour': (0.8, 0.8, 1.0),
	},
	'builders': {
	 'energy': 60, #The number of ticks a builder may survive without eating.
	 'consumption_food': 1.5, #The amount of food that needs to be consumed to recover 50% of max energy.
	 'consumption_water': 1.5 #The amount of water that needs to be consumed to recover 50% of max energy.
	},
	'warriors': {
	 'consumption_food': 3, #The amount of food that needs to be consumed to recover 50% of max energy.
	 'consumption_water': 3, #The amount of water that needs to be consumed to recover 50% of max energy.
	 'decay': 0.55, #The decay ratio that gets applied to a hill's warrior complement in times of peace.
	 'growth': 1.8, #The growth ratio that gets applied to a hill's warrior complement in times of strife.
	 'energy': 75, #The number of ticks a warrior may survive without eating. Warriors head to a hill when this hits 50%.
	 'escort': 0.25, #The probability that this warrior will serve as an escort to workers.
	 'population_minimum': 0.1, #The minimum amount of a hill's population that must be comprised of warriors, resource-permitting.
	 'sight': 3, #The range that can be seen. Higher values mean more intelligence, but also more processing time.
	 'smell': 5, #The range of pheromones that can be sensed. Higher values mean more intelligence, but also more processing time.
	 'colour': (0.4, 0.4, 1.0),
	},
	'workers': {
	 'boldness': shared.BOLDNESS_PASSIVE, #This determines how a worker will behave when confronted with danger.
	 'carrying_capacity': 5, #The number of resources that may be carried back to a hill.
	 'no_focus': 0.25, #The probability that a worker will seek any type of resource, rather than focusing on food or water, assuming risk is low.
	 'consumption_food': 2, #The amount of food that needs to be consumed to recover 50% of max energy.
	 'consumption_water': 2, #The amount of water that needs to be consumed to recover 50% of max energy.
	 'energy': 60, #The number of ticks a worker may survive without eating. Workers head to a hill when this hits 50%.
	 'growth': 1.25, #The growth ratio that gets applied to a hill's worker complement when resources are abundant.
	 'sight': 3, #The range that can be seen. Higher values mean more intelligence, but also more processing time.
	 'smell': 8, #The range of pheromones that can be sensed. Higher values mean more intelligence, but also more processing time.
	 'stochastic_probability': 0.1, #The probability that a worker will ignore pheromones entirely, making it more likely to discover new resources.
	 'colour': (0.6, 0.6, 1.0),
	},
   'food': 25,
   'water': 25,
  },
  (#Hills: position, workers, warriors, builders
   ((5, 5), 20, 5, 0),
  )
 ),
 
 (
  {
   'pheromones': 75, #The intensity of pheromones dropped to indicate the presence of resources.
   'pheromones_gradient': 0.75, #The rate of exponential decay that gets applied to the pheromones dropped as a worker returns from a resource.
   'pheromones_attack': 100, #The intensity of pheromones dropped to indicate the presence of danger.
   
	'lifespan': 100, #The number of ticks that unts in this colony will live beyond the reproduction tick-count.
   
   'importance_expansion': 0.5, #Higher values give spawning priority to hills that are more likely to produce an architect.
   'importance_growth': 0.25, #Higher values give spawning priority to hills that comprise large amounts of the colony's population.
   'importance_resources': 1.0, #Higher values give spawning priority to hills that yeild more resources.
   'importance_territory': 0.5, #Higher values give spawning priority to hills that are under attack, since gaining dominance will subdue rivals.
   
   'hill_colour': (1.0, 0, 0),
   
   'architects': {
	 'energy': 75, #The number of ticks an architect may survive without eating.
	 'spawning_builder_ratio': 0.10, #The ratio of builders to non-builders that a hill must have to spawn an architect.
	 'sight': 10, #The range that can be seen. Architects will build a hill as soon as they find an appropriate resource within this range (if there are no friendly hills nearby).
	 'colour': (1.0, 0.8, 0.8),
	},
	'builders': {
	 'energy': 60, #The number of ticks a builder may survive without eating.
	 'consumption_food': 1.5, #The amount of food that needs to be consumed to recover 50% of max energy.
	 'consumption_water': 1.5 #The amount of water that needs to be consumed to recover 50% of max energy.
	},
	'warriors': {
	 'consumption_food': 3, #The amount of food that needs to be consumed to recover 50% of max energy.
	 'consumption_water': 3, #The amount of water that needs to be consumed to recover 50% of max energy.
	 'decay': 0.55, #The decay ratio that gets applied to a hill's warrior complement in times of peace.
	 'growth': 1.8, #The growth ratio that gets applied to a hill's warrior complement in times of strife.
	 'energy': 75, #The number of ticks a warrior may survive without eating. Warriors head to a hill when this hits 50%.
	 'escort': 0.25, #The probability that this warrior will serve as an escort to workers.
	 'population_minimum': 0.1, #The minimum amount of a hill's population that must be comprised of warriors, resource-permitting.
	 'sight': 3, #The range that can be seen. Higher values mean more intelligence, but also more processing time.
	 'smell': 5, #The range of pheromones that can be sensed. Higher values mean more intelligence, but also more processing time.
	 'colour': (1.0, 0.4, 0.4),
	},
	'workers': {
	 'boldness': shared.BOLDNESS_ASSERTIVE, #This determines how a worker will behave when confronted with danger.
	 'carrying_capacity': 5, #The number of resources that may be carried back to a hill.
	 'no_focus': 0.25, #The probability that a worker will seek any type of resource, rather than focusing on food or water, assuming risk is low.
	 'consumption_food': 2, #The amount of food that needs to be consumed to recover 50% of max energy.
	 'consumption_water': 2, #The amount of water that needs to be consumed to recover 50% of max energy.
	 'energy': 60, #The number of ticks a worker may survive without eating. Workers head to a hill when this hits 50%.
	 'growth': 1.25, #The growth ratio that gets applied to a hill's worker complement when resources are abundant.
	 'sight': 3, #The range that can be seen. Higher values mean more intelligence, but also more processing time.
	 'smell': 8, #The range of pheromones that can be sensed. Higher values mean more intelligence, but also more processing time.
	 'stochastic_probability': 0.1, #The probability that a worker will ignore pheromones entirely, making it more likely to discover new resources.
	 'colour': (1.0, 0.6, 0.6),
	},
   'food': 25,
   'water': 25,
  },
  (#Hills: position, workers, warriors, builders
   ((94, 5), 20, 5, 0),
  )
 ),
 
 (
  {
   'pheromones': 75, #The intensity of pheromones dropped to indicate the presence of resources.
   'pheromones_gradient': 0.75, #The rate of exponential decay that gets applied to the pheromones dropped as a worker returns from a resource.
   'pheromones_attack': 100, #The intensity of pheromones dropped to indicate the presence of danger.
   
	'lifespan': 100, #The number of ticks that unts in this colony will live beyond the reproduction tick-count.
   
   'importance_expansion': 0.5, #Higher values give spawning priority to hills that are more likely to produce an architect.
   'importance_growth': 0.25, #Higher values give spawning priority to hills that comprise large amounts of the colony's population.
   'importance_resources': 1.0, #Higher values give spawning priority to hills that yeild more resources.
   'importance_territory': 0.5, #Higher values give spawning priority to hills that are under attack, since gaining dominance will subdue rivals.
   
   'hill_colour': (0, 1.0, 0),
   
   'architects': {
	 'energy': 75, #The number of ticks an architect may survive without eating.
	 'spawning_builder_ratio': 0.10, #The ratio of builders to non-builders that a hill must have to spawn an architect.
	 'sight': 10, #The range that can be seen. Architects will build a hill as soon as they find an appropriate resource within this range (if there are no friendly hills nearby).
	 'colour': (0.8, 1.0, 0.8),
	},
	'builders': {
	 'energy': 60, #The number of ticks a builder may survive without eating.
	 'consumption_food': 1.5, #The amount of food that needs to be consumed to recover 50% of max energy.
	 'consumption_water': 1.5 #The amount of water that needs to be consumed to recover 50% of max energy.
	},
	'warriors': {
	 'consumption_food': 3, #The amount of food that needs to be consumed to recover 50% of max energy.
	 'consumption_water': 3, #The amount of water that needs to be consumed to recover 50% of max energy.
	 'decay': 0.55, #The decay ratio that gets applied to a hill's warrior complement in times of peace.
	 'growth': 1.8, #The growth ratio that gets applied to a hill's warrior complement in times of strife.
	 'energy': 75, #The number of ticks a warrior may survive without eating. Warriors head to a hill when this hits 50%.
	 'escort': 0.25, #The probability that this warrior will serve as an escort to workers.
	 'population_minimum': 0.1, #The minimum amount of a hill's population that must be comprised of warriors, resource-permitting.
	 'sight': 3, #The range that can be seen. Higher values mean more intelligence, but also more processing time.
	 'smell': 5, #The range of pheromones that can be sensed. Higher values mean more intelligence, but also more processing time.
	 'colour': (0.4, 1.0, 0.4),
	},
	'workers': {
	 'boldness': shared.BOLDNESS_ASSERTIVE, #This determines how a worker will behave when confronted with danger.
	 'carrying_capacity': 5, #The number of resources that may be carried back to a hill.
	 'no_focus': 0.25, #The probability that a worker will seek any type of resource, rather than focusing on food or water, assuming risk is low.
	 'consumption_food': 2, #The amount of food that needs to be consumed to recover 50% of max energy.
	 'consumption_water': 2, #The amount of water that needs to be consumed to recover 50% of max energy.
	 'energy': 60, #The number of ticks a worker may survive without eating. Workers head to a hill when this hits 50%.
	 'growth': 1.25, #The growth ratio that gets applied to a hill's worker complement when resources are abundant.
	 'sight': 3, #The range that can be seen. Higher values mean more intelligence, but also more processing time.
	 'smell': 8, #The range of pheromones that can be sensed. Higher values mean more intelligence, but also more processing time.
	 'stochastic_probability': 0.1, #The probability that a worker will ignore pheromones entirely, making it more likely to discover new resources.
	 'colour': (0.6, 1.0, 0.6),
	},
   'food': 25,
   'water': 25,
  },
  (#Hills: position, workers, warriors, builders
   ((5, 94), 20, 5, 0),
  )
 ),
 
 (
  {
   'pheromones': 75, #The intensity of pheromones dropped to indicate the presence of resources.
   'pheromones_gradient': 0.75, #The rate of exponential decay that gets applied to the pheromones dropped as a worker returns from a resource.
   'pheromones_attack': 100, #The intensity of pheromones dropped to indicate the presence of danger.
   
	'lifespan': 100, #The number of ticks that unts in this colony will live beyond the reproduction tick-count.
   
   'importance_expansion': 0.5, #Higher values give spawning priority to hills that are more likely to produce an architect.
   'importance_growth': 0.25, #Higher values give spawning priority to hills that comprise large amounts of the colony's population.
   'importance_resources': 1.0, #Higher values give spawning priority to hills that yeild more resources.
   'importance_territory': 0.5, #Higher values give spawning priority to hills that are under attack, since gaining dominance will subdue rivals.
   
   'hill_colour': (1.0, 1.0, 0),
   
   'architects': {
	 'energy': 75, #The number of ticks an architect may survive without eating.
	 'spawning_builder_ratio': 0.10, #The ratio of builders to non-builders that a hill must have to spawn an architect.
	 'sight': 10, #The range that can be seen. Architects will build a hill as soon as they find an appropriate resource within this range (if there are no friendly hills nearby).
	 'colour': (1.0, 1.0, 0.8),
	},
	'builders': {
	 'energy': 60, #The number of ticks a builder may survive without eating.
	 'consumption_food': 1.5, #The amount of food that needs to be consumed to recover 50% of max energy.
	 'consumption_water': 1.5 #The amount of water that needs to be consumed to recover 50% of max energy.
	},
	'warriors': {
	 'consumption_food': 3, #The amount of food that needs to be consumed to recover 50% of max energy.
	 'consumption_water': 3, #The amount of water that needs to be consumed to recover 50% of max energy.
	 'decay': 0.55, #The decay ratio that gets applied to a hill's warrior complement in times of peace.
	 'growth': 1.8, #The growth ratio that gets applied to a hill's warrior complement in times of strife.
	 'energy': 75, #The number of ticks a warrior may survive without eating. Warriors head to a hill when this hits 50%.
	 'escort': 0.25, #The probability that this warrior will serve as an escort to workers.
	 'population_minimum': 0.1, #The minimum amount of a hill's population that must be comprised of warriors, resource-permitting.
	 'sight': 3, #The range that can be seen. Higher values mean more intelligence, but also more processing time.
	 'smell': 5, #The range of pheromones that can be sensed. Higher values mean more intelligence, but also more processing time.
	 'colour': (1.0, 1.0, 0.4),
	},
	'workers': {
	 'boldness': shared.BOLDNESS_AGGRESSIVE, #This determines how a worker will behave when confronted with danger.
	 'carrying_capacity': 5, #The number of resources that may be carried back to a hill.
	 'no_focus': 0.25, #The probability that a worker will seek any type of resource, rather than focusing on food or water, assuming risk is low.
	 'consumption_food': 2, #The amount of food that needs to be consumed to recover 50% of max energy.
	 'consumption_water': 2, #The amount of water that needs to be consumed to recover 50% of max energy.
	 'energy': 60, #The number of ticks a worker may survive without eating. Workers head to a hill when this hits 50%.
	 'growth': 1.25, #The growth ratio that gets applied to a hill's worker complement when resources are abundant.
	 'sight': 3, #The range that can be seen. Higher values mean more intelligence, but also more processing time.
	 'smell': 6, #The range of pheromones that can be sensed. Higher values mean more intelligence, but also more processing time.
	 'stochastic_probability': 0.1, #The probability that a worker will ignore pheromones entirely, making it more likely to discover new resources.
	 'colour': (1.0, 1.0, 0.6),
	},
   'food': 25,
   'water': 25,
  },
  (#Hills: position, workers, warriors, builders
   ((94, 94), 20, 5, 0),
  )
 ),
)

threats = (
 (#Predators: position
  (50, 49),
 ),
 (#Hunters: position
  (50, 50),
 ),
 (#Stalkers: position
  (49, 50),
 )
)

resources = (
 (#Food: position, capacity, replenishment %, cooldown
  ((3, 11), 100, 0.1, 10), ((96, 11), 100, 0.1, 10),
  ((3, 88), 100, 0.1, 10), ((96, 88), 100, 0.1, 10),
  
  ((25, 30), 250, 0.25, 75), ((74, 30), 250, 0.25, 75),
  ((25, 69), 250, 0.25, 75), ((74, 69), 250, 0.25, 75),
  
  ((40, 10), 500, 0.08, 15), ((49, 10), 500, 0.08, 15),
  ((50, 89), 500, 0.08, 15), ((59, 89), 500, 0.08, 15),
  ((10, 50), 500, 0.08, 15), ((10, 59), 500, 0.08, 15),
  ((89, 40), 500, 0.08, 15), ((89, 49), 500, 0.08, 15),
  
  ((45, 54), 1000, 0.1, 50), ((54, 45), 1000, 0.1, 50),
  ((40, 40), 1000, 0.1, 50), ((59, 59), 1000, 0.1, 50),
 ),
 (#Water: position, capacity, replenishment %, cooldown
  ((11, 3), 100, 0.1, 10), ((11, 96), 100, 0.1, 10),
  ((88, 3), 100, 0.1, 10), ((88, 96), 100, 0.1, 10),
  
  ((30, 25), 250, 0.25, 75), ((30, 74), 250, 0.25, 75),
  ((69, 25), 250, 0.25, 75), ((69, 74), 250, 0.25, 75),
  
  ((40, 5), 500, 0.08, 15), ((49, 5), 500, 0.08, 15),
  ((50, 94), 500, 0.08, 15), ((59, 94), 500, 0.08, 15),
  ((5, 50), 500, 0.08, 15), ((5, 59), 500, 0.08, 15),
  ((94, 40), 500, 0.08, 15), ((94, 49), 500, 0.08, 15),
  
  ((45, 45), 1000, 0.1, 50), ((54, 54), 1000, 0.1, 50),
  ((40, 59), 1000, 0.1, 50), ((59, 40), 1000, 0.1, 50),
 )
)

walls = (
 (#Walls: position
  (45, 0), (45, 1), (45, 2), (45, 3), (45, 4), (45, 5), (45, 6),
  (45, 7), (45, 8), (45, 9), (45, 10), (45, 11), (45, 12), (45, 13),
  (45, 14), (45, 15), (45, 16), (45, 17), (45, 18), (45, 19), (45, 20),
  (45, 21), (45, 22), (45, 23), (45, 24), (45, 25), (45, 26), (45, 27),
  (45, 28), (45, 29), (45, 30), (45, 31), (45, 32), (45, 33), (45, 34),
  (45, 35), (45, 36), (45, 37), (45, 38), (45, 39),
  (54, 99), (54, 98), (54, 97), (54, 96), (54, 95), (54, 94), (54, 93),
  (54, 92), (54, 91), (54, 90), (54, 89), (54, 88), (54, 87), (54, 86),
  (54, 85), (54, 84), (54, 83), (54, 82), (54, 81), (54, 80), (54, 79),
  (54, 78), (54, 77), (54, 76), (54, 75), (54, 74), (54, 73), (54, 72),
  (54, 71), (54, 70), (54, 69), (54, 68), (54, 67), (54, 66), (54, 65),
  (54, 64), (54, 63), (54, 62), (54, 61), (54, 60),
  (0, 54), (1, 54), (2, 54), (3, 54), (4, 54), (5, 54), (6, 54),
  (7, 54), (8, 54), (9, 54), (10, 54), (11, 54), (12, 54), (13, 54),
  (14, 54), (15, 54), (16, 54), (17, 54), (18, 54), (19, 54), (20, 54),
  (21, 54), (22, 54), (23, 54), (24, 54), (25, 54), (26, 54), (27, 54),
  (28, 54), (29, 54), (30, 54), (31, 54), (32, 54), (33, 54), (34, 54),
  (35, 54), (36, 54), (37, 54), (38, 54), (39, 54),
  (99, 45), (98, 45), (97, 45), (96, 45), (95, 45), (94, 45), (93, 45),
  (92, 45), (91, 45), (90, 45), (89, 45), (88, 45), (87, 45), (86, 45),
  (85, 45), (84, 45), (83, 45), (82, 45), (81, 45), (80, 45), (79, 45),
  (78, 45), (77, 45), (76, 45), (75, 45), (74, 45), (73, 45), (72, 45),
  (71, 45), (70, 45), (69, 45), (68, 45), (67, 45), (66, 45), (65, 45),
  (64, 45), (63, 45), (62, 45), (61, 45), (60, 45),
 ),
 (#Sponges: position
  (45, 40), (46, 40), (47, 40), (48, 40), (49, 40), (50, 40), (51, 40),
  (52, 40), (53, 40), (54, 40),
  (54, 59), (53, 59), (52, 59), (51, 59), (50, 59), (49, 59), (48, 59),
  (47, 59), (46, 59), (45, 59),
  (40, 54), (40, 53), (40, 52), (40, 51), (40, 50), (40, 49), (40, 48),
  (40, 47), (40, 46), (40, 45),
  (59, 45), (59, 46), (59, 47), (59, 48), (59, 49), (59, 50), (59, 51),
  (59, 52), (59, 53), (59, 54),
 )
)
