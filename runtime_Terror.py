import random
from typing import Iterable, List

from planet_wars.planet_wars import Player, PlanetWars, Order, Planet
from planet_wars.battles.tournament import get_map_by_id, run_and_view_battle, TestBot

import pandas as pd


class ETerror(Player):
    """
    Eterro
    """
    def get_planets_to_attack(self, game: PlanetWars) -> List[Planet]:
        """
        :param game: PlanetWars object representing the map
        :return: The planets we need to attack
        """

        return [p for p in game.planets if p.owner != PlanetWars.ME]
    
    def get_my_planets(self, game: PlanetWars) -> List[Planet]:
        """
        :param game: PlanetWars object representing the map
        :return: The planets we need to attack
        """

        return [p for p in game.planets if p.owner == PlanetWars.ME]

    def calc_fleet(source_planet: Planet, dest_planet: Planet):
        dis = Planet.distance_between_planets(source_planet, dest_planet)
        if dest_planet.owner == 2:
            return dest_planet.num_ships + (dest_planet.growth_rate * dis)
        return dest_planet.num_ships

    def get_all_planets_list (self, game:PlanetWars):
        return [p for p in game.planets if p.owner != PlanetWars.ME]
        
    def farest_planet_rate(self, game: PlanetWars, source_planet: Planet):
        distance_key = lambda a: Planet.distance_between_planets(source_planet, a)
        return sorted(self.get_all_planets_list(game),key=distance_key)


    def biggest_growth_rate(self, game: PlanetWars):
        keyGrowthRate = lambda a:a.growth_rate
        return sorted(self.get_all_planets_list(game),key=keyGrowthRate)
        
    def smallest_planet_fleet(self, game: PlanetWars):
        key_num_ships = lambda a:a.num_ships
        return sorted(self.get_all_planets_list(game),key=key_num_ships)
        
        
    def best_option(self, game: PlanetWars, source_planet: Planet)->Planet:
        distanceList = self.farest_planet_rate(game, source_planet)[::-1]
        growthList = self.biggest_growth_rate(game)
        armiesList = self.smallest_planet_fleet(game)[::-1]
        bestOption = {p: 0 for p in self.get_all_planets_list(game)}

        for index, planet in enumerate(distanceList):
            bestOption[planet] +=  index
        for index, planet in enumerate(growthList):
            bestOption[planet] +=  index    
        for index, planet in enumerate(armiesList):
            bestOption[planet] +=  index
        if bestOption:
            target = max(bestOption.items(),key= lambda a:a[1])[0]
            return target
        return None
   

    def ships_to_send_in_a_flee(self, source_planet: Planet, dest_planet: Planet) -> int:
        if dest_planet.owner == 2:
            dest_ships_num = dest_planet.num_ships + (dest_planet.growth_rate * Planet.distance_between_planets(source_planet, dest_planet)) + 1
        elif dest_planet.owner == 0:
            dest_ships_num = dest_planet.num_ships + 1
        if source_planet.num_ships > dest_ships_num:
            return dest_ships_num
        return 0

    def play_turn(self, game: PlanetWars) -> Iterable[Order]:
        """
        See player.play_turn documentation.
        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.
        :return: List of orders to execute, each order sends ship from a planet I own to other planet.
        """
        orders = []
        for planet in self.get_my_planets(game):
            attack_planet = self.best_option(game,planet)
            if not attack_planet:
                return []
            troops = self.ships_to_send_in_a_flee(planet,attack_planet)
            if troops > 0:
                orders.append(Order(planet,attack_planet,troops))
        return orders

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
    run_and_view_battle(ETerror(), AttackWeakestPlanetFromStrongestBot(), map_str)


def check_bot():
    """
    Test AttackWeakestPlanetFromStrongestBot against the 2 other bots.
    Print the battle results data frame and the PlayerScore object of the tested bot.
    So is AttackWeakestPlanetFromStrongestBot worse than the 2 other bots? The answer might surprise you.
    """
    maps = [get_random_map(), get_random_map()]
    player_bot_to_test = AttackWeakestPlanetFromStrongestBot()
    tester = TestBot(
        player=player_bot_to_test,
        competitors=[
            ETerror(), AttackWeakestPlanetFromStrongestBot()
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
