from nicegui import ui
from getMoves import moves as m
from calculator import comboCalculator as cc
import re
import uuid
import math
import pandas as pd


@ui.page('/')
def main_page():
    state = {
        # variables for loading moves
        'file_name': '',
        'move_list': [],
        'character': 'None',
        #variables for calculating damage/scaling/drive gauge
        'counter': 'No Counter',
        'perfect_parry': False,
        'cancelled_special': False,
        'final_damage': 0,
        'additional_damage': 0,
        'drive_gauge': 60000.0,
        #combo_data contains  cleaned up data for the calculation per-move
        'combo_data': [{'Move name': None, 'Final damage': None, 'Final scaling': None, 'Route scaling': None,
                        'Drive Rush scaling': None, 'Counts as x hits': None, 'Immediate scaling': None,
                        'Next move scaling': None, 'Raw damage': None, 'Combo damage': None, 'Drive gain': None}],
        #combo_storage will store key information about a combo when it is saved so it can be restored later by the user
        'combo_storage': {},
        # string storing svg data for the drive gauge to update
        'drive_gauge_svg': '''
                            <svg viewBox="0 0 680 37" width="220" height="20" xmlns="http://www.w3.org/2000/svg">
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
        # character UI colours and icons
        'char_custom_dict': {'None': ['#465261', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/None.png'], 'A.K.I.': ['#6b254b', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/A.K.I..png'], 'Akuma': ['#8e1f11', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Akuma.png'], 'Blanka': ['#036c03', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Blanka.png'], 'Cammy': ['#355f97', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Cammy.png'], 'Chun-Li': ['#6483de', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Chun-Li.png'], 'Dee Jay': ['#008b0c', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Dee Jay.png'], 'Dhalsim': ['#d7a403', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Dhalsim.png'], 'Ed': ['#086b7a', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Ed.png'], 'E.Honda': ['#a90600', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/E.Honda.png'], 'Guile': ['#316326', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Guile.png'], 'Jamie': ['#bc9c0e', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Jamie.png'], 'JP': ['#3c2a51', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/JP.png'], 'Juri': ['#601199', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Juri.png'], 'Ken': ['#bd1613', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Ken.png'], 'Kimberly': ['#7584', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Kimberly.png'], 'Lily': ['#d78076', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Lily.png'], 'Luke': ['#4628c9', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Luke.png'], 'M. Bison': ['#61346d', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/M. Bison.png'], 'Manon': ['#796dc7', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Manon.png'], 'Marisa': ['#b90302', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Marisa.png'], 'Rashid': ['#cb7c1c', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Rashid.png'], 'Ryu': ['#863532', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Ryu.png'], 'Terry': ['#8e1b18', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Terry.png'], 'Zangief': ['#c91212', 'https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/Zangief.png']},
         # character specific variables
        'character_specifics': {'Jamie': 2,
                                'A.K.I.': 0},

        # faq term info
        'faq_tables': {'term_columns': [{'name': 'name', 'label': 'Name', 'field': 'name', 'sortable': False},
                                                {'name': 'meaning', 'label': 'Meaning', 'field': 'meaning',
                                                 'sortable': False}],
                               'move_term_rows': [{'name': '', 'meaning': ''},
                                                  {'name': '', 'meaning': ''}],
                               'data_term_rows': [{'name': '', 'meaning': ''},
                                                  {'name': '', 'meaning': ''}]
                               }

    }

    # set ui defaults
    ui.colors()
    dark = ui.dark_mode()
    ui.colors(primary='#465261')
    ui.card.default_style('width: 250px; height: 220px')

    def characterSpecificStuff(state):

        def changeAkiPoison(slider_value, label):
            state['additional_damage'] = math.floor(slider_value * 60)
            poison_text = state['additional_damage']
            label.set_text(f'Poison damage: {poison_text}')
            calculateDamage(state)

        def changeJamieScaling(radio_value):
            state['character_specifics']['Jamie'] = radio_value
            calculateDamage(state)

        char_specific_row.clear()
        if state['character'] == 'Jamie':
            with char_specific_row:
                ui.select(label='Drink level', options=[0, 1, 2, 3, 4], value=state['character_specifics']['Jamie'],on_change=lambda e: changeJamieScaling(e.value)).style('width: 100px')

        elif state['character'] == 'A.K.I.':
            with char_specific_row:
                ui.label('Estimated seconds poisoned:').style('height: 40px')
                poison = ui.slider(min=0.0, max=10.0, step=0.1, value=0,
                                   on_change=lambda e: changeAkiPoison(e.value, poison_label)).props('label-always')
                poison_label = ui.label('Poison damage: 0')
        else:
            with char_specific_row:
                ui.label('No character specific options available')

    def characterSelected(state, selected_character, move_dropdown, label):
        state['character'] = selected_character
        state['additional_damage'] = 0
        state['character_specifics']['Jamie'] = 2
        state['file_name'] = m.get_character(selected_character)
        all_moves = m.get_moves(state['file_name'])
        move_dropdown.set_options(all_moves)
        clearList(state)
        ui.colors(primary=state['char_custom_dict'][selected_character][0])
        character_portrait.set_source(state['char_custom_dict'][selected_character][1])
        label.content = f'###### **{selected_character}**'
        characterSpecificStuff(state)
        return selected_character

    def createChip(name):
        if name:
            try:
                # Default color
                colour = 'blue-grey-5'
                colours = {
                    re.compile(r'\d{2,3}[PK][PK]|\d{3}[LMH][KP][LMH][KP]'): 'orange-4',  # OD moves
                    re.compile(r'\d.*L[KP]'): 'light-blue-11',  # Lights
                    re.compile(r'\d.*M[KP]'): 'amber-4',  # Mediums
                    re.compile(r'\d.*H[KP]'): 'red-5',  # Heavies
                    re.compile(r'SA[123]|CA$'): 'deep-orange-6',  # Supers
                    re.compile(r'Drive'): 'light-green-6'  # Drive gauge stuff
                }
                # Determine the chip's color
                for pattern, pattern_colour in colours.items():
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
                        on_value_change=lambda: removeMove(new_move)
                    ).props('square flat size=18px')
                updateChips(state)
            except Exception as e:
                print(f'No move selected:{e}')

    def updateChips(state):
        state['move_list'] = [chip.text for chip in chips]
        calculateDamage(state)

    def removeMove(chip):
        chip.delete()
        updateChips(state)

    def updateCounter(state, value):
        if value != 'Punish Counter':
            updatePerfectParry(state, False)
            perfect_parry_checkbox.set_value(False)
        state['counter'] = value
        counter_dict = {'No Counter': '#d5deee',
                        'Counter': '#E2C900',
                        'Punish Counter': '#FF5118'}
        chips_row.clear()
        with chips_row:
            ui.markdown('#### **Combo string**:').style('flex:1; min-width: 240px')
            counter_chip = ui.chip(icon='undo', text=value, color=counter_dict[value]).props(
                'flat square size=18px').style('justify-self:end')
        calculateDamage(state)

    def updatePerfectParry(state, value):
        state['perfect_parry'] = value
        if value == True:
            counter_radio.set_value('Punish Counter')
        calculateDamage(state)

    def updateCancelledSpecial(state, value):
        state['cancelled_special'] = value
        calculateDamage(state)

    def calculateDamage(state):
        move_dict = m.get_selected_moves_data(state['file_name'], state['move_list'])
        try:
            data = cc.comboCalculatorFunc(move_dict, state)
            state['final_damage'] = data[0] + state['additional_damage']
            state['combo_data'] = data[1]
            state['drive_gauge'] = data[2]
            updateTable(state)
            calculateDriveGauge(state)
        except Exception as e:
            print(f'Calculator function error: {e}')
        with col2:
            final_damage_number = state['final_damage']
            final_damage_label.set_content(f'#### Damage: **{final_damage_number}**')

    def calculateDriveGauge(state):
        svg = ''
        svg_dict = {
            'Bar 6': ['<path id="Bar 6" class="s6" d="m', 4.0],
            'Bar 5': ['<path id="Bar 5" class ="s5" d="m', 117.0],
            'Bar 4': ['<path id="Bar 4" class ="s4" d="m', 231.0],
            'Bar 3': ['<path id="Bar 3" class ="s3" d="m', 342.0],
            'Bar 2': ['<path id="Bar 2" class ="s2" d="m', 453.0],
            'Bar 1': ['<path id="Bar 1" class ="s1" d="m', 564.0]
        }
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
                            <svg viewBox="0 0 680 37" width="220" height="20" xmlns="http://www.w3.org/2000/svg">
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
                with ui.grid(columns=2).style('row:auto; width:100%;') as table_dialog_grid:
                    ui.button('Show/Hide Columns', on_click=lambda: table_dialog.close()).style('justify-self:start;')
                    ui.button('Close', on_click=lambda: table_dialog.close()).style('justify-self:end;')
            else:
                with ui.row():
                    ui.label('No moves selected. Select some moves first!')
                with ui.grid(columns=1).style('row:auto; width:100%;') as table_dialog_grid:
                    ui.button('Close', on_click=lambda: table_dialog.close()).style('justify-self:center;')

    def clearList(state):
        chips.clear()
        updateChips(state)

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
                    drive_gauge_status = state['drive_gauge']
                    if state['additional_damage'] > 0:
                        damage_label_text = f'{final_damage_number} ({final_damage_number - additional_damage_number} + {additional_damage_number})'
                    else:
                        damage_label_text = state['final_damage']
                    state['combo_storage'][combo_uuid] = [state['move_list'], damage_label_text, state['counter'],
                                                          state['perfect_parry'], state['character_specifics'][state['character']],
                                                          combo_name]
                    with col2:
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

                                        Drive used: **{int(60000 - drive_gauge_status)}**''')
                else:
                    ui.notify('Too many saved combos. Delete one to save!')

    def restoreCombo(state, combo_uuid):
        clearList(state)
        state['move_list'] = state['combo_storage'][combo_uuid][0]
        state['counter'] = state['combo_storage'][combo_uuid][2]
        state['perfect_parry'] = state['combo_storage'][combo_uuid][3]
        print(state['combo_storage'][combo_uuid][4])
        state['character_specifics'][state['character']] = state['combo_storage'][combo_uuid][4]
        print(state['character_specifics'])
        characterSpecificStuff(state)
        for move in state['move_list']:
            createChip(move)
        counter_radio.set_value(state['counter'])
        perfect_parry_checkbox.set_value(state['perfect_parry'])

    def downloadCombo(state, uuid, name):
        combo_string = f"Counter: {state['combo_storage'][uuid][2]}\nString: {', '.join(state['combo_storage'][uuid][0])}\nDamage: {state['combo_storage'][uuid][1]}"
        ui.download(combo_string.encode('utf-8'), f'{name}.txt')

    def deleteCombo(state, uuid, row):
        del state['combo_storage'][uuid]
        row.delete()

    with ui.row().style('width:100%;'):
        # left side
        with ui.column(align_items='center').style('max-width:240px;min-width:240px;') as left_drawer:
            with ui.card().style('width:100%;height:100%;').props('square flat'):
                with ui.row():
                    # dropdown button for selecting a character. runs update_dropdown function on selection which loads the character moves and sets them as options for the move_dropdown
                    with ui.dropdown_button('Character', auto_close=True, icon='switch_account').style(
                            'width: auto') as select_character_button:
                        ui.item('A.K.I.').on('mousedown',
                                             lambda: characterSelected(state, 'A.K.I.', move_dropdown, character_label))
                        ui.item('Akuma').on('mousedown',
                                            lambda: characterSelected(state, 'Akuma', move_dropdown, character_label))
                        ui.item('Blanka').on('mousedown',
                                             lambda: characterSelected(state, 'Blanka', move_dropdown, character_label))
                        ui.item('Cammy').on('mousedown',
                                            lambda: characterSelected(state, 'Cammy', move_dropdown, character_label))
                        ui.item('Chun-Li').on('mousedown', lambda: characterSelected(state, 'Chun-Li', move_dropdown,
                                                                                     character_label))
                        ui.item('Dee Jay').on('mousedown', lambda: characterSelected(state, 'Dee Jay', move_dropdown,
                                                                                     character_label))
                        ui.item('Dhalsim').on('mousedown', lambda: characterSelected(state, 'Dhalsim', move_dropdown,
                                                                                     character_label))
                        ui.item('Ed').on('mousedown',
                                         lambda: characterSelected(state, 'Ed', move_dropdown, character_label))
                        ui.item('E.Honda').on('mousedown', lambda: characterSelected(state, 'E.Honda', move_dropdown,
                                                                                     character_label))
                        ui.item('Guile').on('mousedown',
                                            lambda: characterSelected(state, 'Guile', move_dropdown, character_label))
                        ui.item('Jamie').on('mousedown',
                                            lambda: characterSelected(state, 'Jamie', move_dropdown, character_label))
                        ui.item('JP').on('mousedown',
                                         lambda: characterSelected(state, 'JP', move_dropdown, character_label))
                        ui.item('Juri').on('mousedown',
                                           lambda: characterSelected(state, 'Juri', move_dropdown, character_label))
                        ui.item('Ken').on('mousedown',
                                          lambda: characterSelected(state, 'Ken', move_dropdown, character_label))
                        ui.item('Kimberly').on('mousedown', lambda: characterSelected(state, 'Kimberly', move_dropdown,
                                                                                      character_label))
                        ui.item('Lily').on('mousedown',
                                           lambda: characterSelected(state, 'Lily', move_dropdown, character_label))
                        ui.item('Luke').on('mousedown',
                                           lambda: characterSelected(state, 'Luke', move_dropdown, character_label))
                        ui.item('M. Bison').on('mousedown', lambda: characterSelected(state, 'M. Bison', move_dropdown,
                                                                                      character_label))
                        ui.item('Manon').on('mousedown',
                                            lambda: characterSelected(state, 'Manon', move_dropdown, character_label))
                        ui.item('Marisa').on('mousedown',
                                             lambda: characterSelected(state, 'Akuma', move_dropdown, character_label))
                        ui.item('Rashid').on('mousedown',
                                             lambda: characterSelected(state, 'Rashid', move_dropdown, character_label))
                        ui.item('Ryu').on('mousedown',
                                          lambda: characterSelected(state, 'Ryu', move_dropdown, character_label))
                        ui.item('Terry').on('mousedown',
                                            lambda: characterSelected(state, 'Terry', move_dropdown, character_label))
                        ui.item('Zangief').on('mousedown', lambda: characterSelected(state, 'Zangief', move_dropdown,
                                                                                     character_label))

                with ui.row().style('width: 100%; justify-content: center;'):
                    character_label = ui.markdown('###### None').style('width:100%; text-align: center;')
                    character_portrait = ui.image(state['char_custom_dict'][state['character']][1]).style('height:56px;width:56px').classes('shadow-md rounded-borders')

                ui.markdown('**Character Moves:**')
                with ui.row():
                    move_dropdown = ui.select(label='Select Move', options=[], with_input=True,
                                              on_change=lambda e: createChip(e.value)).style('width:75%')
                    select_button = ui.button(icon='check', on_click=lambda e: createChip(move_dropdown.value)).style(
                        'position:relative; top:10px; width:15%')

                ui.markdown('**Counter hit:**').style('height: 12px')
                counter_radio = ui.radio(['No Counter', 'Counter', 'Punish Counter'], value='No Counter',
                                         on_change=lambda e: updateCounter(state, e.value)).style('padding: 4px')

                ui.markdown('**Other Modifiers:**').style('height: 12px')
                perfect_parry_checkbox = ui.checkbox(text='Perfect Parry',
                                                     on_change=lambda e: updatePerfectParry(state, e.value))
                cancelled_special_checkbox = ui.checkbox(text='Cancelled special into Super',
                                                         on_change=lambda e: updateCancelledSpecial(state, e.value))

                ui.markdown('**Character specific options:**').style('height: 12px')
                with ui.row() as char_specific_row:
                    ui.label('No character selected')

        # main body
        with ui.column().style('flex:1; width:100%;min-width:240px;') as main_col:
            ui.markdown('#### **Combo string**:').style('flex:1; min-width: 240px')
            with ui.card().style('width: 100%; height:auto; min-height: 180px').classes('drop-shadow-md').props(
                    'square flat') as chips_card:
                with ui.row().style('width:100%') as chips_row:
                    counter_chip = ui.chip(icon='undo', text='No Counter', color='#d5deee', ).props(
                        'flat square size=18px').style('justify-self:end')
                with ui.column() as chips:
                    chips = chips
                clear_button = ui.button(text='Clear', on_click=lambda e: clearList(state)).style(
                    'position: absolute; bottom: 10px; right: 10px')

        # right side
        with ui.column(align_items='center').style('width:20%;max-width:240px;min-width:240px;') as col2:
            with ui.card().props('square flat'):
                final_damage_number = state['final_damage']
                final_damage_label = ui.markdown(f'#### Damage: **{final_damage_number}**').style('width: 100%')
                drive_gauge_label = ui.markdown('Drive gauge:')
                drive_gauge_html = ui.html(state['drive_gauge_svg'])
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
                    None #ui.table()

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
                     None #ui.table()

                ui.markdown('######**How did you make this?**')

                ui.markdown('This tool is built in Python using NiceGui.io')

                ui.markdown('######**Something seems broken…**')

                ui.markdown(
                    'I am not surprised! [Please submit it as a bug report](https://docs.google.com/forms/d/e/1FAIpQLScZaAIoZlvbGyReEaReG2fSogdw5BKusLqWRuxZ7lj55gJNKw/viewform?usp=header) using the button in the bottom left of you screen. Please share as much information as you can, including what you did, what happened, what you expected to happen and screenshots if possible. If a combo is doing the a different amount of damage in the app as in-game, please double check you have all the same settings and moves, and if possible, send a training mode video with inputs and damage numbers enabled so I can troubleshoot. Thank you!')

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



ui.run(title='Combo Calculator',favicon='https://raw.githubusercontent.com/TragicDoggo/sf6comboCalculator/refs/heads/master/images/icon.svg')

#to do:
# create definitions for keywords
# add section select for move select dropdown



