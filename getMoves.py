import csv
from pathlib import Path


class moves:
    '''everything to do with fetching the data about a character's moves'''


    def get_character(character):
        '''combines a character name with a file suffix and extension (must match file case)

        :param character: Name of character (capitalised first letter)
        :return: csv
        '''
        root_dir = Path(__file__).resolve().parent.parent
        try:
            file_name = root_dir / 'sf6comboCalculator' / 'CSVs' / f'{character}_moves.csv'
            return file_name
        except Exception as e:
            print(f'Failed to get file_name: {e}')

    def get_moves(file_name,move_type):
        '''takes a file name as an argument, opens that file and returns a list of all the moves in the file

        :param file_name: the file name to be opened
        :return: a list of moves available in that file
        '''
        # create an empty list for moves
        # tries to read the file passes as an argument and create a list named moves based on all the entries in the 'Move' column



        try:
            with open(file_name, 'r') as csv_file:
                print(move_type)
                reader=csv.DictReader(csv_file,delimiter=',')
                moves = []
                for row in reader:
                    if (row ['Visible?'] == 'Yes') & (row ['Move type'] == move_type):
                        moves.append(row['Move'])
                print(moves)
            return moves

        except Exception as e:
            print(f'error reading file: {e} in get_moves')

    def get_selected_moves_data(file_name, selected_moves):
        '''takes a file name and a list of moves as arguements. Returns a dictionary containing each move in the provided list and the additional data related to it

        :param file_name: the file name to be opened, should be the same as the file in get_moves
        :param selected_moves: the moves the user has selected in their combo
        :return: a dictionary of all data related to selected moves
        '''
        #create an empty dictionary for selected moves
        selected_data = []
        # tries to read the file passes as an argument and create a dictionary named selected_data based on moves selected by the user

        def fetch_move_data(move,reader):
            for row in reader:
                if row ['Move'] == move:
                    selected_data.append({
                        'Move' : move,
                        'Damage': int(row['Damage']),  # Damage value
                        'Counts as': int(row['Counts as (hits)']),  # Counts as hits
                        'Next hit': str(row['Next hit']),  #If the move hits more than once and each hit is considered a different instance for scaling purposes
                        'Scaling route': float(row['Scaling route']),  # Scaling route
                        'Next scaling': float(row['Next move scaling']),  # Next move scaling
                        'Immediate scaling': float(row['Immediate scaling']),  # Immediate scaling
                        'Min scaling': float(row['Min scaling']),  # Minimum scaling
                        'Counter multiplier':float(row['Counter multiplier']), #Counter multiplier
                        'Punish multiplier':float(row['Punish multiplier']),
                        'Drive gain':float(row['Drive gain']),
                        'Visible?': str(row['Visible?'])
                    })
                    next_hit = row['Next hit'].strip()
                    if next_hit != 'None':
                        fetch_move_data(next_hit, reader)
        try:
            with open(file_name, 'r') as csv_file:
                reader = list(csv.DictReader(csv_file, delimiter=','))  # Convert to a list for multiple iterations
                if selected_moves:
                    for move in selected_moves:
                        fetch_move_data(move, reader)
        except FileNotFoundError:
            print(f"File {file_name} not found.")
        except KeyError as e:
            print(f"Missing column in file: {e}")
        except ValueError as e:
            print(f"Invalid value encountered: {e}")
        except TypeError as e:
            print(f"Wrong data type: {e}")
        return selected_data