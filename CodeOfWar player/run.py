import battlecode as bc
import random
import sys
import traceback
import time

import os
print(os.getcwd())

print("pystarting")

# A GameController is the main type that you talk to the game with.
# Its constructor will connect to a running game.
gc = bc.GameController()
directions = list(bc.Direction)
'''
my_team = gc.team()
enemy_team = bc.Team.Red
if my_team == bc.Team.Red:
	enemy_team = bc.Team.Blue
random.seed(datetime.now())

def find_free_locations_in_Mars():
	component_number = 0
	for i in range(marsHeight+1):
		for j in range(marsWidth+1):
			if (i, j) not in component:
				temp_location = bc.MapLocation(bc.Planet.Mars, i, j)
				try:
					if marsMap.is_passable_terrain_at(temp_location):
						#print('found free location on mars!')
						locations.append((i, j))
						flood_fill(i, j, component_number)
						component_number += 1

				except Exception as e:
					print(i, j)
					print('Error:', e)
					# use this to show where the error was
					traceback.print_exc()
'''

print("pystarted")

# It's a good idea to try to keep your bots deterministic, to make debugging easier.
# determinism isn't required, but it means that the same things will happen in every thing you run,
# aside from turns taking slightly different amounts of time due to noise.
random.seed(6137)

# let's start off with some research!
# we can queue as much as we want.
gc.queue_research(bc.UnitType.Rocket)
gc.queue_research(bc.UnitType.Worker)
gc.queue_research(bc.UnitType.Knight)

my_team = gc.team()

'''
Strategy:
    First use given workers and given 100 Karbonite- replicate to make more? Worker research to upgrade them- costs 25 rounds
    10-15 workers for karbonite harvesting
    factory produce knights, want to research that unit one at a time, do not go over 3-4 times
    workers replicate

    Then create a rocket as soon as we can, multiple, and collect resources
    5-10 units work together to make rocket, per group of rockets (full capability is 12 at level 3)

    Around round 700, get in rockets and fly to Mars

    Mars: create as many units as possible to win
'''

#logic for worker units
#CURRENT TODOS: Building rockets, repairing structures, reacting to enemy units
def workerWork(worker):
	for worker in workers:
		#if there is a worker deficit and we have the resources to replicate,
		#find a valid direction to do so.
		if len(workers) < 10 and gc.karbonite() >= 60:
			for dir in directions:
				if gc.can_replicate(worker.id, dir):
					replicate(worker.id, dir)
					print('replicating!')
					return #once an action is performed, that worker is done
		#build on any existing nearby blueprints. Took this bit of code from
		#below. Not entirely sure what the second param in this method is, and
		#I couldnt find it documented anywhere.
		nearby = gc.sense_nearby_units(worker.location.map_location(), 2)
		for other in nearby:
			if gc.can_build(worker.id, other.id):
				gc.build(unit.id, other.id)
				print('built a factory!')
				return
		#im not sure when the best times to build factories are, so for now
		#its just an arbitrary 10% chance they try doing that instead of
		#harvesting. This will only happen if there is enough Karbonite
		#to make a factory in the first place
		if gc.karbonite() > bc.UnitType.Factory.blueprint_cost():
			fact_chance = random.randint(0,9)
		else:
			fact_chance = 1
		#find a direction to harvest or set a blueprint
		for dir in directions:
			if fact_chance == 0:
				if gc.can_blueprint(worker.id, bc.UnitType.Factory, dir):
					gc.blueprint(worker.id, bc.UnitType.Factory, dir)
					return
			elif gc.can_harvest(worker.id, dir):
				gc.harvest(worker.id, dir)
				return
		#if this part of the code is reached, then the only thing left to do is move
		if gc.is_move_ready(worker.id):
			choices = [] #list of possible directions
			for dir in directions:
				if gc.can_move(worker.id, dir):
					choices.append(dir)
			#if there is a valid square to move to, do so
			if choices:
				gc.move_robot(worker.id, random.choice(choices))
				return
			#if there isnt, then it seems to be stuck...and it must die
			gc.disintegrate_unit(worker.id)

while True:
    # We only support Python 3, which means brackets around print()
    print('pyround:', gc.round(), 'time left:', gc.get_time_left_ms(), 'ms')

    # frequent try/catches are a good idea
    try:
		worker_units = []
        # walk through our units:
        for unit in gc.my_units():

			#add all workers to a list to be operated on at once
			if unit.unit_type == bc.UnitType.Worker:
				worker_units.append(unit)

            # first, factory logic
            if unit.unit_type == bc.UnitType.Factory:
                garrison = unit.structure_garrison()
                if len(garrison) > 0:
                    d = random.choice(directions)
                    if gc.can_unload(unit.id, d):
                        print('unloaded a knight!')
                        gc.unload(unit.id, d)
                        continue
                elif gc.can_produce_robot(unit.id, bc.UnitType.Knight):
                    gc.produce_robot(unit.id, bc.UnitType.Knight)
                    print('produced a knight!')
                    continue
			'''
            # first, let's look for nearby blueprints to work on
            location = unit.location
            if location.is_on_map():
                nearby = gc.sense_nearby_units(location.map_location(), 2)
                for other in nearby:
                    if unit.unit_type == bc.UnitType.Worker and gc.can_build(unit.id, other.id):
                        gc.build(unit.id, other.id)
                        print('built a factory!')
                        # move onto the next unit
                        continue
                    if other.team != my_team and gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
                        print('attacked a thing!')
                        gc.attack(unit.id, other.id)
                        continue

            # okay, there weren't any dudes around
            # pick a random direction:
            d = random.choice(directions)

            # or, try to build a factory:
            if gc.karbonite() > bc.UnitType.Factory.blueprint_cost() and gc.can_blueprint(unit.id, bc.UnitType.Factory, d):
                gc.blueprint(unit.id, bc.UnitType.Factory, d)
            # and if that fails, try to move
            elif gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
                gc.move_robot(unit.id, d)
			'''
		#once all units have been looked at, perform worker logic
		#the idea is to have each type of unit do all of their operations
		#at once, then moving on to the next one. Don't want to implement
		#that fully without further discussing with team, however. -Matt
		for worker in worker_units:
			workerWork(worker)

    except Exception as e:
        print('Error:', e)
        # use this to show where the error was
        traceback.print_exc()

    # send the actions we've performed, and wait for our next turn.
    gc.next_turn()

    # these lines are not strictly necessary, but it helps make the logs make more sense.
    # it forces everything we've written this turn to be written to the manager.
    sys.stdout.flush()
    sys.stderr.flush()
'''

A MapLocation represents a concrete space on a given planet. It has x and y coordinates,
in addition to the planet itself, as attributes.


A Location represents the location of a robot. Whenever a robot is on a map, this object maps directly to a MapLocation object.
However, this is not always the case! A Location may also represent a point in space (as in the case of a rocket traveling to Mars),
or a space in a structure’s garrison.
Methods can be used to determine, more concretely, what a Location represents.
'''
#To Handle:
    #Earth:
        #impassible water spots
        #Factories
        #Workers- pick up harvest karbonite, build, repair, blueprint, or replicate (1 to 3 at start)
        #Knights- javelin
        #Mages- fight
        #Rangers- snipe
        #Healers- heal
        #other robots from opponent
        #Rockets to mars: need to build, then find a correct space to land and survive
    #Mars:
        #rocketing to land in a good spot, not right away, but before the flood on Earth
        #karbonite, structures, other robots
        #unwalkable terrain
        #meteor storms