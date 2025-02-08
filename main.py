from nicegui import ui
from getMoves import moves as m
from calculator import comboCalculator as cc
import os
import re
import uuid
import math
import pandas as pd


@ui.page('/')
def main_page():
    state = {
        # variables for loading moves
        'file_name': '',
        'all_moves': {},
        'available_moves':[],
        'move_list': [],
        'selected_chips': {},
        'chips_selected':False,
        'character': 'None',
        'move_types':[],
        #variables for calculating damage/scaling/drive gauge
        'counter': 'None',
        'perfect_parry': False,
        'cancelled_special': False,
        'final_damage': 0,
        'additional_damage': 0,
        'drive_gauge': 60000.0,
        'super_gauge': 30000.0,
        #combo_data contains  cleaned up data for the calculation per-move
        'combo_data': [{'Move name': None, 'Final damage': None, 'Final scaling': None, 'Route scaling': None,
                        'Drive Rush scaling': None, 'Counts as x hits': None, 'Immediate scaling': None,
                        'Next move scaling': None, 'Raw damage': None, 'Combo damage': None, 'Drive gain': None}],
        #combo_storage will store key information about a combo when it is saved so it can be restored later by the user
        'combo_storage': {},
        # string storing svg data for the drive gauge to update
        'drive_gauge_svg': '''
                            <svg viewBox="0 0 770 35" width="220" height="10" xmlns="http://www.w3.org/2000/svg">
                            <style>
                                .s6 { fill: #b3b816;stroke: #ebec24;stroke-miterlimit:100;stroke-width: 5 } 
                                .s5 { fill: #a7b919;stroke: #e7f035;stroke-miterlimit:100;stroke-width: 5 } 
                                .s4 { fill: #8fb11c;stroke: #d0ee36;stroke-miterlimit:100;stroke-width: 5 } 
                                .s3 { fill: #88b713;stroke: #b9e724;stroke-miterlimit:100;stroke-width: 5 } 
                                .s2 { fill: #56b70f;stroke: #90eb2e;stroke-miterlimit:100;stroke-width: 5 } 
                                .s1 { fill: #3eb30d;stroke: #63e523;stroke-miterlimit:100;stroke-width: 5 } 
                                .s7 { opacity: .7;fill: #000000;stroke: #000000;stroke-miterlimit:100;stroke-width: 4 } 
                            </style>
                            <g id="Empty" style="opacity: .7">
                                <path id="Empty" class="s7" d="m4 3.1h90.6l20.4 30.8h-89.5zm113 0h90.6l20.4 30.7h-89.5zm114 0h90.7l20.3 30.7h-89.4zm111 0h90.6l20.4 30.7h-89.5zm111 0h90.6l20.4 30.8h-89.5zm111 0h90.6l20.4 30.7h-89.5z"/>
                            </g>
                            <g id="Drive Gauge">
                            {
                            <path id="Bar 6" class="s6" d="m4 3.1 h90.6 l20.4 30.8 h-89.5 z"/>
                            <path id="Bar 5" class="s5" d="m117 3.1 h90.6 l20.4 30.8 h-89.5 z"/>
                            <path id="Bar 4" class="s4" d="m231 3.1 h90.6 l20.4 30.8 h-89.5 z"/>
                            <path id="Bar 3" class="s3" d="m342 3.1 h90.6 l20.4 30.8 h-89.5 z"/>
                            <path id="Bar 2" class="s2" d="m453 3.1 h90.6 l20.4 30.8 h-89.5 z"/>
                            <path id="Bar 1" class="s1" d="m564 3.1 h90.6 l20.4 30.8 h-89.5 z"/>
                            }
                             </g>

                            </svg>
                            ''',
        # string storing svg data for the drive gauge to update
        'super_gauge_svg': '''
                          <svg viewbox ='0 0 700 70' width=352 height=60 xmlns="http://www.w3.org/2000/svg"> 
                              <defs>
                                <filter id="blur1">
                                      <feGaussianBlur stdDeviation="1.5" in="SourceGraphic"/>
                                </filter>
                                <filter id="blur2">
                                      <feGaussianBlur stdDeviation="1" in="SourceStroke"/>
                                </filter>
                                <linearGradient id="grad1" x1="0%" x2="100%" y1="0%" y2="0%">
                                  <stop offset="0.2" stop-color="#ffffff" stop-opacity=".9"/>                                
                                  <stop offset="0.5" stop-color="#ffffff" stop-opacity=".2"/>
                                  <stop offset="0.8" stop-color="#ffffff" stop-opacity=".9"/>
                                </linearGradient>
                                <linearGradient id="grad2" x2="1">
                                  <stop offset="0.5" stop-color="#ce207a"/>
                                  <stop offset="1" stop-color="#ffd4ff"/>
                                </linearGradient>
                                <linearGradient id="grad3" x2="1">
                                  <stop offset="0.2" stop-color="#ce207a"/>
                                  <stop offset="0.5" stop-color="#ffd4ff"/>
                                  <stop offset="0.8" stop-color="#ce207a"/>
                                </linearGradient> 
                              </defs>
                              <style>
                                .glow {filter: url(#blur1)}
                                .glow2 {filter: url(#blur2)}
                                .outline {stroke: url(#grad1)}
                              </style>
                              <g id="super bar">
                                <polygon id="bar glow" class="glow" fill="#ce207a" fill-opacity="30%" points="0,5 318,5 353,56 35,56"/>
                                <polygon id="bar background" fill="#grey" fill-opacity="30%" points="10,10 316,10 342,50 38,50"/>
                                <polygon id="bar filling" fill="url(#grad3)" points="10,10 316,10 342,50 38,50"/>
                                <polygon id="bar outline" stroke="url(#grad1)" stroke-width=2px fill='transparent' points="10,10 316,10 342,50 38,50"/>
                              </g>
                              </svg>
                        ''',
        # character UI colours and icons
        'char_custom_dict': {'None': ['#465261', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/None.png'],
                             'A.K.I.': ['#6b254b', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/A.K.I..png'],
                             'Akuma': ['#8e1f11', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Akuma.png'],
                             'Blanka': ['#036c03', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Blanka.png'],
                             'Cammy': ['#355f97', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Cammy.png'],
                             'Chun-Li': ['#6483de', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Chun-Li.png'],
                             'Dee Jay': ['#008b0c', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Dee Jay.png'],
                             'Dhalsim': ['#d7a403', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Dhalsim.png'],
                             'Ed': ['#086b7a', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Ed.png'],
                             'E.Honda': ['#a90600', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/E.Honda.png'],
                             'Guile': ['#316326', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Guile.png'],
                             'Jamie': ['#bc9c0e', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Jamie.png'],
                             'JP': ['#3c2a51', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/JP.png'],
                             'Juri': ['#601199', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Juri.png'],
                             'Ken': ['#bd1613', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Ken.png'],
                             'Kimberly': ['#fa77b7', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Kimberly.png'],
                             'Lily': ['#d78076', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Lily.png'],
                             'Luke': ['#4628c9', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Luke.png'],
                             'M.Bison': ['#61346d', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/M.Bison.png'],
                             'Manon': ['#796dc7', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Manon.png'],
                             'Marisa': ['#b90302', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Marisa.png'],
                             'Rashid': ['#cb7c1c', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Rashid.png'],
                             'Ryu': ['#863532', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Ryu.png'],
                             'Terry': ['#8e1b18', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Terry.png'],
                             'Zangief': ['#c91212', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Zangief.png']},
         # character specific variables
        'character_specifics': {'Jamie': 2,
                                'A.K.I.': 0,
                                'Kimberly' : False},
        'current_input' : '',
        'option_index' : -1,
        # faq term info
        'faq_tables': {'term_columns': [{'name': 'name', 'label': 'Name', 'field': 'name', 'sortable': False},
                                                {'name': 'meaning', 'label': 'Meaning', 'field': 'meaning',
                                                 'sortable': False}],
                       'move_term_rows': [
                            {'name': '[X] hit only', 'meaning': 'Only the X hit makes contact with the opponent'},
                            {'name': '[X] hits', 'meaning': 'Indicates the number of hits which make contact with the opponent, e.g. you may choose the 1 hit version of a move as the move can only be cancelled after the first hit'},
                            {'name': '> L/M/HK/P', 'meaning': 'The > symbol indicates a move was cancelled or a follow-up button was pressed, for example, 214K > K. However a move which starts with the > symbol must be preceded by a move which can cancel into it (e.g. Juri\'s 236MKHK > LK)'},
                            {'name': '1st hit/last hit', 'meaning': 'Ed\'s SA2 is odd because it doesn\'t deal all damage at once, instead it deals it over 7 hits. This means that if you hit an opponent with the first hit of the SA2, then use a DP which results in them landing on the ball again, the damage of the second hit scaling of the SA2 will be calculated based on the hit from the DP. Basically, you need to manually add the 7 hits of the SA2, taking note of how many times the opponent hits the ball between other attacks to get an accurate calculation!'},
                            {'name': 'air', 'meaning': 'The button combination is input in the air to perform the attack. For example, entering 214LK for a shoto on the ground would result in a Tatsu, in the air it would result in an Air Tatsu'},
                            {'name': 'airborne opponent', 'meaning': 'Version of that move which is performed when the opponent is airborne'},
                            {'name': 'basic/OD/SA1 charge', 'meaning': 'The type of charge used to activate the Blanka-chan doll'},
                            {'name': 'blocked', 'meaning': 'Version of that move which occurs when the attack is blocked by the opponent'},
                            {'name': 'burst', 'meaning': 'The move bursts the bubble of A.K.I.\'s Nightshade Pulse, as opposed to the bubble hitting the opponent and then the whip follow up hitting them'},
                            {'name': 'cancelled/cancel', 'meaning': 'The move is cancelled, sometimes into a specific move. Changes the damage and other properties'},
                            {'name': 'charge lv[X]', 'meaning': 'The button is held down to produce a more powerful version of the move. The longer the button is held, the higher the charge level. Charge moves don\'t usually have more than 3 levels: the base attack, level 2 charge and level 3 charge'},
                            {'name': 'close/far/mid', 'meaning': 'How close the character is to the opponent, changing the move\'s properties or which move is performed'},
                            {'name': 'counter', 'meaning': 'The move absorbs a hit from the opponent, triggering the counter version of the move'},
                            {'name': 'cross-up', 'meaning': 'Used when the move moves to the other side of the opponent, or crosses-up'},
                            {'name': 'crouching opponent', 'meaning': 'Opponent is in a crouched state when the move hits'},
                            {'name': 'delayed hit', 'meaning': 'Indicates that the first part of the move (maybe only the first active frame) whiffs leading to different properties'},
                            {'name': 'denjin charge', 'meaning': 'Uses a denjin charge when performed'},
                            {'name': 'detonate bomb', 'meaning': 'Manually trigger the explosion of the planted mine/bomb with this move'},
                            {'name': 'drink', 'meaning': 'Jamie drinks after the move'},
                            {'name': 'early/late', 'meaning': 'The timing of the move in the combo'},
                            {'name': 'Enhanced', 'meaning': 'Version of the move performed when the character has resources which enhance that move, e.g. Juri Fuha stocks or Honda Sumo Spirit'},
                            {'name': 'hold', 'meaning': 'Version of the move which is performed when the attack button is held after completing the motion'},
                            {'name': 'install', 'meaning': 'A version of the move performed when the character is in an "install" state, such as Juri, Blanka or Guile\'s SA2'},
                            {'name': 'level [X]', 'meaning': 'Indicates how many medals Manon has'},
                            {'name': 'non-cinematic', 'meaning': 'When a Super\'s first hit misses it leads to a version of the move where the cinematic doesn\'t play and the damage is reduced'},
                            {'name': 'perfect', 'meaning': 'Perfect timing for a charge move or a move which requires holding a button'},
                            {'name': 'secret', 'meaning': 'A secret move (unlocked via letting a long taunt play out)'},
                            {'name': 'timer expired', 'meaning': 'For moves which plant a bomb or mine, which will deal damage after a certain time. This move should be used at the point in the combo where the bomb/mine etc explodes due to the timer running out instead of manually triggering it'},
                            {'name': 'toxic blossom', 'meaning': 'The move triggers the Toxic Blossom effect on a poisoned opponent, dealing additional damage'},
                            {'name': 'whiff [X]', 'meaning': 'Indicates that part of the move missed the opponent, leading to different properties'},
                            {'name': 'wind', 'meaning': 'Move is enhanced with an air current'}
                                          ],
                       'data_term_rows': [
                            {'name': 'Move name', 'meaning': 'Inputs of the move'},
                            {'name': 'Scaled damage', 'meaning': 'Damage of the move after scaling has been applied'},
                            {'name': 'Final scaling', 'meaning': 'Scaling applied to the move after calculations have been performed'},
                            {'name': 'Counts as (hits)', 'meaning': 'Number of hits the move counts as in the combo. Most moves count as 1 and only increase the scaling by 1 level, but some count as more than 1 which means the moves following have increased scaling applied to them'},
                            {'name': 'Immediate scaling', 'meaning': 'Additional scaling applied to the move immediately'},
                            {'name': 'Next move scaling', 'meaning': 'Additional applied to the move following this one'},
                            {'name': 'Raw damage', 'meaning': 'Damage of the move before scaling is applied'},
                            {'name': 'Combo damage', 'meaning': 'Total damage in the combo up to this point'},
                            {'name': 'Drive gain', 'meaning': 'How much drive the character gains (or loses) from this move'},
                            {'name': 'Super gain', 'meaning': 'How much Super meter the character gains (or loses) from this move'}]
                       }
    }

    # set ui defaults
    ui.colors()
    dark = ui.dark_mode()
    ui.colors(primary='#465261',dark='#121212')
    ui.card.default_style('width: 250px; height: 220px')

    def characterSpecificStuff(state):

        def changeAkiPoison(slider_value, label,state):
            state['additional_damage'] = math.floor(slider_value * 60)
            poison_text = state['additional_damage']
            label.set_text(f'Poison damage: {poison_text}')
            calculateData(state)

        def changeJamieScaling(radio_value,state):
            state['character_specifics']['Jamie'] = radio_value
            filterMoves(move_type_toggle.value,state)
            calculateData(state)

        def kimBuff(toggle_value,state):
            state['character_specifics']['Kimberly'] = toggle_value
            calculateData(state)

        char_specific_row.clear()
        if state['character'] == 'Jamie':
            with char_specific_row:
                ui.select(label='Drink level', options=[0, 1, 2, 3, 4], value=state['character_specifics']['Jamie'],on_change=lambda e: changeJamieScaling(e.value,state)).style('width: 100px')

        elif state['character'] == 'A.K.I.':
            with char_specific_row:
                ui.label('Estimated seconds poisoned:').style('height: 40px')
                poison = ui.slider(min=0.0, max=10.0, step=0.1, value=0).props('label-always').on('update:model-value',lambda e: changeAkiPoison(e.args, poison_label,state),throttle=1.0, leading_events=False)
                poison_label = ui.label('Poison damage: 0')

        elif state['character'] == 'Kimberly':
            with char_specific_row:
                ui.checkbox('SA3 buff enabled',value=state['character_specifics']['Kimberly'], on_change= lambda e: kimBuff(e.value,state))
        else:
            with char_specific_row:
                ui.label('No character specific options available')

    def characterSelected(state, selected_character):
        move_dropdown.set_value(None)
        state['character'] = selected_character
        state['additional_damage'] = 0
        state['character_specifics']['Jamie'] = 2
        get_all_moves_data = m.get_all_moves_dict(selected_character)
        state['all_moves'] = get_all_moves_data[0]
        state['move_types'] = get_all_moves_data[1]
        move_type_toggle.set_options(state['move_types'])
        move_type_toggle.set_value(state['move_types'])
        clearList(state)
        ui.colors(primary=state['char_custom_dict'][state['character']][0]).update()
        character_portrait.set_source(state['char_custom_dict'][selected_character][1])
        character_label.set_content(f'###### **{selected_character}**')
        characterSpecificStuff(state)
        filterMoves(state['move_types'],state)
        return selected_character

    def filterMoves(value,state):
        state['available_moves'] = []
        if value == []:
            state['available_moves'] = list(state['all_moves'].keys())
        else:
            for move in state['all_moves'].keys():
                if state['all_moves'][move]['Move type'] in value and state['all_moves'][move]['Visible?'] == 'Yes':
                    if state['character'] == 'Jamie':
                        if state['character_specifics']['Jamie'] in state['all_moves'][move]['Drink level']:
                            state['available_moves'].append(move)
                    else:
                            state['available_moves'].append(move)
        move_dropdown.set_options(state['available_moves'])

    def selectInput(current_key):
        current_move = None
        blocked_keys = ['Enter','ArrowDown','ArrowUp','ArrowRight','ArrowLeft','Tab']
        if current_key not in blocked_keys:
            move_dropdown.run_method('setOptionIndex', 0)

    def createChip(name,selected,state):
        if name:
            try:
                move_type = state['all_moves'][name]['Move type']
                # Default color
                colour = 'blue-grey-5'
                colours_keywords = {
                    'Overdrive': 'orange-4',  # OD moves
                    'Super': 'deep-orange-6',  # Supers
                    'Drive': 'light-green-6'  # Drive gauge stuff
                }
                colours_regex = {
                    re.compile(r'\d.*L[KP]'): 'light-blue-11',  # Lights
                    re.compile(r'\d.*M[KP]'): 'amber-4',  # Mediums
                    re.compile(r'\d.*H[KP]'): 'red-5',  # Heavies
                }
                if move_type in colours_keywords.keys():
                    colour = colours_keywords[move_type]
                else:
                    for pattern, pattern_colour in colours_regex.items():
                        if pattern.match(name):
                            colour = pattern_colour
                            break
                # Create the chip
                with chips:
                    new_move = ui.chip(
                        name,
                        removable=True,
                        icon='sports_mma',
                        color=colour,
                        selected=selected,
                        on_value_change=lambda: removeMove(new_move),selectable=True,on_selection_change= lambda: updateSelected(state)
                    ).props('square flat size=18px')
                calculateData(state)
                updateSelected(state)
            except Exception as e:
                print(f'No move selected:{e}')

    def updateSelected(state):
        clear_button.set_text('Clear all')
        state['chips_selected'] = False
        for chip in chips:
            chip.classes.clear()
            if chip.selected:
                chip.classes('ring-2 ring-slate-400 ring-offset-2')#'border-2 border-dashed  border-current')
                clear_button.set_text('Clear')
                state['chips_selected'] = True

    def moveChipsUp():
        chips_list = list(chips)
        # enumerate creates tuples where i is the index and chip is the value at that index, e.g. (0,chip1)
        selected_chips_indices = [i for i, chip in enumerate(chips_list) if chip.selected]
        if 0 in selected_chips_indices:
            return
        for i in selected_chips_indices:
            # if index isn't out of range and isn't next to another selected chip
            if i >0:
                chips_list[i], chips_list[i - 1] = chips_list[i - 1], chips_list[i]
        chips.clear()
        for chip in chips_list:
            createChip(chip.text, chip.selected,state)

    def moveChipsDown():
        chips_list = list(chips)
        #enumerate creates tuples where i is the index and chip is the value at that index, e.g. (0,chip1)
        selected_chips_indices = [i for i, chip in enumerate(chips_list) if chip.selected]
        if len(chips_list) -1 in selected_chips_indices:
            return
        for i in reversed(selected_chips_indices):
            #if index isn't out of range and isn't next to another selected chip
            if i < len(chips_list) -1:
                chips_list[i], chips_list[i + 1] = chips_list[i + 1], chips_list[i]
        chips.clear()
        for chip in chips_list:
            createChip(chip.text, chip.selected,state)

    def duplicateMove():
        for chip in chips:
            if chip.selected:
                createChip(chip.text, False,state)
                chip.selected = False

    def updateChips(state):
        state['move_list'] = [chip.text for chip in chips]

    def removeMove(chip):
        chip.delete()
        updateSelected(state)
        updateChips(state)

    def clearList(state):
        chips_to_delete = []
        if state['chips_selected']:
            for chip in chips:
                if chip.selected:
                    chips_to_delete.append(chip)
            for chip in chips_to_delete:
                chip.delete()
            clear_button.set_text('Clear all')
            state['chips_selected'] = False
        else:
            chips.clear()
        updateChips(state)

    def updateCounter(state, value):
        if value != 'PC':
            updatePerfectParry(state, False)
            perfect_parry_checkbox.set_value(False)
        state['counter'] = value
        counter_dict = {'None': ['No Counter','#d5deee'],
                        'CH':['Counter','#E2C900'],
                        'PC':['Punish Counter','#FF5118']}
        chips_row.clear()
        with chips_row:
            ui.markdown('#### **Combo string**:').style('flex:1; min-width: 240px')
            counter_chip = ui.chip(icon='undo', text=counter_dict[value][0], color=counter_dict[value][1]).props(
                'flat square size=18px').style('justify-self:end')
        calculateData(state)

    def updatePerfectParry(state, value):
        state['perfect_parry'] = value
        if value == True:
            counter_radio.set_value('PC')
        calculateData(state)

    def updateCancelledSpecial(state, value):
        state['cancelled_special'] = value
        calculateData(state)

    def calculateData(state):
        updateChips(state)
        move_dict = m.get_selected_moves_data(state['all_moves'], state['move_list'])
        state['drive_gauge'] = drive_slider.value
        state['super_gauge'] = super_slider.value
        try:
            data = cc.comboCalculatorFunc(move_dict,state)
            state['final_damage'] = data[0] + state['additional_damage']
            state['combo_data'] = data[1]
            state['super_gauge'] = data[2]
            state['drive_gauge'] = data[3]
            updateTable(state)
            updateDriveGauge(state)
            updateSuperGauge(state)
        except Exception as e:
            print(f'Calculator function error: {e}')
        with output_column:
            final_damage_number = state['final_damage']
            final_damage_label.set_content(f'#### Damage: **{final_damage_number}**')

    def updateSuperGauge(state):
        svg = ''
        super_gauge_svg = state['super_gauge_svg']
        current_super = int(state['super_gauge']/10000)
        bar_percent = float(state['super_gauge'] - (current_super *10000))/10000
        if bar_percent != 0:
            marker_visibility = 100
        else:
            marker_visibility = 0
        if current_super == 3:
            super_gauge_svg = '''
                                <svg viewbox ='0 0 700 70' width=352 height=60 xmlns="http://www.w3.org/2000/svg"> 
                                 <defs>
                                    <filter id="blur1">
                                      <feGaussianBlur stdDeviation="1.5" in="SourceGraphic"/>
                                </filter>
                                <filter id="blur2">
                                      <feGaussianBlur stdDeviation="1" in="SourceStroke"/>
                                </filter>
                                <linearGradient id="grad1" x1="0%" x2="100%" y1="0%" y2="0%">
                                  <stop offset="0.2" stop-color="#ffffff" stop-opacity=".9"/>                                
                                  <stop offset="0.5" stop-color="#ffffff" stop-opacity=".2"/>
                                  <stop offset="0.8" stop-color="#ffffff" stop-opacity=".9"/>
                                </linearGradient>
                                <linearGradient id="grad2" x2="1">
                                  <stop offset="0.5" stop-color="#ce207a"/>
                                  <stop offset="1" stop-color="#ffd4ff"/>
                                </linearGradient>
                                <linearGradient id="grad3" x2="1">
                                  <stop offset="0.2" stop-color="#ce207a"/>
                                  <stop offset="0.5" stop-color="#ffd4ff"/>
                                  <stop offset="0.8" stop-color="#ce207a"/>
                                </linearGradient> 
                              </defs>
                              <style>
                                .glow {filter: url(#blur1)}
                                .glow2 {filter: url(#blur2)}
                                .outline {stroke: url(#grad1)}
                              </style>
                              <g id="super bar">
                                <polygon id="bar glow" class="glow" fill="#ce207a" fill-opacity="30%" points="0,5 318,5 353,56 35,56"/>
                                <polygon id="bar background" fill="#grey" fill-opacity="30%" points="10,10 316,10 342,50 38,50"/>
                                <polygon id="bar filling" fill="url(#grad3)" points="10,10 316,10 342,50 38,50"/>
                                <polygon id="bar outline" stroke="url(#grad1)" stroke-width=2px fill='transparent' points="10,10 316,10 342,50 38,50"/>
                              </g>
                              </svg>
                        '''
        else:
            super_gauge_svg = '''
                          <svg viewbox ='0 0 700 70' width=352 height=60 xmlns="http://www.w3.org/2000/svg"> 
                              <defs>
                                <filter id="blur1">
                                      <feGaussianBlur stdDeviation="1.5" in="SourceGraphic"/>
                                </filter>
                                <filter id="blur2">
                                      <feGaussianBlur stdDeviation="1" in="SourceStroke"/>
                                </filter>
                                <linearGradient id="grad1" x1="0%" x2="100%" y1="0%" y2="0%">
                                  <stop offset="0.2" stop-color="#ffffff" stop-opacity=".9"/>                                
                                  <stop offset="0.5" stop-color="#ffffff" stop-opacity=".2"/>
                                  <stop offset="0.8" stop-color="#ffffff" stop-opacity=".9"/>
                                </linearGradient>
                                <linearGradient id="grad2" x2="1">
                                  <stop offset="0.5" stop-color="#ce207a"/>
                                  <stop offset="1" stop-color="#ffd4ff"/>
                                </linearGradient>
                                <linearGradient id="grad3" x2="1">
                                  <stop offset="0.2" stop-color="#ce207a"/>
                                  <stop offset="0.5" stop-color="#ffd4ff"/>
                                  <stop offset="0.8" stop-color="#ce207a"/>
                                </linearGradient> 
                              </defs>
                              <style>
                                .glow {filter: url(#blur1)}
                                .glow2 {filter: url(#blur2)}
                                .outline {stroke: url(#grad1)}
                              </style>
                              <g id="super bar">
                                <polygon id="bar background" fill="#grey" fill-opacity="30%" points="10,10 316,10 342,50 38,50"/>'''+f'''
                                <polygon id="bar filling" fill="url(#grad2)" points="10,10 {str((306*bar_percent)+10)},10 {str((304*bar_percent)+38)},50 38,50"/>
                                <polygon id="bar outline" stroke="url(#grad1)" stroke-width=2px fill='transparent' points="10,10 316,10 342,50 38,50"/>
                                <line id="marker grad" stroke-opacity='{marker_visibility}%' class="glow" stroke-width="2px" stroke="url(#grad3)" x1="{str((307*bar_percent)+4)}" y1="2" x2="{str((304*bar_percent)+44)}" y2="58"/>
                                <line id="marker white" stroke-opacity='{marker_visibility}%' class="glow2" stroke-width="2px" stroke="white" x1="{str((307*bar_percent)+7)}" y1="6" x2="{str((304*bar_percent)+41)}" y2="54"/>
                              </g>
                              </svg>
                        '''
        super_number_label.set_text(current_super)
        super_gauge_html.set_content(super_gauge_svg)
        super_gauge_html.update()

    def updateDriveGauge(state):
        svg = ''
        svg_dict = {
            'Bar 6': ['<path id="Bar 6" class="s6" d="m', 4.0],
            'Bar 5': ['<path id="Bar 5" class ="s5" d="m', 117.0],
            'Bar 4': ['<path id="Bar 4" class ="s4" d="m', 231.0],
            'Bar 3': ['<path id="Bar 3" class ="s3" d="m', 342.0],
            'Bar 2': ['<path id="Bar 2" class ="s2" d="m', 453.0],
            'Bar 1': ['<path id="Bar 1" class ="s1" d="m', 564.0]
        }
        if state['drive_gauge'] == 0:
            drive_gauge_svg = '''
                            <svg viewBox="0 0 770 35" width="220" height="10" xmlns="http://www.w3.org/2000/svg">
                            <g id="Drive Gauge">
                            <polygon id="burntout" fill="#grey" fill-opacity="30%"  points="10,6 654,6 669,31 25.4,31"/>
                              </g>
                            </svg>
                            '''
        else:
            drive_bars = math.ceil(state['drive_gauge'] / 10000)
            for index in range(drive_bars):
                bar_remaining = state['drive_gauge'] - (index * 10000)
                if bar_remaining > 10000:
                    bar_percent = 1
                else:
                    bar_percent = bar_remaining / 10000
                drive_bar = svg_dict['Bar ' + str((index + 1))][0] + str(
                    (90.6 - round(90.6 * bar_percent, 2) + svg_dict['Bar ' + str((index + 1))][1])) + ' 3.1 h' + str(
                    round(90.6 * bar_percent, 2)) + ' l20.4 30.8 h-' + str(
                    round(89.5 * bar_percent, 2)) + ' z"/>'
                svg = f'{svg}\n{drive_bar}'


            drive_gauge_svg = '''
                                <svg viewBox="0 0 770 35" width="220" height="10" xmlns="http://www.w3.org/2000/svg">
                                <style>
                                    .s6 { fill: #b3b816;stroke: #ebec24;stroke-miterlimit:100;stroke-width: 5 } 
                                    .s5 { fill: #a7b919;stroke: #e7f035;stroke-miterlimit:100;stroke-width: 5 } 
                                    .s4 { fill: #8fb11c;stroke: #d0ee36;stroke-miterlimit:100;stroke-width: 5 } 
                                    .s3 { fill: #88b713;stroke: #b9e724;stroke-miterlimit:100;stroke-width: 5 } 
                                    .s2 { fill: #56b70f;stroke: #90eb2e;stroke-miterlimit:100;stroke-width: 5 } 
                                    .s1 { fill: #3eb30d;stroke: #63e523;stroke-miterlimit:100;stroke-width: 5 } 
                                .s7 { opacity: .7;fill: #000000;stroke: #000000;stroke-miterlimit:100;stroke-width: 4 } 
                                </style>
                                <g id="Empty" style="opacity: .7">
                                    <path id="Empty" class="s7" d="m4 3.1h90.6l20.4 30.8h-89.5zm113 0h90.6l20.4 30.7h-89.5zm114 0h90.7l20.3 30.7h-89.4zm111 0h90.6l20.4 30.7h-89.5zm111 0h90.6l20.4 30.8h-89.5zm111 0h90.6l20.4 30.7h-89.5z"/>
                                </g>
                                <g id="Drive Gauge">
                                    {''' + svg + '''
                                    }
                                </g>
    
                                </svg>
                                '''
        drive_gauge_html.set_content(drive_gauge_svg)
        drive_gauge_html.update()

    def updateTable(state):
        table_row.clear()
        with table_row:
            if state['move_list']:
                df = pd.DataFrame(data=state['combo_data'])
                grid = ui.table.from_pandas(df).classes('w-full')
                with ui.grid(columns=1).style('row:auto; width:100%;') as table_dialog_grid:
                    ui.button('Close', on_click=lambda: table_dialog.close()).style('justify-self:end;')
            else:
                with ui.row():
                    ui.label('No moves selected. Select some moves first!')
                with ui.grid(columns=1).style('row:auto; width:100%;') as table_dialog_grid:
                    ui.button('Close', on_click=lambda: table_dialog.close()).style('justify-self:center;')

    async def saveCombo(state):
        save_combo_dialog_input.set_value('')
        combo_name = await save_combo_dialog
        if combo_name == '':
            combo_name = 'Combo'
        if combo_name:
            if state['move_list'] != []:
                if len(state['combo_storage'].keys()) < 11:
                    combo_uuid = uuid.uuid4()
                    final_damage_number = state['final_damage']
                    additional_damage_number = state['additional_damage']
                    drive_gauge_gained = state['drive_gauge'] - drive_slider.value
                    super_gauge_gained = state['super_gauge'] - super_slider.value
                    if state['additional_damage'] > 0:
                        damage_label_text = f'{final_damage_number} ({final_damage_number - additional_damage_number} + {additional_damage_number})'
                    else:
                        damage_label_text = state['final_damage']
                    if state['character'] in state['character_specifics'].keys():
                        character_specifics = state['character_specifics'][state['character']]
                    else:
                        character_specifics = None
                    state['combo_storage'][combo_uuid] = [state['move_list'],
                                                          state['counter'],
                                                          state['perfect_parry'],
                                                          character_specifics,
                                                          drive_slider.value,
                                                          super_slider.value,
                                                          state['final_damage'],
                                                          state['drive_gauge'],
                                                          state['super_gauge']]
                    with output_column:
                        with ui.row() as new_combo_row:
                            with ui.card().style('height: auto').props('square flat').classes('drop-shadow-md'):
                                with ui.row().style('width:100%'):
                                    with ui.column().style('width:15%').classes('gap-1'):
                                        ui.button(icon='arrow_back',on_click=lambda: restoreCombo(state,combo_uuid)).style('width:24px;')
                                        ui.button(icon='delete',on_click=lambda: deleteCombo(state, combo_uuid,new_combo_row)).style('width:24px;')
                                        ui.button(icon='download',on_click=lambda: downloadCombo(state, combo_uuid,combo_name)).style('width:24px;')
                                    with ui.column().style('width:77%'):
                                        ui.markdown(f'###### {combo_name}').style('width:100%;')
                                        ui.restructured_text(f'''
                                        Damage: **{damage_label_text}**

                                        Drive gained: **{drive_gauge_gained}**
                                        
                                        Super meter gain: **{super_gauge_gained}** ''')
                else:
                    ui.notify('Too many saved combos. Delete one to save!')

    def restoreCombo(state, combo_uuid):
        clearList(state)
        if state['character'] in state['character_specifics'].keys():
            state['character_specifics'][state['character']] = state['combo_storage'][combo_uuid][3]
        characterSpecificStuff(state)
        counter_radio.set_value(state['combo_storage'][combo_uuid][1])
        perfect_parry_checkbox.set_value(state['combo_storage'][combo_uuid][2])
        drive_slider.set_value(state['combo_storage'][combo_uuid][4])
        super_slider.set_value(state['combo_storage'][combo_uuid][5])
        for move in state['combo_storage'][combo_uuid][0]:
            createChip(move,False,state)

    def downloadCombo(state, uuid, name):
        combo_string = (f"Counter: {state['combo_storage'][uuid][1]}"
                        f"\nPerfect Parry: {state['combo_storage'][uuid][2]}"
                        f"\nString: {', '.join(state['combo_storage'][uuid][0])}"
                        f"\nDamage: {state['combo_storage'][uuid][6]}"
                        f"\nDrive Gain: {state['combo_storage'][uuid][7]-state['combo_storage'][uuid][4]}"
                        f"\nSuper Gain: {state['combo_storage'][uuid][8]-state['combo_storage'][uuid][5]}"
                        )
        ui.download(combo_string.encode('utf-8'), f'{name}.txt')

    def deleteCombo(state, uuid, row):
        del state['combo_storage'][uuid]
        row.delete()

    with (ui.row().style('width:100%;')):
        # left side
        with ui.column().style('min-width:240px;') as parameter_column:
            with ui.card().style('width:100%;height:100%;').props('square flat'):
                # dropdown button for selecting a character. runs update_dropdown function on selection which loads the character moves and sets them as options for the move_dropdown
                with ui.row():
                    with ui.button('Character', icon='switch_account').style('width: auto').props('align=left icon-right=arrow_drop_down') as select_character_button:
                        with ui.menu().style('width: 180px'):
                            ui.menu_item('A.K.I.').on('mousedown',lambda: characterSelected(state, 'A.K.I.'))
                            ui.menu_item('Akuma').on('mousedown', lambda: characterSelected(state, 'Akuma'))
                            ui.menu_item('Blanka').on('mousedown',lambda: characterSelected(state, 'Blanka'))
                            ui.menu_item('Cammy').on('mousedown', lambda: characterSelected(state, 'Cammy'))
                            ui.menu_item('Chun-Li').on('mousedown', lambda: characterSelected(state, 'Chun-Li'))
                            ui.menu_item('Dee Jay').on('mousedown', lambda: characterSelected(state, 'Dee Jay'))
                            ui.menu_item('Dhalsim').on('mousedown', lambda: characterSelected(state, 'Dhalsim'))
                            ui.menu_item('Ed').on('mousedown',lambda: characterSelected(state, 'Ed'))
                            ui.menu_item('E.Honda').on('mousedown', lambda: characterSelected(state, 'E.Honda'))
                            ui.menu_item('Guile').on('mousedown',lambda: characterSelected(state, 'Guile'))
                            ui.menu_item('Jamie').on('mousedown',lambda: characterSelected(state, 'Jamie'))
                            ui.menu_item('JP').on('mousedown',lambda: characterSelected(state, 'JP'))
                            ui.menu_item('Juri').on('mousedown',lambda: characterSelected(state, 'Juri'))
                            ui.menu_item('Ken').on('mousedown',lambda: characterSelected(state, 'Ken'))
                            ui.menu_item('Kimberly').on('mousedown', lambda: characterSelected(state, 'Kimberly'))
                            ui.menu_item('Lily').on('mousedown', lambda: characterSelected(state, 'Lily'))
                            ui.menu_item('Luke').on('mousedown', lambda: characterSelected(state, 'Luke'))
                            ui.menu_item('M.Bison').on('mousedown', lambda: characterSelected(state, 'M.Bison'))
                            ui.menu_item('Manon').on('mousedown', lambda: characterSelected(state, 'Manon'))
                            ui.menu_item('Marisa').on('mousedown', lambda: characterSelected(state, 'Marisa'))
                            ui.menu_item('Rashid').on('mousedown', lambda: characterSelected(state, 'Rashid'))
                            ui.menu_item('Ryu').on('mousedown', lambda: characterSelected(state, 'Ryu'))
                            ui.menu_item('Terry').on('mousedown', lambda: characterSelected(state, 'Terry'))
                            ui.menu_item('Zangief').on('mousedown', lambda: characterSelected(state, 'Zangief'))
                #character label and portrait
                with ui.row().style('width: 100%; justify-content: center;'):
                    character_label = ui.markdown('###### None').style('width:100%; text-align: center;')
                    character_portrait = ui.image(state['char_custom_dict'][state['character']][1]).style('height:56px;width:56px').classes('shadow-md rounded-borders')
                #character move select box and filter
                ui.markdown('**Character Moves:**')
                # move select dropdown
                with ui.row():
                    move_dropdown = ui.select(label='Select Move',
                                              with_input=True,
                                              options=[],
                                              on_change=lambda e: createChip(e.value,False,state) if e.value else None
                                              ).style('width:75%').props('hide-selected').on('keydown', lambda e: selectInput(e.args['key']))
                    select_button = ui.button(icon='check', on_click=lambda e: createChip(move_dropdown.value,False,state)).style(
                        'position:relative; top:10px; width:15%')
                    #filter
                with ui.expansion('Filter moves',icon='filter_list').style('width:100%; max-width: 280px'):
                    move_type_toggle = ui.select(label='No filter if empty', options=[],multiple=True,value=[],clearable=True, on_change= lambda e:filterMoves(e.value,state)).style('width: 100%').props('use-chips size=xs dense inline')
                    #modifiers
                with ui.expansion('Adjust modifiers', icon='tune').style('width:100%; max-width: 280px'):
                    ui.markdown('**Counter hit:**').style('height: 12px')
                    counter_radio = ui.radio(['None', 'CH', 'PC'], value='None',
                                             on_change=lambda e: updateCounter(state, e.value)).props('inline')

                    ui.markdown('**Other Modifiers:**').style('height: 12px')
                    perfect_parry_checkbox = ui.checkbox(text='Perfect Parry',
                                                         on_change=lambda e: updatePerfectParry(state, e.value))
                    cancelled_special_checkbox = ui.checkbox(text='Cancelled special into Super',
                                                             on_change=lambda e: updateCancelledSpecial(state, e.value))

                    ui.markdown('**Character specific options:**').style('height: 12px')
                    with ui.row() as char_specific_row:
                        ui.label('No character selected')
                    #sliders
                with ui.expansion('Adjust meter settings', icon='speed').style('width:100%; max-width: 280px'):
                    ui.markdown('**Starting Drive:**').style('height: 12px')
                    drive_slider_labels = {0:"0", 10000:"1", 20000:"2", 30000:"3",40000:"4", 50000:"5", 60000:"6"}
                    drive_slider = ui.slider(min=0, max=60000, step=250, value=60000).props(f'label thumb-size="0px" track-size="20px" :markers="10000" :marker-labels="{drive_slider_labels}"'
                    ).on('update:model-value', lambda: calculateData(state), throttle=0.3)
                    ui.markdown('**Starting Super:**').style('height: 12px')
                    super_slider_labels = {0:"0", 10000:"1", 20000:"2", 30000:"3"}
                    super_slider = ui.slider(min=0, max=30000, step=100, value=30000).props(f'label thumb-size="0px" track-size="20px" :markers="10000" :marker-labels="{super_slider_labels}"'
                    ).on('update:model-value', lambda: calculateData(state), throttle=0.3)

        # main body
        with ui.column().style('flex:1; width:100%;min-width:350px;') as combo_column:
            ui.markdown('#### **Combo string**:').style('flex:1; min-width: 240px')
            with ui.card().style('width: 100%; height:auto; min-height: 180px').classes('drop-shadow-md').props(
                    'square flat') as chips_card:
                with ui.row().style('width:100%') as chips_row:
                    counter_chip = ui.chip(icon='undo', text='No Counter', color='#d5deee').props(
                        'flat square size=18px').style('justify-self:end')
                with ui.column() as chips:
                    None
                with ui.row().style('width: 100%; height: 50px' ):
                    with ui.column().style(
                        'position: absolute; bottom: 10px; left: 10px'):
                        with ui.row().classes('gap-1'):
                            up_button = ui.button(icon='keyboard_arrow_up',on_click=lambda: moveChipsUp()).style('width:40px').bind_enabled_from(state, 'chips_selected', backward=lambda e: e)
                            down_button = ui.button(icon='keyboard_arrow_down',on_click=lambda: moveChipsDown()).style('width:40px').bind_enabled_from(state, 'chips_selected', backward=lambda e: e)
                    with ui.column().style(
                            'position: absolute; bottom: 10px; right: 10px'):
                        with ui.row().classes('gap-1'):
                            duplicate_button = ui.button(text='Duplicate', on_click=lambda: duplicateMove()).bind_enabled_from(state, 'chips_selected', backward=lambda e: e)
                            clear_button = ui.button(text='Clear all', on_click=lambda: clearList(state)).bind_enabled_from(state, 'move_list',
                                                                                               backward=lambda e: e)

        # right side
        with ui.column(align_items='center').style('width:20%;min-width:240px;') as output_column:
            with ui.card().props('square flat'):
                final_damage_number = state['final_damage']
                final_damage_label = ui.markdown(f'#### Damage: **{final_damage_number}**').style('width: 100%')
                drive_gauge_html = ui.html(state['drive_gauge_svg'])
                with ui.row(align_items='center').style('width: 100%; align-content: center;'):
                    super_number_label = ui.label(text=3).classes('text-2xl font-black').style('width:3%; color:#ce207a')
                    super_gauge_html = ui.html(state['super_gauge_svg']).style('width:87%')
                with ui.row().style('width: 100%; justify-content: center;'):
                    show_data_button = ui.button('Data', on_click=lambda: table_dialog.open()).style(
                        'width: 45%').bind_enabled_from(state, 'move_list', backward=lambda e: e)
                    save_button = ui.button('Save', on_click=lambda: saveCombo(state)).style(
                        'width: 45%').bind_enabled_from(state, 'move_list', backward=lambda e: e)

        # dialogs:
        with ui.dialog().props('maximized') as table_dialog:
            with ui.card().style('width:auto; height:auto;') as table_row:
                with ui.row():
                    ui.label('No moves selected. Select some moves first!')
                with ui.grid(columns=1).style('row:auto; width:100%;') as table_dialog_grid:
                    ui.button('Close', on_click=lambda: table_dialog.close()).style('justify-self:center;')
        with ui.dialog() as save_combo_dialog:
            with ui.card().style('width:auto; height:auto;'):
                save_combo_dialog_input = ui.input('Combo name').on('keydown.enter', lambda: save_combo_dialog.submit(
                    save_combo_dialog_input.value))
                with ui.grid(columns=1).style('row:auto; width:100%;'):
                    ui.button('Save', on_click=lambda: save_combo_dialog.submit(
                        save_combo_dialog_input.value) if save_combo_dialog_input else save_combo_dialog_input.set_value(
                        '')).style('justify-self:center;')
        with ui.dialog() as faq:
            with ui.card().style('width:auto; height:auto') as faq_text:
                ui.markdown('#### **FAQ**')

                ui.markdown('###### **What is this?**')

                ui.markdown('This is a (fairly) simple calculator for Street Fighter 6 combos built in Python. I built it to develop my programming skills. Hopefully you can find it useful/interesting/informative!')

                ui.markdown('###### **How do I use it?**')

                ui.markdown(
                    'First, select a character from the ‘Character’ menu, then select your moves from the ‘Select Move’ drop-down below it. You can experiment with counter types, perfect parry, cancelling from a special into a SA3 or CA or a number of character-specific options.')

                ui.markdown(
                    'Having an understanding of which moves combo into each other is required to take advantage of this tool fully.')

                ui.markdown('###### **How do I save my combos?**')

                ui.markdown('You can click “Save” next to the final damage on the right of your screen. Once you have named your combo you can click “download" to save it to a text file.')

                ui.markdown('###### **What does *term* mean when selecting my moves?**')

                ui.markdown(
                    'There are a number of keywords you might come across when selecting your moves from the drop-down. Check the expansion below for a full list.')
                with ui.expansion('Move keywords'):
                    ui.table(columns=state['faq_tables']['term_columns'], rows=state['faq_tables']['move_term_rows'], row_key='name', column_defaults={'align':'left'}).props('wrap-cells')

                ui.markdown('###### **How does the calculation work?**')

                ui.markdown(
                    'The simplest scaling calculations in Street Fighter 6 simply involve multiplying the base damage of an attack by a percentage which decreases depending on which move in the combo you are calculating.')

                ui.markdown(
                    'Most simple combos deal 100% for the first 2 hits, then drops to 80%, then 70%, 60%, etc, eventually dropping all the way to 10%.')

                ui.markdown(
                    'However, certain moves change this “scaling route”. The most common attacks which have this affect are light normal attacks, which basically skip the first multiplier of the example above, dealing 100%, then 80%, 70% and so on.')

                ui.markdown(
                    'Certain moves also apply additional scaling to themselves or the next move in the combo, and actions like Drive Rush can apply an additional scaling multiplier to the combo.')

                ui.markdown(
                    'Honestly, the number of factors which affect scaling is more than I can cover here. I recommend you experiment with the tool (especially using the "Data" button to view the breakdown of the calculation) and check out [the SuperCombo Wiki](https://wiki.supercombo.gg) if you want a better explanation!')

                ui.markdown('######**What does *term* mean when I view the data?**')

                ui.markdown(
                    'The columns in the data table might not be self-explanatory unless you have an decent understanding of the scaling calculation for Street Fighter 6. You can open the expansion below for an explanation of each column.')

                with ui.expansion('Calculation keywords'):
                     ui.table(columns=state['faq_tables']['term_columns'], rows=state['faq_tables']['data_term_rows'], row_key='name', column_defaults={'align':'left'}).props('wrap-cells')

                ui.markdown('######**How and why did you make this?**')

                ui.markdown('This tool is built in Python using [NiceGui](https://nicegui.io/)! I built it as an exercise for myself to learn some Python and turn a silly idea I had into something the Fighting Game Community might find useful. I am very unemployed right now.')

                ui.markdown('######**Something seems broken…**')

                ui.markdown(
                    'I am not surprised! [Please submit it as a bug report](https://docs.google.com/forms/d/e/1FAIpQLScZaAIoZlvbGyReEaReG2fSogdw5BKusLqWRuxZ7lj55gJNKw/viewform?usp=header). Please share as much information as you can, including what you did, what happened, what you expected to happen and screenshots if possible. If a combo is doing the a different amount of damage in the app as in-game, please double check you have all the same settings and moves, and if possible, send a training mode video with inputs and damage numbers enabled so I can troubleshoot. Thank you!')

        #footer
        with ui.row().style('width:100%'):
            with ui.button(icon='menu').style('width:38px; position:fixed; bottom: 4px; left: 4px'):
                with ui.menu():
                    dark_mode_toggle = ui.menu_item('Dark mode toggle',
                                                    on_click=lambda e: dark.disable() if dark.value else dark.enable())
                    faq_button = ui.menu_item('FAQ', on_click=lambda: faq.open())
                    bug_report = ui.menu_item('Bug report', on_click=lambda: ui.navigate.to(
                        'https://docs.google.com/forms/d/e/1FAIpQLScZaAIoZlvbGyReEaReG2fSogdw5BKusLqWRuxZ7lj55gJNKw/viewform?usp=header',
                        new_tab=True))
            with ui.link(target='https://ko-fi.com/tragicdog'):
                ui.image(
                    'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/kofi.png').style(
                    'width:200px; position:fixed; bottom: 4px; right: 10px')

ui.run(title='Combo Calculator',favicon='https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/icon.svg',on_air=False,reload='FLY_ALLOC_ID' not in os.environ,viewport='width=device-width, user-scalable=no')

#to do:
# create definitions for keywords
# add section select for move select dropdown



