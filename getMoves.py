import csv
from pathlib import Path


class moves:
    '''everything to do with fetching the data about a character's moves'''

    def get_all_moves_dict(character):
        '''combines a character name with a file suffix and extension (must match file case)

        :param character: Name of character (capitalised first letter)
        :return: csv
        '''
        root_dir = Path(__file__).resolve().parent.parent
        try:
            file_name = root_dir / 'sf6comboCalculator' / 'CSVs' / f'{character}_moves.csv'
        except Exception as e:
            print(f'Failed to get file_name: {e}')

        move_types = set()

        try:
            with open(file_name, 'r') as csv_file:
                all_moves_data = {}
                reader = csv.DictReader(csv_file, delimiter=',')
                if character == 'Jamie':
                    for row in reader:
                        all_moves_data[row['Move']] = {
                            'Move': str(row['Move']), #name of move
                            'Move type': str(row['Move type']), #type of move
                            'Drink level': list([int(value) for value in row['Drinks'].split(',')]), #list of numbers
                            'Damage': int(row['Damage']),  # Damage value
                            'Counts as': int(row['Counts as (hits)']),  # Counts as hits
                            'Next hit': str(row['Next hit']), # If the move hits more than once and each hit is considered a different instance for scaling purposes
                            'Scaling route': float(row['Scaling route']),  # Scaling route
                            'Next scaling': float(row['Next move scaling']),  # Next move scaling
                            'Immediate scaling': float(row['Immediate scaling']),  # Immediate scaling
                            'Min scaling': float(row['Min scaling']),  # Minimum scaling
                            'Counter Hit': float(row['Counter Hit']),
                            'Punish Counter': float(row['Punish Counter']),
                            'Super gain': int(row['Super gain']),
                            'Drive gain': float(row['Drive gain']),
                            'Visible?': str(row['Visible?'])
                        }
                        move_types.add(row['Move type'])
                else:
                    for row in reader:
                        all_moves_data[row['Move']] = {
                            'Move': str(row['Move']),#name of move
                            'Move type': str(row['Move type']) #name of move
,                           'Damage': int(row['Damage']),  # Damage value
                            'Counts as': int(row['Counts as (hits)']),  # Counts as hits
                            'Next hit': str(row['Next hit']), # If the move hits more than once and each hit is considered a different instance for scaling purposes
                            'Scaling route': float(row['Scaling route']),  # Scaling route
                            'Next scaling': float(row['Next move scaling']),  # Next move scaling
                            'Immediate scaling': float(row['Immediate scaling']),  # Immediate scaling
                            'Min scaling': float(row['Min scaling']),  # Minimum scaling
                            'Counter Hit': float(row['Counter Hit']),  # Counter multiplier
                            'Punish Counter': float(row['Punish Counter']),
                            'Super gain' : int(row['Super gain']),
                            'Drive gain': int(row['Drive gain']),
                            'Visible?': str(row['Visible?'])
                        }
                        move_types.add(row['Move type'])
            move_types = sorted(list(move_types))
            return all_moves_data,move_types

        except FileNotFoundError:
            print(f"File {file_name} not found.")
        except KeyError as e:
            print(f"Missing column in file: {e}")
        #except ValueError as e:
         #   print(f"Invalid value encountered: {e}")
        except TypeError as e:
             print(f"Wrong data type: {e}")

    # def get_moves(character, file_name, move_type, jamie_dl):
    #     '''takes a file name as an argument, opens that file and returns a list of all the moves in the file
    #
    #     :param file_name: the file name to be opened
    #     :return: a list of moves available in that file
    #     '''
    #     # create an empty list for moves
    #     # tries to read the file passes as an argument and create a list named moves based on all the entries in the 'Move' column
    #
    #     try:
    #         with open(file_name, 'r') as csv_file:
    #             reader = csv.DictReader(csv_file, delimiter=',')
    #             moves = []
    #             if character == 'Jamie':  # and jamie_dl == int:
    #                 for row in reader:
    #                     if (row['Visible?'] == 'Yes') & (row['Move type'] in move_type):
    #                         moves.append(row['Move'])
    #             else:
    #                 for row in reader:
    #                     if (row['Visible?'] == 'Yes') & (row['Move type'] in move_type):
    #                         moves.append(row['Move'])
    #         return moves
    #
    #     except Exception as e:
    #         print(f'error reading file: {e} in get_moves')

    def get_selected_moves_data(all_moves_data, selected_moves):
        '''takes a file name and a list of moves as arguments. Returns a dictionary containing each move in the provided list and the additional data related to it

        :param file_name: the file name to be opened, should be the same as the file in get_moves
        :param selected_moves: the moves the user has selected in their combo
        :return: a dictionary of all data related to selected moves
        '''
        # create an empty dictionary for selected moves
        selected_data = []
        # tries to read the file passes as an argument and create a dictionary named selected_data based on moves selected by the user
        try:
            if selected_moves:
                for move in enumerate(selected_moves):
                    if move[1] in all_moves_data:
                        if all_moves_data[move[1]]['Next hit'] != 'None':
                            selected_moves.insert(move[0] + 1, all_moves_data[move[1]]['Next hit'])
            for move in selected_moves:
                if move in all_moves_data:
                    selected_data.append(all_moves_data[move])

        except KeyError as e:
            print(f"Missing column in file: {e}")
        except ValueError as e:
            print(f"Invalid value encountered: {e}")
        except TypeError as e:
             print(f"Wrong data type: {e}")
        return selected_data