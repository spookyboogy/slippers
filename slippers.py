import os
from helpers import *


def test_run():
    
    user_code = get_user_code(quiet=quiet, testing=testing)
    replay_directory = str(os.sep).join(__file__.split('/')[:-1])

    test_files = [os.path.join(replay_directory, file) 
                for file in os.listdir(replay_directory) if file.endswith('.slp')]

    decorator = '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ・'
    for test_file in test_files:
        print(decorator)
        fetch_and_print(test_file, user_code, quiet=False, no_fetch=no_fetch)
    print(decorator)


def main():

    
    most_recent_game = get_most_recent_game(replay_directory, quiet=quiet)
    most_recent_opponent = fetch_and_print(most_recent_game, user_code,
                                            quiet=True, no_fetch=no_fetch)
    opponent_cache = []
    streaming = bool(not most_recent_opponent)


    while True:

        if quiet:
            os.system("cls" if os.name == "nt" else "clear")
        else:
            print(f'\n~~ mrg : ...{most_recent_game[-10:]}')
            print(f"~~ mro : {most_recent_opponent.splitlines()[0]}")
            print(f'~~ streaming : {streaming}')

        if most_recent_opponent:
            prompt = print_and_prompt(most_recent_opponent, quiet=quiet) 
            if prompt == "q":
                return
            
            # then check for new opponent
            most_recent_check =  get_most_recent_game(replay_directory, quiet=True)

            if most_recent_game != most_recent_check:
                # get a list of all the new games since current
                new_games = get_most_recent_game_list(replay_directory, most_recent_game,
                                                      quiet=quiet)
                # try getting opponents from each game (1st newest will be none if streaming)
                # this lazily uses fetch and print and set instead of doing it efficiently
                new_opponents = list(set(fetch_and_print(game, user_code, 
                                                         quiet=True, no_fetch=no_fetch)
                                                         for game in new_games))
                # print all new opponents since current
                print_opponents(new_opponents)

                # update most recent game
                most_recent_game = most_recent_check
                # add opponents (including nonetypes atm) to cache
                opponent_cache += [opp for opp in new_opponents if opp not in opponent_cache]
                # update most recent opponent
                most_recent_opponent = opponent_cache[-1]
                # update whether current game is streaming or not
                streaming = bool(not most_recent_opponent)
                if streaming:
                    prompt = print_in_progress()
                    if prompt == 'q':
                        return

            else:
                # pressed enter while still on the same game, do nothing
                prompt = print_and_prompt(most_recent_opponent, quiet=quiet) 
                if prompt == "q":
                    return
        else:
            if not most_recent_game:
                # most_recent_game will always exist if directory has slps
                # empty directory most likely
                input('\n\nEmpty directory?\
                       \nPress enter to check for a recent game...\n')
                most_recent_game = get_most_recent_game(replay_directory, quiet=quiet)
                if not most_recent_game:
                    print('Game not found... Quitting... ')
                    os.sleep(2)
                    return

            most_recent_check = get_most_recent_game(replay_directory, quiet=True)
            # most_recent_opponent will be None if most_recent_game is streaming
            # or if it was an offline vs game between 2 human players but ignoring that atm)
            # This will have to be rewritten once I figure out how to parse streams

            if most_recent_game == most_recent_check:
                #we have to check if the streaming game ended 
                opponent = fetch_and_print(most_recent_game, user_code,
                                            quiet=True, no_fetch=no_fetch)
                print('~~ checkies')
                if opponent:
                    # game ended
                    opponent_cache += [opponent]
                    most_recent_opponent = opponent
                    streaming = False
                    prompt = print_and_prompt(most_recent_opponent, quiet=quiet) 
                    if prompt == "q":
                        return
                else: 
                    # game still streaming
                    streaming = True
                    prompt = print_in_progress()
                    if prompt == 'q':
                        return
            else:
                if not quiet:
                    print('~~ no checkies !')
                # new games have come in since the streaming game was tested
                new_games = get_most_recent_game_list(replay_directory, most_recent_game,
                                                        quiet=quiet)
                # try getting opponents from each game (1st newest will be none if streaming)
                # this lazily uses fetch and print and set instead of doing it efficiently
                new_opponents = [fetch_and_print(game, user_code, quiet=True, no_fetch=no_fetch)
                                    for game in new_games]
                # print all new opponents since current
                if not quiet:
                    print('new games+opponents, no mro')
                print_opponents(new_opponents)



if __name__ == "__main__":

    os.system("cls" if os.name == "nt" else "clear")
    # print everything or don't
    quiet=True
    # provides hardcoded path and user code (mine, can rewrite) and
    # bypasses user prompts to make testing easier 
    testing=True
    # skips rank lookups to prevent unnecessary HTMLSession calls
    # to not ddos slippi.gg  while testing
    no_fetch=False

    user_code = get_user_code(quiet=quiet, testing=testing)
    replay_directory = set_base_directory(quiet=quiet, testing=testing)

    main()


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
# # set_base_directory could be changed to return replay_directory 
# # and a base_directory variable (equivalent if using default)
# # if the user is to be able to navigate between base and sub folders
# # 
# # Can expand slippers to collect oppoents during a given session
# # and display a summary of opponents (incl rank/elo/char(s)) 
# # on session quit.  
# # To do: 
# #     - Update readme with gallery images and a brief use description
# #     - clean up readme with proper markdown
# #     - investigate that one error
# #     - implement graceful error handling
# #     - add clipping feature which creates a log.txt file of 
# #       timestamp of current game (or just current game if not possible)
# #       (could include an optional message to commit to timestamp)
# #       on a set keystroke
# #