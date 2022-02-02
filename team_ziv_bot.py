from asyncio.proactor_events import constants
from math import ceil
from pprint import pprint
import random
from typing import Iterable, List

from planet_wars.planet_wars import Player, PlanetWars, Order, Planet
from planet_wars.battles.tournament import get_map_by_id, run_and_view_battle, TestBot

import pandas as pd

RELEVANT_PLANET_AMOUNT = 5

class TeamZivBot(Player):
    def get_planets_to_attack(self, game: PlanetWars) -> List[Planet]:
        return [p for p in game.planets if p.owner != PlanetWars.ME] # all not me planets

    def get_ship_in_radius(self, game: PlanetWars,center_planet: Planet, radius: int, owner):
        planets = [planet for planet in game.planets if planet.owner == owner and Planet.distance_between_planets(planet, center_planet) <= radius]
        planets.sort(key = lambda planet: planet.distance_between_planets(planet,center_planet))
        return planets

    def defend(self,game: PlanetWars):
        for enemy_fleet in game.get_fleets_by_owner(owner=PlanetWars.ENEMY):
            dest_planet = game.planets[enemy_fleet.destination_planet_id]
            if(dest_planet.owner != PlanetWars.ME):
                continue
            ships_i_will_have = dest_planet.num_ships + enemy_fleet.turns_remaining * dest_planet.growth_rate
            if(ships_i_will_have > enemy_fleet.num_ships):
                continue # bad attack

            ships_i_need =  enemy_fleet.num_ships - ships_i_will_have
            all_relevant_planets = self.get_ship_in_radius(game, dest_planet, enemy_fleet.turns_remaining, PlanetWars.ME)
            print(all_relevant_planets, ships_i_need)
            if not all_relevant_planets:
                continue
            relevant_planets = all_relevant_planets[0:RELEVANT_PLANET_AMOUNT]
            total_relevant_ships = sum([planet.num_ships for planet in relevant_planets])

            return [Order(planet,dest_planet,ceil((ships_i_need / total_relevant_ships) * planet.num_ships)) for planet in relevant_planets]
        return []

    def me_planets(self, game: PlanetWars):
        planets = [planet for planet in game.planets if planet.owner == PlanetWars.ME]
        return planets

    def attack(self, game: PlanetWars):
        if len([flee for flee in game.fleets if flee.owner == PlanetWars.ME]) >= len(game.get_planets_by_owner(PlanetWars.ME)):
            return []
        me_planets = self.me_planets(game)
        not_me_planets = [planet for planet in game.planets if planet.owner != PlanetWars.ME]
        if len(me_planets) == 0 or len(not_me_planets) == 0:
            return []
        strongest_planet = max(me_planets, key = lambda planet: planet.num_ships)
        closest_planet = min(not_me_planets, key = lambda planet: planet.num_ships + 10*Planet.distance_between_planets(planet, strongest_planet))
        return [Order(
            strongest_planet,
            closest_planet,
            strongest_planet.num_ships
        )]

    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        order = []

        a = self.attack(game)
        d = self.defend(game)
        if (len(d) > 0): order +=d
        if (len(a) > 0): order +=a
        return order


class AttackWeakestPlanetFromStrongestBot(Player):
    """
    Example of very simple bot - it send flee from its strongest planet to the weakest enemy/neutral planet
    """

    def get_planets_to_attack(self, game: PlanetWars) -> List[Planet]:
        """
        :param game: PlanetWars object representing the map
        :return: The planets we need to attack
        """
        return [p for p in game.planets if p.owner != PlanetWars.ME]

    def ships_to_send_in_a_flee(self, source_planet: Planet, dest_planet: Planet) -> int:
        return source_planet.num_ships // 2

    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """
        # (1) If we currently have a fleet in flight, just do nothing.
        if len(game.get_fleets_by_owner(owner=PlanetWars.ME)) >= 1:
            return []

        # (2) Find my strongest planet.
        my_planets = game.get_planets_by_owner(owner=PlanetWars.ME)
        if len(my_planets) == 0:
            return []
        my_strongest_planet = max(my_planets, key=lambda planet: planet.num_ships)

        # (3) Find the weakest enemy or neutral planet.
        planets_to_attack = self.get_planets_to_attack(game)
        if len(planets_to_attack) == 0:
            return []
        enemy_or_neutral_weakest_planet = min(planets_to_attack, key=lambda planet: planet.num_ships)

        # (4) Send half the ships from my strongest planet to the weakest planet that I do not own.
        return [Order(
            my_strongest_planet,
            enemy_or_neutral_weakest_planet,
            self.ships_to_send_in_a_flee(my_strongest_planet, enemy_or_neutral_weakest_planet)
        )]


class AttackEnemyWeakestPlanetFromStrongestBot(AttackWeakestPlanetFromStrongestBot):
    """
    Same like AttackWeakestPlanetFromStrongestBot but attacks only enemy planet - not neutral planet.
    The idea is not to "waste" ships on fighting with neutral planets.
    See which bot is better using the function view_bots_battle
    """

    def get_planets_to_attack(self, game: PlanetWars):
        """
        :param game: PlanetWars object representing the map
        :return: The planets we need to attack - attack only enemy's planets
        """
        return game.get_planets_by_owner(owner=PlanetWars.ENEMY)


class AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot(AttackWeakestPlanetFromStrongestBot):
    """
    Same like AttackWeakestPlanetFromStrongestBot but with smarter flee size.
    If planet is neutral send up to its population + 5
    If it is enemy send most of your ships to fight!
    Will it out preform AttackWeakestPlanetFromStrongestBot? see test_bot function.
    """

    def ships_to_send_in_a_flee(self, source_planet: Planet, dest_planet: Planet) -> int:
        original_num_of_ships = source_planet.num_ships // 2
        if dest_planet.owner == PlanetWars.NEUTRAL:
            if dest_planet.num_ships < original_num_of_ships:
                return dest_planet.num_ships + 5
        if dest_planet.owner == PlanetWars.ENEMY:
            return int(source_planet.num_ships * 0.75)
        return original_num_of_ships


def get_random_map():
    """
    :return: A string of a random map in the maps directory
    """
    random_map_id = random.randrange(1, 100)
    return get_map_by_id(random_map_id)


def view_bots_battle():
    """
    Runs a battle and show the results in the Java viewer
    Note: The viewer can only open one battle at a time - so before viewing new battle close the window of the
    previous one.
    Requirements: Java should be installed on your device.
    """
    map_str = get_random_map()
    run_and_view_battle(TeamZivBot(), AttackEnemyWeakestPlanetFromStrongestBot(), map_str)


def check_bot():
    maps = [get_random_map(), get_random_map()]
    player_bot_to_test = TeamZivBot()
    tester = TestBot(
        player=player_bot_to_test,
        competitors=[
            AttackEnemyWeakestPlanetFromStrongestBot(), AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot()
        ],
        maps=maps
    )
    tester.run_tournament()

    # for a nicer df printing
    pd.set_option('display.max_columns', 30)
    pd.set_option('expand_frame_repr', False)

    print(tester.get_testing_results_data_frame())
    print("\n\n")
    print(tester.get_score_object())

    # To view battle number 4 uncomment the line below
    # tester.view_battle(4)


if __name__ == "__main__":
    check_bot()
    view_bots_battle()