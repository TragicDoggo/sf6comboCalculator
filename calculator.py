import math
import re

class comboCalculator:

    def comboCalculatorFunc(selectedMoves,state):
        '''calculator function which takes a dictionary of all selected moves, and calculates the overall damage of the combo

        :param selectedMoves: a dictionary of the selected moves
        :param counter: the counter multiplier, usually 1.5 for counter/punish counter
        :param move_cancelled: a bool which should be true if the last move was SA3 or CA and was cancelled into from a special
        :param pp_multiplier: a float which should either be 1 or .5. If a combo was performed following a perfect parry, the damage is halved
        '''
        #variables from ui
        counter = state['counter']
        move_cancelled = state['cancelled_special']

        #jamie stuff
        jamie_drink_level = state['character_specifics']['Jamie']
        jamie_multiplier_list = [0.9, 0.95, 1, 1.05, 1.1]
        jamie_scaling = jamie_multiplier_list[jamie_drink_level]

        # scaling index is where in the scaling route the combo starts (always starts at 0)
        scaling_index = 0
        # 1 until drc is used
        drc_multiplier = 1
        # additional scaling multiplier based on things like wall splat and perfect parry
        additional_multiplier = 1.0
        # increases or decreases depending on whether the move has special scaling properties leading to a flat scaling increase
        additional_scaling = 0
        # total damage done during the combo
        combo_damage = 0
        # additional damage dealt by other factors (such as poison)
        additional_damage = 0
        # drive gauge starting value
        drive_gauge = 60000
        # bool to track whether player can gain drive
        can_gain_drive = True
        # check if combo starts with DI wall-splat
        scaling_modifiers = {
            'perfect parry' :[state['perfect_parry'], 0.5],
            'wall splat' : [False, 0.8],
        }
        #scaling routes
        scaling_100 = [1, 1, .8, .7, .6, .5, .4, .3, .2, .1, .1, .1, .1]
        scaling_90 = [1, .9, .8, .7, .6, .5, .4, .3, .2, .1, .1, .1]
        scaling_85 = [1, .85, .75, .65, .55, .45, .35, .25, .15, .1, .1, .1]
        scaling_80 = [1, .8, .7, .6, .5, .4, .3, .2, .1, .1, .1, .1]
        scaling_75 = [1, .75, .65, .55, .45, .35, .25, .15, .1, .1, .1, .1]
        scaling_70 = [1, .7, .6, .5, .4, .3, .2, .1, .1, .1, .1, .1]
        scaling_60 = [1, .6, .5, .4, .3, .2, .1, .1, .1, .1, .1, .1]

        #list of routes
        scaling_routes_list = [scaling_60,scaling_70,scaling_75,scaling_80,scaling_85,scaling_90, scaling_100]

        combo_data = []
        #combo_data = {'Move name':[],'Final damage': [],'Final scaling': [],'Route scaling': [],'Drive Rush scaling': [],'Counts as x hits': [],'Immediate scaling': [],'Next move scaling': [],'Raw damage': [],'Combo damage': [],'Drive gain': []}

        #get first entry in selectedMoves
        if selectedMoves:
            first_move = next(iter(selectedMoves))
            first_move_data = selectedMoves[0]
        else:
            return combo_damage,combo_data, drive_gauge

        #iterate through all scaling routes and return the route where the second index is equal to the scaling route value in the first move dictionary
        for route in scaling_routes_list:
            if route[1] == first_move_data['Scaling route']:
                scaling_route = route
        #for each move in the selectedMoves, start by resetting instance damage to 0

        if re.match(r'Drive Impact Wall Splat .blocked.',first_move_data['Move'],):
            scaling_modifiers['wall splat'][0] = True

        for modifier in scaling_modifiers.values():
            if modifier[0]:
                additional_multiplier = additional_multiplier * modifier[1]


        for move_data in selectedMoves:
            if scaling_index > len(scaling_route)-1:
                scaling_index = len(scaling_route)-2
            route_scaling = scaling_route[scaling_index]
            damage = 0
            move = move_data['Move']
            #update additional scaling with any immediate scaling changes
            additional_scaling = additional_scaling + move_data['Immediate scaling']
            #if an SA3 or CA was cancelled from a special, the additional scaling is increased
            if move_cancelled and (move == 'CA' or move == 'SA3' or move == 'Raging Demon'):
                additional_scaling = additional_scaling -.1
            # check if the move is drc
            elif re.match(r'Drive Rush',move) and scaling_index > 0:
                drc_multiplier = 0.85
                can_gain_drive = False
            #calculate scaling for this hit based on current index of the scaling route, any additonal scaling, the drc multiplier and perfect parry multiplier
            instance_scaling = math.floor(((scaling_route[scaling_index] + additional_scaling) * additional_multiplier * drc_multiplier * jamie_scaling)*100)/100
            #check whether the current move has any minimum scaling which should be used instead
            if instance_scaling > move_data['Min scaling']:
                final_scaling = instance_scaling
                super_override = False
            else:
                final_scaling = move_data['Min scaling']
                super_override = True
            #finally multiply damage by final scaling figure
            damage = move_data['Damage'] * final_scaling
            #hits_left = hits_left - 1
            #if it is the first move in the combo, multiply the damage for this hit by the counter multiplier
            if scaling_index == 0:
                if counter == 'Counter':
                    damage = damage * move_data['Counter multiplier']
                elif counter == 'Punish Counter':
                    damage = damage * move_data['Punish multiplier']
            #increase the scaling index by the number of hits the damage instance counts as. A move may only hit once but can count as more hits in the game
            scaling_index = scaling_index + move_data['Counts as']
            #update the total damage so far
            combo_damage = math.floor(combo_damage + damage)
            #update additional scaling with any scaling which applies to next move
            additional_scaling = additional_scaling + move_data['Next scaling']
            # only OD moves cost -20000 drive, and using one means the player can gain drive again
            if move_data['Drive gain'] == -20000:
                can_gain_drive = True
            if can_gain_drive or move_data['Drive gain'] < 0:
                drive_gauge = drive_gauge + move_data['Drive gain']
            if drive_gauge > 60000:
                drive_gauge = 60000
            elif drive_gauge < 0:
                drive_gauge = 0
            current_move_dict = {
                'Move name':move,
                'Final damage':damage,
                'Final scaling':final_scaling,
                'Route scaling':route_scaling,
                'Drive Rush scaling':drc_multiplier,
                'Counts as x hits':move_data['Counts as'],
                'Immediate scaling':move_data['Immediate scaling'],
                'Next move scaling':move_data['Next scaling'],
                'Raw damage':move_data['Damage'],
                'Combo damage':combo_damage,
                'Drive gain':move_data['Drive gain']
                }
            combo_data.append(current_move_dict)

            combo_damage = combo_damage + additional_damage



        return combo_damage, combo_data, drive_gauge