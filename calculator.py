import math
import re

class comboCalculator:

    def comboCalculatorFunc(selectedMoves,state):

        def checkWallsplat(selected_moves):
            '''
            Checks whether the first move in the selected moves is a blocked drive impact wall splat and returns true or false depending
            :param selected_moves:
            :return True or False:
            '''
            if selected_moves:
                if re.match(r'Drive Impact Wall Splat .blocked.', selected_moves[0]['Move']):
                    return True
                else:
                    return False
            else:
                return False

        def jamieMultiplier(state):
            '''
            Returns a multiplier value based on what drink level Jamie is at as selected by the user.
            :param state: pull the state to access Jamie's drink level as selected by the user (between 0 and 4)
            :return jamie_multiplier_list[jamie_drink_level] (float): the value in the jamie_multiplier_list on the index of the selected drink level
            '''
            if state['character'] == 'Jamie':
                jamie_drink_level = state['character_specifics']['Jamie']
                jamie_multiplier_list = [0.9, 0.95, 1, 1.05, 1.1]
                return jamie_multiplier_list[jamie_drink_level]
            else:
                return 1

        def workOutStartingMultiplier(state,selected_moves):
            '''
            Set additional_multiplier to 1, then check for other modifiers which would affect the additional multiplier such as perfect parry or character specific things
            Then return the final value
            :param state: access multiple parameters
            :param selected_moves: list of moves selected by the user
            :return multiplier: a value of 1.0 or less
            '''

            multiplier = 1.0
            scaling_modifiers = {
                'perfect parry': [state['perfect_parry'], 0.5],
                'wall splat': [checkWallsplat(selected_moves), 0.8],
                'kim buff' : [state['character_specifics']['Kimberly'], 1.1114]
            }
            for modifier in scaling_modifiers.values():
                if modifier[0]:
                    multiplier = multiplier * modifier[1]
            return multiplier

        def calculateScaling(move, scaling_index, additional_multiplier,scaling_route,drc_multiplier,additional_scaling,jamie_multiplier,state):
            additional_scaling = additional_scaling + move['Immediate scaling']
            if state['cancelled_special'] and (move['Move'] == 'CA' or move['Move'] == 'SA3' or move['Move'] == 'Raging Demon'):
                additional_scaling = additional_scaling -0.1
            if scaling_index > len(scaling_route)-1:
                 scaling_route_multiplier = 0.1
            else:
                scaling_route_multiplier = scaling_route[scaling_index] + additional_scaling
            move_scaling = additional_multiplier * scaling_route_multiplier * drc_multiplier * jamie_multiplier
            additional_scaling = additional_scaling + move['Next scaling']
            return move_scaling,additional_scaling

        def calculateDrive(move,can_gain_drive,drive_gauge):
            if can_gain_drive or move['Drive gain'] < 0:
                if drive_gauge > 0:
                    drive_gauge = drive_gauge + move['Drive gain']
            if drive_gauge > 60000:
                drive_gauge = 60000
            elif drive_gauge < 0:
                drive_gauge = 0
            return drive_gauge

        def calculateSuper(move,super_gauge):
            super_gauge = super_gauge + move['Super gain']
            if super_gauge > 30000:
                super_gauge = 30000
            elif super_gauge < 0:
                super_gauge = 0
            return super_gauge

        #Various multipliers and modifiers
        # scaling index is where in the scaling route the combo starts (starts at 0)
        scaling_index = -1
        #scaling for that specific instance (usually one move but can be multiple hits of a move)
        instance_scaling = 1
        # 1 until drc is used
        drc_multiplier = 1
        # additional scaling multiplier based on things like wall splat and perfect parry
        additional_multiplier = workOutStartingMultiplier(state, selectedMoves)

        jamie_multiplier = jamieMultiplier(state)
        # increases or decreases depending on whether the move has special scaling properties leading to a flat scaling increase
        additional_scaling = 0
        # bool to track whether player can gain drive
        can_gain_drive = True
        #a dictionary containing all possible base scaling routes
        scaling_routes_dict = {
                               1: [1, 1, .8, .7, .6, .5, .4, .3, .2, .1, .1, .1, .1],
                               0.9: [1, .9, .8, .7, .6, .5, .4, .3, .2, .1, .1, .1],
                               0.85: [1, .85, .75, .65, .55, .45, .35, .25, .15, .1, .1, .1],
                               0.8: [1, .8, .7, .6, .5, .4, .3, .2, .1, .1, .1, .1],
                               0.75: [1, .75, .65, .55, .45, .35, .25, .15, .1, .1, .1, .1],
                               0.7: [1, .7, .6, .5, .4, .3, .2, .1, .1, .1, .1, .1],
                               0.6: [1, .6, .5, .4, .3, .2, .1, .1, .1, .1, .1, .1],
                               0.5: [1, .5, .4, .3, .2, .1, .1, .1, .1, .1, .1, .1],
                               1.7: [1, 1, .7, .6, .5, .4, .3, .2, .1, .1, .1, .1],
                               1.55: [1, 1, .55, .45, .35, .25, .15, .1, .1, .1, .1, .1]
                               }

        counter_dict = {'None':'Damage',
                        'CH':'Counter Hit',
                        'PC':'Punish Counter'}

        #data to track for calculation and data display
        # total damage done during the combo
        combo_damage = 0
        # additional damage dealt by other factors (such as poison)
        additional_damage = 0
        #collects combo data for table
        combo_data = []


        #check if selectedMoves contains any data, if so, save the first move which contains a hit as first_move_data.
        if selectedMoves:
            first_move_data = None
            for move in selectedMoves:
                if move['Counts as'] > 0:
                    first_move_data = move
                    break
            if first_move_data == None: #If no move in the list contains a hit, the first move in the list is set as the first for the sake of drive gauge calculation etc
                first_move_data = selectedMoves[0]
        else:
            return combo_damage, combo_data, state['super_gauge'], state['drive_gauge'] #Else, just return default values for calculator

        #set the scaling route for this combo based on the first move
        scaling_route = scaling_routes_dict[first_move_data['Scaling route']]

        for move in selectedMoves:
            #Calculate damage:
            if re.match(r'Drive Rush', move['Move']) and scaling_index > -1: #check if move is drive rush
                drc_multiplier = 0.85 #set drc scaling for the rest of the combo
                can_gain_drive = False #disable drive gain
            if state['character'] == 'Jamie' and move['Move'] == 'SA2':
                jamie_multiplier = 1.15
            if move['Counts as'] > 0: #only increases scaling index and recalculates instance scaling if the move counts as a hit
                scaling_index = scaling_index + 1 #increase index by one by default
                scaling_data = calculateScaling(move, scaling_index, additional_multiplier,scaling_route,drc_multiplier,additional_scaling,jamie_multiplier,state) #calculate scaling
                instance_scaling = math.floor(scaling_data[0]*100)/100
                additional_scaling = scaling_data[1]
                scaling_index = scaling_index + move['Counts as'] - 1 #increase index again if move counts as more than one hit in combo
            if move['Min scaling'] > instance_scaling:
                instance_scaling = move['Min scaling']
            if scaling_index < 1:
                move_damage = move[counter_dict[state['counter']]]
            else:
                move_damage = move['Damage']
            instance_damage = math.floor(move_damage * instance_scaling)
            combo_damage = combo_damage + instance_damage
            if move['Move type'] == 'Overdrive':
                can_gain_drive = True
            state['drive_gauge'] = calculateDrive(move,can_gain_drive,state['drive_gauge'])
            state['super_gauge'] = calculateSuper(move, state['super_gauge'])
            current_move_dict = {
                'Move name':move['Move'],
                'Scaled damage':instance_damage,
                'Final scaling':instance_scaling,
                'Counts as (hits)':move['Counts as'],
                'Immediate scaling':move['Immediate scaling'],
                'Next move scaling':move['Next scaling'],
                'Raw damage':move['Damage'],
                'Combo damage':combo_damage,
                'Drive gain':move['Drive gain'],
                'Super gain':move['Super gain']
            }
            combo_data.append(current_move_dict)

        return combo_damage, combo_data, state['super_gauge'], state['drive_gauge']