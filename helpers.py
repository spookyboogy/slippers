import sys
import os
from requests_html import HTMLSession
import slippi


def get_single_rank(player_hash_code, quiet=True):
    """
    write a different version for getting multiple ranks to avoid
    making unnecessary repeated session calls
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


def get_player_codes(slippi_file, quiet=True):
    """
    will have to figure out pathing stuff later
    hard coding paths till then
    """
    
    game = slippi.Game(slippi_file)
    players = [player for player in game.metadata.players if player]

    codes = []
    for p in range(len(players)):
        try:
            if not quiet:
                print(f'player {p}:\n{players[p]}')
                print(f'code = {players[p].netplay.code}')
                print('~~~~~~~~\n')
            codes += [players[p].netplay.code]
        except Exception as ex:
            print(ex)
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
    
    # cwd = os.getcwd()
    # username = os.getlogin()
    user_home = os.path.expanduser('~')
    default_location = os.path.join('Documents','Slippi')
    default_directory = f"{user_home}{os.sep}{default_location}"

    if not quiet:
        print(f'Working in : {os.getcwd()}')
        print(f'Default replay directory : {default_directory}\n')

    if testing:
        # this is set to whatever directory I'm using it in,
        # change it to your own to skip the directory prompt.
        # this should eventually change to default to the 
        # directory where slippers is located, so that it uses the 
        # provided test.slp's 
        replay_directory = default_directory

        if not quiet:
            print(f'\nUsing : {replay_directory}\n')
        return replay_directory

    # prompt user
    print(f"Enter the path to your replay directory.\
          \nThe default is usually '{default_directory}'...")
    path = sys.stdin.readline().strip('\n')

    if path:
        replay_directory = path
    else:
        replay_directory = default_directory

    print(f'Using : {replay_directory}\n')

    return replay_directory


def fetch_and_print(slippi_file, user_code, quiet=True, no_fetch=True, only_opp=True):
    """
    Grabs opponent connect code(s) from slippi_file,
    fetches player ranks/elo (requires internet),
    and prints/returns results.

    Not handling doubles replays yet (assuming 1 opponent)
    """

    opponent_codes = get_player_codes(slippi_file, quiet=quiet)
    opponent_codes = [i for i in opponent_codes if i != user_code]

    if not opponent_codes:
        print('No opponents found')
        return 

    if not no_fetch:
        rank = get_single_rank(opponent_codes[0], quiet=quiet)
        if not quiet:
            print(f'~~~~~~~~~ opp.\n{rank}\n~~~~~~~~~\n')
        
        if not only_opp:
            user_rank = get_single_rank(user_code, quiet=quiet)
            if not quiet:
                print(f'~~~~~~~~~ user\n{user_rank}\n~~~~~~~~~\n\n')
        return rank
    
    return opponent_codes[0]


def get_most_recent_game(directory):

    games = [os.path.join(directory, file) 
            for file in os.listdir(directory) if file.endswith('.slp')]
    games = sorted(games, key=os.path.getmtime)[::-1]
    res = games[0]
    return res
