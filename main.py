# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# type, note, time, channel, velocity
import math
from datetime import time

import easygui
from typing import Tuple, List, Any

import midi_data_obtainer as md
from fractions import Fraction

# import math

MAX_DENOM_POWER = 7  # useless var
MAX_DENOM = 2 ** MAX_DENOM_POWER  # useless var
FORCE_STOP = False
SONG_LENGTH = 850
PROMPT = True

# well scrap that, predefine our BPM mult
BPM_MULTI = 8
TRANSPOSE = 4


def generate_powers_of_2(max_pow: int) -> list[int]:
    """
    :param max_pow: A max power.
    :return: A list of powers of 2 no greater than 2 ** max_pow.

    >>> generate_powers_of_2(5)
    [2, 4, 8, 16, 32]
    """
    list_so_far = []
    curr = 2
    for i in range(0, max_pow):
        list_so_far.append(curr)
        curr = 2 ** (i + 2)
    return list_so_far


def psb(text: str) -> bool:
    """Used for inputs: y for yes, F for others.
    :param text:
    :return:
    """
    t = input(f'{text} y (or Y) for yes, otherwise no.')
    if t in {'y', 'Y'}:
        return True
    else:
        return False


def main(midi_path: str):
    if PROMPT:
        f_stop = psb('Force stop?')
        bpm_mult = int(input('BPM multiplier? (e.g. say 2 if your most precise notes are eigth notes, 4 if 16th...)'))
        if not math.isclose(math.log2(bpm_mult) % 1, 0):
            print('DID YOU JUST IMPLEMENT A BPM MULTIPLIER THAT IS NOT AN EXPONENT OF 2???'
                  ' Make sure you know what you are doing. Unless you are dealing with a song with'
                  'a swing tempo, but even then, I cannot guarantee anything.')
        bpm_div = float(input('Type 0.5 if you want the song to play half as fast, 1 for normal, or 2 for fast'))
    else:
        f_stop = FORCE_STOP
        bpm_mult = BPM_MULTI
        bpm_div = 1

    spb = md.obtain_spb(midi_path)
    bpm = 60 / spb
    print('The bpm is ' + str(bpm))
    midi_data = md.process_midi(midi_path)
    # convert all timings to beat numbers
    midi_data_1 = multiply_beat_number(midi_data, spb, bpm_mult)
    print('a')
    highest_midi_channel = max(x[3] for x in midi_data_1)
    print(highest_midi_channel)
    final_bpm = round(bpm * BPM_MULTI * bpm_div)
    file_str = generate_file(midi_data_1, final_bpm, f_stop)

    ei = midi_path.rfind('\\')
    if ei != -1:
        export_file_name = midi_path[ei + 1:]
    else:
        export_file_name = midi_path

    export(file_str, f'{export_file_name[:-4]}.🗿')

    # midi_data_1, highest_denom = obtain_beat_number(midi_data, spb)
    # bpm_multiplier = math.ceil(math.log(highest_denom, 2))
    # highest_denom_ceiling = 2 ** bpm_multiplier
    # true_bpm = (60 / spb) * bpm_multiplier
    # midi_data_2 = obtain_beat_number_int(midi_data_1, highest_denom_ceiling)
    # print(midi_data_2)


def nnto(pitch: str) -> int:
    """Note name to offset
    Return the note to subtract. For example, if a C is passed and our root note is A, then
    we need to add by C - cur.
    :param pitch:
    :return:
    """
    pitch_relative = pitch[:-1]
    octave = int(pitch[-1])
    octave_offset = (octave - 5) * 12
    note_dict = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6,
                 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}

    cur_note = note_dict[pitch_relative]  # a value from 0 to 11 representing offset
    note_you_want_to_play = -cur_note - octave_offset
    return note_you_want_to_play


def channel_to_sample(channel: int, file_str: str) -> list[str, int]:
    """
    :param file_str:
    :param channel: midi channel of the note
    :return: what it corresponds to
    """
    if not PROMPT:
        the_list = [
            ['mariopaint_flower', -6],
            ['noteblock_bell', -6]
        ]
    else:
        insts = file_str  # read_file('instruments.txt')
        last_ind = insts.find(r'\\')
        if last_ind == -1:
            last_ind = len(insts)
        insts_final = insts[:last_ind].strip()
        temp_list = insts_final.split('\n')
        dl = ';'
        the_list = []
        for item in temp_list:
            split_str = item.split(dl)
            if len(split_str) == 1:
                offset = 0
            else:
                offset = nnto(split_str[1])
            the_list.append([split_str[0], offset])
        # consider splitting the list again
    try:
        sample = the_list[channel]
    except IndexError:
        sample = the_list[0]
    return sample


MIDI_PERCS = {
    35: '🥁', 36: 'undertale_crack', 37: 'sidestick', 38: 'hammer',
    39: '👏', 40: 'noteblock_snare', 41: 'adofaikick', 42: 'cowbell',
    43: '💀', 44: 'tab_rows', 45: 'tonk', 46: 'tab_sounds', 47: 'undertale_hit',
    48: 'undertale_encounter', 49: 'fnf_death', 50: 'yahoo', 51: 'issac_hurt', 52: 'issac_dead',
    53: 'minecraft_bell', 54: 'ook', 55: 'gun', 56: 'cowbell', 57: 'mariopaint_dog', 58: 'mariopaint_cat'
}


MIDI_PERCS_2 = [
    '🥁',
    'undertale_crack',
    'sidestick',
    'hammer',
    '👏',
    'noteblock_snare',
    'adofaikick',
    'cowbell',
    '💀',

]


def generate_file(midi_data: list, final_bpm: int, f_stop: bool = False) -> str:
    """Actually generate the final string.
    :param f_stop:
    :param midi_data:
    :param final_bpm:
    :return:

    Preconditions:
        - all the notes in midi_data are in chronological order
    """
    # this only runs once. The running time also SUCKS
    inst_text_dir = easygui.fileopenbox(msg='What INST TXT file would you like to select?', filetypes=["*.txt", '*'], default='*.txt')
    # inst_text_dir = 'freedomdive.txt'
    if inst_text_dir is None:
        print('Did you close the box? We\'ll do defaults for you.')
        file_string = 'noteblock_banjo;F#5\nmariopaint_car;F#5'
    else:
        file_string = read_file(inst_text_dir)
    sequence_so_far = [f'!speed@{final_bpm * 2}']
    # prev_note_timing = -1
    for i in range(0, SONG_LENGTH):
        acceptable_notes = [x for x in midi_data if x[2] == i]
        # formatted_acceptable_notes = [f'{channel_to_sample(x[3])}{generate_pitch_str(x[1] - 64)}'
        #                              for x in acceptable_notes]
        formatted_acceptable_notes = []
        for curr_note in acceptable_notes:
            if curr_note[3] != 9:
                processed_str = f'{channel_to_sample(curr_note[3], file_string)[0]}' \
                                f'{generate_pitch_str(channel_to_sample(curr_note[3], file_string)[1] + curr_note[1] - 64 + TRANSPOSE)}'
                formatted_acceptable_notes.append(processed_str)
            else:
                try:
                    processed_str = MIDI_PERCS[curr_note[1]]
                    formatted_acceptable_notes.append(processed_str)
                except KeyError:
                    pass  # do not pass go; do not collect 200
        new_fan = []
        cur_iter = 0
        if len(formatted_acceptable_notes) != 0:
            for note in formatted_acceptable_notes:
                if cur_iter >= 1:
                    new_fan.extend(['!combine', note])
                else:
                    new_fan.append(note)
                cur_iter += 1
            if f_stop:
                new_fan.insert(0, '!cut')
        else:
            new_fan = ['_pause']

        sequence_so_far.extend(new_fan)

    # sequence so far is our sequence so far. Now let's just truncate it a bit:
    # we will go through sequence so far and truncate any
    new_sequence_so_far = []
    pause_accumulator = 0
    for element in sequence_so_far:
        if element == '_pause':
            pause_accumulator += 1
            # add 1 to the pause accumulator. Do NOT add to the new sequence.
        else:
            if pause_accumulator == 1:
                new_sequence_so_far.append('_pause')
            elif pause_accumulator >= 2:
                new_sequence_so_far.append(f'!stop@{str(pause_accumulator)}')
            # either way, we'll still append like normal
            pause_accumulator = 0
            new_sequence_so_far.append(element)
    return '|'.join(new_sequence_so_far)


trash = r"""
    for note in midi_data:
        relative_pitch = note[1] - 60
        pitch_str = generate_pitch_str(relative_pitch)
        sample_str = channel_to_sample(note[3])
        final_str = sample_str + pitch_str
        # HERE COMES THE WARNINGS
        if note[2] - prev_note_timing > 1:  # 2 or above
            if note[2] - prev_note_timing == 2:
                sequence_so_far.append('_pause')
            else:
                time_diff = note[2] - prev_note_timing
                sequence_so_far.append(f'!stop@{time_diff}')
        if prev_note_timing == note[2]:  # matching note timings
            sequence_so_far.append('!combine')
        elif FORCE_STOP:  # will not run if the note timings match but always otherwise.
            sequence_so_far.append('!cut')
        prev_note_timing = note[2]
        sequence_so_far.append(final_str)
    # finally when we are done
    """


def export(string: str, file_name: str) -> None:
    """Export the file for once!!
    :param string:
    :param file_name:
    :return:
    """
    with open(file_name, 'w', encoding='UTF-8') as f:
        f.write(string)


def read_file(directory: str) -> str:
    """Read the file you wish to read!!
    :param directory:
    :return:
    """
    with open(directory, 'r', encoding='UTF-8') as f:
        file_content = f.read()
    return file_content


def generate_pitch_str(num: int) -> str:
    """
    :param num: realtive pitch: C5 is 0
    :return: what it shows up as
    """
    if num == 0:
        return ''
    else:
        return '@' + str(num)


def multiply_beat_number(midi_data: list[list[str | float | int]],
                         spb: int | float, mult: int) -> list[list[str | float | int]]:
    """Return the same midi data but all the timings are in int format.
    We will also return the highest fraction.

    Preconditions: No triplets. All notes are quantized
    We will be using the highest denominator here.
    """
    # highest_denom_so_far = 1  # must be 1 or a power of 2.
    new_midi_data_so_far = []
    for note in midi_data:
        beat_count = note[2] / spb
        timing = round(beat_count * mult)

        new_midi_data_so_far.append([note[0], note[1], timing, note[3], note[4]])
    return new_midi_data_so_far


# GARBAGE BELOW


def obtain_beat_number(midi_data: list[list[str | float | int]],
                       spb: int | float) -> tuple[list[list[str | float | int | Fraction]], int]:
    """Return the same midi data but all the timings are in fraction format.
    We will also return the highest fraction.

    Preconditions: No triplets. All notes are quantized
    We will be using the highest denominator here.
    """
    highest_denom_so_far = 1  # must be 1 or a power of 2.
    new_midi_data_so_far = []
    for note in midi_data:
        timing = note[2]
        beat = timing / spb
        frac = Fraction(beat).limit_denominator(MAX_DENOM)
        highest_denom_so_far = max(highest_denom_so_far, frac.denominator)
        new_midi_data_so_far.append([note[0], note[1], frac, note[3], note[4]])
    return new_midi_data_so_far, highest_denom_so_far


def obtain_beat_number_int(midi_data: list[list[str | float | int | Fraction]], highest_denom: int):
    """Same as the previous function but return the beat count assuming there are nothing more than
    quarter notes.
    :param midi_data:
    :param highest_denom:
    :return:
    """
    midi_data_so_far = []
    for note in midi_data:
        # timing = note[2]
        denominator = note[2].denominator
        if denominator != highest_denom:
            mult = highest_denom // note[2].denominator
            new_beats = note[2].numerator * mult
        else:
            new_beats = note[2].numerator
        midi_data_so_far.append([note[0], note[1], new_beats, note[3], note[4]])
    return midi_data_so_far


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    directory_cur = easygui.fileopenbox(msg='What MIDI file would you like to select?',
                                        filetypes=["*.mid", '*'],
                                        default='*.mid')
    print('You selected ' + directory_cur)
    if directory_cur is None:
        print('Did you not select a file?')
    main(directory_cur)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
