import os
import time
from helpers import *
from datetime import date

def test_run():

    test_files = [os.path.join(replay_directory, file) 
                for file in os.listdir(replay_directory) if file.endswith('.slp')]

    for test_file in test_files:
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ・')
        fetch_and_print(test_file, quiet=quiet, no_fetch=no_fetch)


def main(directory, quiet=False, testing=False, no_fetch=False):

   
    # Testing april's games, make a way to optionally select month subfolder

    #user_code = user_code
    most_recent_game = get_most_recent_game(directory)
    most_recent_opponent = fetch_and_print(most_recent_game, user_code,
                                           quiet=True, no_fetch=no_fetch)
    while True:
        
        os.system("cls" if os.name == "nt" else "clear")
        print(f'~~~~~~~~~ opp.\n{most_recent_opponent}\n~~~~~~~~~\n')
        s = input('[q] Quit \nPress enter to update... ')

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
    testing=True
    # skips rank lookups to prevent unnecessary HTMLSession calls
    # to not ddos slippi.gg  while testing
    no_fetch=True

    user_code = get_user_code(quiet=quiet, testing=testing)
    replay_directory = set_base_directory(quiet=quiet, testing=testing)
    # # useless flag to keep track of whether we're in the base directory
    # in_base_directory = True

    if not testing:
        s = input('Using current month subfolder? Y/N : ')
        if s.lower() == 'y':
            d = date.today()
            # in_base_directory = False
            # parent_directory = replay_directory 
            year = d.year
            month = d.strftime("%m")
            replay_directory += os.sep + f"{year}-{month}"
    else:
        replay_directory += os.sep + "2023-04"
    

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