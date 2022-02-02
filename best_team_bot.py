import random

from typing import Iterable, List


from planet_wars.planet_wars import Player, PlanetWars, Order, Planet

from planet_wars.battles.tournament import get_map_by_id, run_and_view_battle, TestBot

import pandas as pd


class BestBotClass(Player):

    """

    Example of very simple bot - it send flee from its strongest planet to the weakest enemy/neutral planet

    """

    def __init__(self):

        self.last_turns = []

    def get_planets_to_attack(self, game: PlanetWars) -> List[Planet]:

        """

        :param game: PlanetWars object representing the map

        :return: The planets we need to attack

        """

        return [p for p in game.planets if p.owner != PlanetWars.ME]

    def ships_to_send_in_a_flee(
        self, source_planet: Planet, dest_planet: Planet
    ) -> int:

        return dest_planet.num_ships + 2

    def play_turn(self, game: PlanetWars) -> Iterable[Order]:

        """

        See player.play_turn documentation.

        :param game: PlanetWars object representing the map - use it to fetch all the planets and flees in the map.

        :return: List of orders to execute, each order sends ship from a planet I own to other planet.

        """

        my_planets = game.get_planets_by_owner(owner=PlanetWars.ME)

        if len(my_planets) == 0:
            return []

        # (2) Find my strongest planet.

        my_strongest_planet = max(my_planets, key=lambda planet: planet.num_ships)

        owner = 2 if len(my_planets) >= 6 else 0

        planets = game.get_planets_by_owner(owner)

        top_planets_gr = sorted(planets, key=lambda p: p.growth_rate)

        top_planets_ds = sorted(
            planets,
            key=lambda p: Planet.distance_between_planets(my_strongest_planet, p),
        )

        grades = get_planet_grade(top_planets_gr, top_planets_ds)

        planet_to_attack = best_planet_to_attack(
            self.last_turns, game, my_strongest_planet, grades
        )

        if not bool(planet_to_attack):

            return []

        self.last_turns += [planet_to_attack.planet_id]

        self.last_turns = (
            self.last_turns[-1:] if len(self.last_turns) > 2 else self.last_turns
        )

        # (1) If we currently have a fleet in flight, just do nothing.

        # if len(game.get_fleets_by_owner(owner=PlanetWars.ME)) >= 1:

        #     return []

        # (3) Find the weakest enemy or neutral planet.

        # planets_to_attack = self.get_planets_to_attack(game)

        # if len(planets_to_attack) == 0:

        #     return []

        # enemy_or_neutral_weakest_planet = min(

        #     planets_to_attack, key=lambda planet: planet.num_ships

        # )

        # (4) Send half the ships from my strongest planet to the weakest planet that I do not own.

        return [
            Order(
                my_strongest_planet,
                planet_to_attack,
                self.ships_to_send_in_a_flee(my_strongest_planet, planet_to_attack),
            )
        ]


class AttackEnemyWeakestPlanetFromStrongestBot(BestBotClass):
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


class AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot(BestBotClass):
    """
    Same like AttackWeakestPlanetFromStrongestBot but with smarter flee size.
    If planet is neutral send up to its population + 5
    If it is enemy send most of your ships to fight!

    Will it out preform AttackWeakestPlanetFromStrongestBot? see test_bot function.

    """

    def ships_to_send_in_a_flee(
        self, source_planet: Planet, dest_planet: Planet
    ) -> int:

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

    run_and_view_battle(
        BestBotClass(),
        AttackEnemyWeakestPlanetFromStrongestBot(),
        map_str,
    )


def check_bot():
    """
    Test AttackWeakestPlanetFromStrongestBot against the 2 other bots.
    Print the battle results data frame and the PlayerScore object of the tested bot.
    So is AttackWeakestPlanetFromStrongestBot worse than the 2 other bots? The answer might surprise you.
    """
    maps = [get_random_map(), get_random_map()]
    player_bot_to_test = BestBotClass()
    tester = TestBot(
        player=player_bot_to_test,
        competitors=[
            AttackEnemyWeakestPlanetFromStrongestBot(),
            AttackWeakestPlanetFromStrongestSmarterNumOfShipsBot(),
        ],
        maps=maps,
    )
    tester.run_tournament()

    # for a nicer df printing

    pd.set_option("display.max_columns", 30)

    pd.set_option("expand_frame_repr", False)

    print(tester.get_testing_results_data_frame())

    print("\n\n")

    print(tester.get_score_object())

    # To view battle number 4 uncomment the line below

    # tester.view_battle(4)


def get_planet_grade(gr_list, dis_list):

    grades = {}

    for i, p in enumerate(gr_list):

        grade = grades.get(p.planet_id, 0) + i

        grades[p.planet_id] = grade

    for i, p in enumerate(dis_list):

        grade = grades.get(p.planet_id, 0) + i

        grades[p.planet_id] = grade

    return sorted(grades.items(), key=lambda p: p[1])


def best_planet_to_attack(last_turns, game, my_strongest, planets_grades_list):

    for planet_id, grade in planets_grades_list:

        planet = PlanetWars.get_planet_by_id(game, planet_id)

        if (
            my_strongest.num_ships > 1.2 * planet.num_ships
            and not planet_id in last_turns
        ):
            return planet


if __name__ == "__main__":

    check_bot()

    view_bots_battle()
