import warnings

import pandas as pd

from planet_wars.battles.tournament import Tournament
from best_team_bot import BestBotClass
from Dima_ron_aviv_bot import dima
from dy_team import dyBot
from penguins_bot import penguins_bot
from runtime_Terror import ETerror
from space_pirate_bot import SpacePirateBot
from team_wizards import WizardsBot
from planet_wars.player_bots.RHUL.RHUL_bot import RhulBot
from dream_team_bot import DreamTeamV1
from team_ziv_bot import TeamZivBot

# Insert Your bot object here, as BotObject(). Don't forget to set BotObject.NAME to your team name
PLAYER_BOTS = [
    BestBotClass(),
    dima(),
    dyBot(),
    penguins_bot(),
    ETerror(),
    SpacePirateBot(),
    WizardsBot(),
    RhulBot(),
    DreamTeamV1(),
    TeamZivBot()
]


ROUND1_MAP = """P 13 13 0 36 4
P 3.7820839879289565 12.57131994383198 1 100 5
P 14.566680518832031 22.09391303829458 2 100 5
P 6.714699700365638 20.23041089459612 0 81 4
P 5.471494067341194 21.660555378506636 0 35 1
P 24.735601688020807 8.489327141914504 0 8 3
P 16.0229442973115 0.7962168001927417 0 8 3
P 6.436172310561731 2.873730227972443 0 73 5
P 23.861041702180607 18.259557640715546 0 73 5
P 23.01027681820345 8.585404917274749 0 95 2
P 16.14122363806936 2.5201619393657797 0 95 2
P 20.862860436292834 11.056744855024498 0 6 2
P 13.954777609541708 4.957039443375921 0 6 2
P 8.420223458807161 8.169133999180557 0 35 5
P 18.360731572897127 16.94641311680333 0 35 5
P 21.431433058369393 14.134653557437993 0 50 2
P 10.830154961442174 4.773927144632324 0 50 2"""

if __name__ == '__main__':
    # Display options
    warnings.simplefilter(action='ignore')
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('expand_frame_repr', False)

    tournament = Tournament(PLAYER_BOTS, [ROUND1_MAP], all_against_all=False)
    battle_results = tournament.run_tournament()
    # player_scores_df = tournament.get_player_scores_data_frame()
    battle_results_df = tournament.get_battle_results_data_frame()
    # print(player_scores_df)
    print(battle_results_df)

    # player_scores_df.to_parquet("./player_scores_df.parquet")
    battle_results_df.to_parquet("./battle_results_df.parquet")
    # player_scores_df.to_csv("./player_scores_df.csv")
    battle_results_df.to_csv("./battle_results_df.csv")
    # TODO commit the saved df so all players can see the battle results