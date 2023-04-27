import os
from os.path import getmtime
import sys
from datetime import date
from requests_html import HTMLSession
import slippi
from slippi.parse import parse
from slippi.parse import ParseEvent, ParseError
import traceback


def get_single_rank(player_hash_code, quiet=True):
    """
    write a different version for getting multiple ranks to avoid
    making unnecessary repeated session calls

    expand this version to fetch other info like character usage stat
    """

    if not player_hash_code:
        if not quiet:
            print('___\nno user provided...\n')
        return None
    
    base_url = "https://slippi.gg/user/"
    user_url = '-'.join(player_hash_code.split('#'))
    url = base_url + user_url

    if not quiet:
        print(f'_____\nurl : {url} ...\n')

    # might want to use async instead for some reason
    with HTMLSession() as session:
        response = session.get(url)
    response.html.render()
    elements = response.html.find('div.jss7')

    if not elements:
        if not quiet:
            print('search return empty, maybe bad url')
        return None
    else:
        res = elements[0].text
        return res 


def get_player_codes(slippi_file, quiet=False):
    """
    needs to be updated to check whether slippi_file is a:
    - cpu file (cpu's don't have codes, cpu.code returns an error)
    - stream (needs to use parser instead of game module, I think)
    - past non-cpu game (default)

    if cpu, fetch_and_print should print 'CPU' accordingly
    """
    
    try:
        game = slippi.Game(slippi_file)
    except Exception as ex:
        # this generally means that the file is currently being written to
        # a parser would be used in this case to read the file as a stream
        # however that's not working atm
        if not quiet:
            print(f'\n\n!!\n{ex.__annotations__}\n!!\n')
        return None

    players = [player for player in game.metadata.players]
    stage = game.start.stage.name.title().replace('_', ' ')
    
    if not quiet:
        print(f'\n~~~~~~~~~~~~~~~~ ...{slippi_file[-10:]}\
                \nStage : {stage}')

    codes = []
    for p in range(len(players)):
        if not players[p]:
            continue
        try:
            char = list(players[p].characters.items())[0][0].name.title()
            player_type = game.start.players[p].type.name
            if not quiet:
                print(f'\n  Player type : {player_type}\
                        \n  Char : {char}\n\
                        \n  Player {p + 1}:\n  {players[p]}\
                        \n  Netplay = {players[p].netplay}')
                print('  ~~~~~~~~')
            if players[p].netplay == None:
                if player_type == 'CPU':
                    codes += [f'CPU {char}\n {stage}']
                else:
                    codes += [f'Offline {char}']
                    pass
            else:
                codes += [players[p].netplay.code]
        except Exception as ex:
            print(ex)
            print(f'player {p}:\n{players[p]}')
    if not quiet:
        print('~~~~~~~~~~~~~~~~')
    return codes


def get_user_code(testing=False, quiet=False):
    """
    code format -> name#number or name-number

    Not checking code validity yet.
    Can be inferred from looking at more than one .slp 
    """

    if testing:
        user_code = "Nils-626".upper().replace('-', '#')
    else:
        print("\nEnter your connect code: ")
        user_code = sys.stdin.readline().strip('\n')
        # if block to make empty input use my code, will remove later
        if user_code:
            user_code = user_code.upper().replace('-', '#')
        else:
            user_code = "Nils-626".upper().replace('-', '#')

    if not quiet:
        print(f'user code : {user_code}\n')

    return user_code


def set_base_directory(quiet=False, testing=False):
    
    user_home = os.path.expanduser('~')
    default_location = os.path.join('Documents','Slippi')
    default_directory = f"{user_home}{os.sep}{default_location}"

    if not quiet:
        print(f'Working in :\n    {os.getcwd()}')
        print(f'Default replay directory :\n    {default_directory}\n')

    if testing:
        # this is set to whatever directory I'm using it in,
        # change it to your own to skip the directory prompt.
        # this should eventually change to default to the 
        # directory where slippers is located, so that it uses the 
        # provided test.slp's 
        replay_directory = default_directory
        replay_directory = set_sub_folder(replay_directory, testing=testing)

        if not quiet:
            print(f'Using : \n\t{replay_directory}\n')
        return replay_directory

    # prompt user
    print(f"Enter the path to your main replay directory.\
          \nThe default is usually:\n    '{default_directory}'...")
    path = sys.stdin.readline().strip('\n')

    if path:
        replay_directory = path
    else:
        replay_directory = default_directory

    replay_directory = set_sub_folder(replay_directory, testing=testing)
    print(f'Using : {replay_directory}\n')

    return replay_directory


def set_sub_folder(replay_directory, testing=False):

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
        # assumes you're using the current month subfolder
        if subfolder in os.listdir(replay_directory):
            replay_directory +=  os.sep + subfolder

    return replay_directory


def fetch_and_print(slippi_file, user_code, quiet=True, no_fetch=True, only_opp=True):
    """
    Grabs opponent connect code(s) from slippi_file,
    fetches player ranks/elo (requires internet),
    and prints/returns results.

    Not handling doubles replays yet (assuming 1 opponent)

    Needs to be updated to handle slippi_files which are streams (live games)
    or at least fail gracefully if not
    """
    try:
        opponent_codes = get_player_codes(slippi_file, quiet=quiet)
    except Exception as ex:
        print(f'\n\n~?~?~?~?~?~?{traceback.print_exc()}\n{ex}\n')
        print('Error getting opponent codes\n\n')
        return None 

    if not opponent_codes:
        # game in progress probably, need to parse stream 
        return None
    if any(i.startswith('CPU') for i in opponent_codes):
        return [i for i in opponent_codes if i.startswith('CPU')][0]
    if any(i.startswith('Offline') for i in opponent_codes):
        return 'Offline game'
    
    opponent_codes = [code for code in opponent_codes 
                      if code not in [user_code, 'CPU']]

    if not no_fetch:
        rank = get_single_rank(opponent_codes[0], quiet=quiet)
        if not quiet:
            print(f'~~~~~~~~~ opp.\n{rank}\n~~~~~~~~~\n')
        
        if not only_opp:
            # this is extremely redundant even in cases when we want to
            # print our own rank. eventually needs attention
            user_rank = get_single_rank(user_code, quiet=quiet)
            if not quiet:
                print(f'~~~~~~~~~ user\n{user_rank}\n~~~~~~~~~\n\n')
        return rank
    
    return opponent_codes[0]


def get_most_recent_game(directory, quiet=True):
    """
    Replay filename format : Game_YYYYMMDDTHHMMSS.slp
    Ongoing/live games (streams) are also saved as slp,
    this doesn't check if it's a stream or not. 
    """

    if os.listdir() == []:
        return None

    if not quiet:
        print(f'Getting most recent game...')
        s = '\n\t'.join(i for i in os.listdir(directory)[-4:][::-1])
        print(f"\ndir :\n\t{s}\n\t...\n")

    slps = (os.path.join(directory, file) 
            for file in os.listdir(directory) if file.endswith('.slp'))
    slps = sorted(slps, key=getmtime)[::-1][0]

    return slps


def get_most_recent_game_list(directory, current_game, quiet=True):
    " Returns names of all files created after current_game "

    if os.listdir() == []:
        return None

    if not quiet:
        print(f'Getting most recent games...')
        s = '\n\t'.join(i for i in os.listdir(directory)[-4:][::-1])
        print(f"\ndir :\n\t{s}\n\t...\n")

    slps = (os.path.join(directory, file) for file in os.listdir(directory) 
            if file.endswith('.slp'))
    slps = sorted(slps, key=getmtime)[::-1]

    # could include the current game in case it was streaming before
    new_games = [slp for slp in slps if getmtime(slp) > getmtime(current_game)]
    return new_games
    

def print_opponents(opponents, quiet=False):
    "opponents -> str or [str,]"

    top = '\n~~~~~~~~~~~~~~ opp.\n'
    bottom = '\n~~~~~~~~~~~~~~\n'

    if isinstance(opponents, str):
        # single opponent
        print(f'{top}{opponents}{bottom}')
    else:
        # multiple opponents
        for opp in opponents:
            if opp:  
                print(f'{top}{opp}{bottom}\n')
            else:
                if not quiet:
                    print('~~~~~~~~~\n Streaming x_x \n~~~~~~~~~\n')


def print_and_prompt(opponent, quiet=False):
    "prints and prompts..."

    print_opponents(opponent, quiet=quiet)

    s = input('\n[q] Quit \
                \nPress enter to update ... \n')
    return s.lower()


def print_in_progress():

    s = input('\n~~~~~~~~~~~~~~~~~~ ・\n\
               \n Game in progress...\
               \n Press enter after game ends to update...\
               \n~~~~~~~~~~~~~~~~~~ ・\
               \n[q] Quit \n')
    return s.lower()