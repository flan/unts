# -*- coding: utf-8 -*-
"""
Unts module: system; controls the simulation.

Configuration
=============
 To change the rules of a simulation, edit seed.py to your liking. It is fully
 documented.

Usage
=====
 To run this program, open Breve, then load this file. Start the simulation as
 normal.
 
Legal
=====
 All code, unless otherwise indicated, is original, and subject to the terms of
 the attached licensing agreement.
 
 Copyright (c) Neil Tallim, 2008
 
 Unts is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 2 of the License, or
 (at your option) any later version.
 
 Unts is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.
 
 You should have received a copy of the GNU General Public License
 along with this program; if not, write to the Free Software
 Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA 
"""
import breve

import math
import gc

import seed
import shared
shared.initialize(seed.environment) #Set up the simulation's shared data.

import colony
import map
import inerts
import agents
import time

class System(breve.Control):
	"""
	A control class, as required by breve for the execution of Python code.
	"""
	_field = None #: The current state of the system's field, which contains everything.
	_tick = 0 #: The current discrete time-step of the system.
	
	def __init__(self):
		"""
		Initializes breve and defines the simulation in terms of values read from
		seed.py.
		"""
		breve.Control.__init__(self)
		
		#Initialize the system. Use minimal settings to get more cycles for computation.
		self.setBackgroundColor(breve.vector(1, 1, 1))
		self.disableLighting()
		self.disableBlur()
		self.disableFog()
		self.disableLightExposureDetection()
		self.disableLightExposureDrawing()
		self.disableReflections()
		self.disableShadowVolumes()
		self.disableShadows()
		self.disableText()
		self.disableSmoothDrawing()
		self.pointCamera(
		 breve.vector((shared.ENVIRONMENT.FIELD_WIDTH - 1) / 2.0, (shared.ENVIRONMENT.FIELD_HEIGHT - 1) / 2.0, 0),
		 breve.vector(0, 0, -140)
		)
		
		#Create colonies
		for (config, hills) in seed.colonies:
			new_colony = colony.Colony(config)
			shared.COLONIES.append(new_colony)
			for (position, workers, warriors, builders) in hills:
				hill = inerts.Hill(new_colony, position)
				hill.generateUnts(workers, warriors, builders)
				
		#Create threats
		(predators, hunters, stalkers) = seed.threats
		for position in predators:
			shared.THREATS.append(agents.Predator(position))
		for position in hunters:
			shared.THREATS.append(agents.Hunter(position))
		for position in stalkers:
			shared.THREATS.append(agents.Stalker(position))
			
		#Create resources
		(food, water) = seed.resources
		for (position, capacity, replenishment, cooldown) in food:
			shared.RESOURCES.append(inerts.Food({
			 'capacity': capacity,
			 'replenishment': replenishment,
			 'cooldown': cooldown
			}, position))
		for (position, capacity, replenishment, cooldown) in water:
			shared.RESOURCES.append(inerts.Water({
			 'capacity': capacity,
			 'replenishment': replenishment,
			 'cooldown': cooldown
			}, position))
			
		#Create walls
		(walls, sponges) = seed.walls
		for position in walls:
			shared.WALLS.append(inerts.Wall(position))
		for position in sponges:
			shared.WALLS.append(inerts.Sponge(position))
			
		#Create field
		self._field = map.Field((shared.ENVIRONMENT.FIELD_WIDTH, shared.ENVIRONMENT.FIELD_HEIGHT))
		
	def iterate(self):
		"""
		Called by breve each tick, this function handles the process of moving
		from one discrete time-step to another.
		
		@return: Nothing.
		"""
		start_time = time.time() #Used to calculate the speed of the simulation.
		
		new_field = map.Field(self._field.getDimensions())
		
		#Draw walls.
		for wall in shared.WALLS:
			wall.plant(new_field)
			
		#Replenish resources.
		for resource in shared.RESOURCES:
			resource.plant(new_field)
			resource.tick()
			
		#Update the pheromone map.
		pheromones_processed = new_field.flowPheromones(self._field)
		
		#Update the threats.
		for threat in shared.THREATS:
			if threat.tick():
				threat.act(self._field, new_field)
				new_field.getSpace(threat.getPosition()).addAgent(threat)
				
		#Update the unts and add the hills.
		unts = []
		for colony in shared.COLONIES:
			unts += colony.getArchitects()
			for hill in colony.getHills():
				hill.plant(new_field)
				unts += hill.getUnts()
		shared.RANDOMIZER.shuffle(unts)
		for unt in unts:
			if unt.tick():
				unt.act(self._field, new_field)
				new_field.getSpace(unt.getPosition()).addAgent(unt)
				
		#Tick each colony.
		for colony in shared.COLONIES:
			colony.tick()
			
		#Finalize the transition.
		self._field = new_field
		self._tick += 1
		
		#Print statistics about the transition.
		print "Iteration: %i; time taken: %fs; pheromones: %i; agents: %i" % \
		 (self._tick, time.time() - start_time, pheromones_processed, len(shared.AGENTS))
breve.System = System

System() #Start the simulation.
