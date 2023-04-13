import os
import time
from helpers import *
from datetime import date


def test_run():
    
    replay_directory = str(os.sep).join(__file__.split('/')[:-1])
    test_files = [os.path.join(replay_directory, file) 
                for file in os.listdir(replay_directory) if file.endswith('.slp')]

    decorator = '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ・'
    for test_file in test_files:
        print(decorator)
        fetch_and_print(test_file, user_code, quiet=False, no_fetch=no_fetch)
    print(decorator)


def main(directory, quiet=False, testing=False, no_fetch=False):

    most_recent_game = get_most_recent_game(directory)
    most_recent_opponent = fetch_and_print(most_recent_game, user_code,
                                           quiet=True, no_fetch=no_fetch)
    while True:
        
        os.system("cls" if os.name == "nt" else "clear")
        print(f'~~~~~~~~~ opp.\n{most_recent_opponent}\n~~~~~~~~~\n')
        s = input(f'\n[q] Quit \nPress enter to update... \n')

        if s.lower() == "q":
            return
        time.sleep(1)

        most_recent_check =  get_most_recent_game(directory)

        if most_recent_game != most_recent_check:
            most_recent_game = most_recent_check
            most_recent_opponent_check = fetch_and_print(most_recent_game, user_code, 
                                                         quiet=True, no_fetch=no_fetch)
            if most_recent_opponent != most_recent_opponent_check:
                most_recent_opponent = most_recent_opponent_check
        

if __name__ == "__main__":

    os.system("cls" if os.name == "nt" else "clear")
    # print everything or don't
    quiet=False
    # provides hardcoded path and user code (mine, can rewrite) and
    # bypasses user prompts to make testing easier 
    testing=False
    # skips rank lookups to prevent unnecessary HTMLSession calls
    # to not ddos slippi.gg  while testing
    no_fetch=False

    user_code = get_user_code(quiet=quiet, testing=testing)
    replay_directory = set_base_directory(quiet=quiet, testing=testing)
    # # set_base_directory could be changed to return replay_directory 
    # # and a base_directory variable (equivalent if using default)
    # # useless flag to keep track of whether we're in the base directory
    # in_base_directory = True

    d = date.today() 
    year, month = d.year, d.strftime("%m")
    subfolder = f"{year}-{month}"
    if not testing:
        s = input('Using current month subfolder? Y/N : ')
        if s.lower() == 'y':
            # in_base_directory = False
            # parent_directory = replay_directory 
            replay_directory += os.sep + subfolder
    else:
        if subfolder in os.listdir(replay_directory):
            replay_directory +=  os.sep + subfolder

    main(replay_directory, quiet=quiet, testing=testing, no_fetch=no_fetch)


# # Write modes for displaying a custom amount of .slp's 
# # ie, maybe we only want the ranks from the past session, or maybe we want
# # the whole month. Or, maybe we only want the most recent player, 
# # or current/live player, if this script can run as a dolphin hook.
# # Or, a "--More--"-like tool which goes through the n most recent opponents
# # 
# # Maybe implement getch() while maintaining original behavior 
# # when getch is unavailable
# # ie 
# # try:
# #     import getch
# #     has_getch = True
# # else:
# #     has_getch = False
# # 