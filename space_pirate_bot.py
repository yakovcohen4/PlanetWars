import random
import math
from typing import Iterable, List

from planet_wars.planet_wars import Player, PlanetWars, Order, Planet
from planet_wars.battles.tournament import get_map_by_id, run_and_view_battle, TestBot

import pandas as pd


class SpacePirateBot(Player):
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
        # return int(source_planet.num_ships * 0.7)
        original_num_of_ships = source_planet.num_ships // 2
        if dest_planet.owner == PlanetWars.NEUTRAL:
            if dest_planet.num_ships < original_num_of_ships:
                return dest_planet.num_ships + 5
        if dest_planet.owner == PlanetWars.ENEMY:
            return int(source_planet.num_ships * 0.75)
        return original_num_of_ships
    # def distance_between_planets(planetA: Planet, planetB: Planet):

    #     return math.dist([planetA.x, planetA.y], [planetB.x, planetB.y])

    def ideal_planet_to_attack(self, planets: List[Planet], origin_planet: Planet) -> Planet:
        all_planets_ranked = []
        for p in planets:
            # print(f'Num of ships: {p.num_ships}')
            ratio = int(origin_planet.num_ships * 0.5)
            if p.num_ships <= ratio:
                score = (p.growth_rate * p.num_ships) / \
                    p.distance_between_planets(origin_planet, p)
                all_planets_ranked.append((p, score))

        # print(f'All planets ranked: {all_planets_ranked}')
        if len(all_planets_ranked) != 0:
            ideal = max(all_planets_ranked, key=lambda t: t[1])[0]
        else:
            ideal = min(planets, key=lambda planet: planet.num_ships)

        return ideal  # a planet

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
        my_strongest_planet = max(
            my_planets, key=lambda planet: planet.num_ships)

        # (3) Find the weakest enemy or neutral planet.
        planets_to_attack = self.get_planets_to_attack(game)
        if len(planets_to_attack) == 0:
            return []
        # enemy_or_neutral_weakest_planet = min(planets_to_attack, key=lambda planet: planet.num_ships)
        enemy_or_neutral_weakest_planet = self.ideal_planet_to_attack(
            planets_to_attack, my_strongest_planet)

        # (4) Send half the ships from my strongest planet to the weakest planet that I do not own.
        return [Order(
            my_strongest_planet,
            enemy_or_neutral_weakest_planet,
            self.ships_to_send_in_a_flee(
                my_strongest_planet, enemy_or_neutral_weakest_planet)
        )]
