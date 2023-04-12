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
        print(f'\nuser code : {user_code}\n')

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
        replay_directory = f"{user_home}\\Desktop\\CS\\slippers"
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


def fetch_and_print(slippi_file, quiet=True, no_fetch=True, only_opp=True):
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


def test_run():

    test_files = [os.path.join(replay_directory, file) 
                for file in os.listdir(replay_directory) if file.endswith('.slp')]

    for test_file in test_files:
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ・')
        fetch_and_print(test_file, quiet=quiet, no_fetch=no_fetch)


def main(directory, quiet=False, testing=False, no_fetch=False):

   
    # Testing april's games, make a way to optionally select month subfolder
    directory += os.sep + "2023-04"
    
    most_recent_game = get_most_recent_game(directory)
    most_recent_opponent = fetch_and_print(most_recent_game, 
                                           quiet=True, no_fetch=no_fetch)
    while True:
        
        os.system("cls" if os.name == "nt" else "clear")
        print(f'~~~~~~~~~ opp.\n{most_recent_opponent}\n~~~~~~~~~\n')
        print('Press enter to update...')
        input()

        most_recent_check =  get_most_recent_game(directory)

        if most_recent_game != most_recent_check:
            most_recent_game = most_recent_check
            most_recent_opponent_check = fetch_and_print(most_recent_game, 
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

    main(replay_directory, quiet=quiet, testing=testing, no_fetch=no_fetch)
    

# # Write modes for displaying a custom amount of .slp's 
# # ie, maybe we only want the ranks from the past session, or maybe we want
# # the whole month. Or, maybe we only want the most recent player, 
# # or current/live player, if this script can run as a dolphin hook.
# # Or, a "--More--"-like tool which goes through the n most recent opponents
