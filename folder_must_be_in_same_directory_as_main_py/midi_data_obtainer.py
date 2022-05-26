"""
Most of the code is copy-pasted from
https://stackoverflow.com/questions/63105201/python-mido-how-to-get-note-starttime-stoptime-track-in-a-list
which is under a CC-BY-SA license, as everything on stackoverflow is.
"""
from pprint import pprint
from typing import Union

from mido import MidiFile


def process_midi(path: str) -> list[list[str | float | int]]:
    """Return midi data from path."""
    mid = MidiFile(path)
    mididict = []
    output = []

    # Put all note on/off in midinote as dictionary.
    for i in mid:
        if i.type == 'note_on' or i.type == 'note_off' or i.type == 'time_signature':
            mididict.append(i.dict())
    # change time values from delta to relative time.
    mem1 = 0
    for i in mididict:
        time = i['time'] + mem1
        i['time'] = time
        mem1 = i['time']
        # make every note_on with 0 velocity note_off
        if i['type'] == 'note_on' and i['velocity'] == 0:
            i['type'] = 'note_off'
        # put note, starttime, stoptime, as nested list in a list.
        # format is [type, note, time, channel]
        mem2 = []
        if i['type'] == 'note_on':  # or i['type'] == 'note_off':
            mem2.append(i['type'])
            mem2.append(i['note'])
            mem2.append(i['time'])
            mem2.append(i['channel'])
            mem2.append(i['velocity'])
            output.append(mem2)
        # put timesignatures
        if i['type'] == 'time_signature':
            pass
            # mem2.append(i['type'])
            # mem2.append(i['numerator'])
            # mem2.append(i['denominator'])
            # mem2.append(i['time'])
            # output.append(mem2)
    return output
    # viewing the midimessages.
    # for i in output:
    #     print(i)
    # print(mid.ticks_per_beat)


def isolate_midi_channels(data: list[list[str, int, Union[int, float], int]]):
    """Return a tuple.
    [0]: dict: note_data, keys are channel
    [1]: same as 0 but for special notes
    [2]: set of channels that are used
    """
    midi_channels_so_far = {}  # contains data for all midi channels
    midi_channels_so_far_specific = {}
    midi_channel_nums = set()
    midi_channel_nums_specific = set()
    for note in data:
        if note[0] != 'note_on':
            continue
        if note[1] != 72:  # the non special note
            if note[3] not in midi_channel_nums:
                midi_channel_nums.add(note[4])
                midi_channels_so_far[note[4]] = []
            midi_channels_so_far[note[3]].append(note[2])
    return (midi_channels_so_far, midi_channel_nums)  # false error


def primary(dir: str) -> tuple[dict[str, list], set[str]]:
    """Do it
    """
    return isolate_midi_channels(process_midi(dir))


def get_tempo(mid):
    for msg in mid:  # Search for tempo
        if msg.type == 'set_tempo':
            return msg.tempo
    return 500000  # If not found return default tempo


def get_tempo_from_file(path):
    mid = MidiFile(path)
    return get_tempo(mid)


def mspt_to_spb(num: float) -> float:
    spb = num / 1000000
    return spb


def obtain_spb(path):
    mspt = get_tempo_from_file(path)
    return mspt_to_spb(mspt)

if __name__ == '__main__':
    # pm = process_midi('goof.mid')
    # print(get_tempo_from_file('goof.mid'))
    print(obtain_spb('Test_midifile.mid'))
    # bm = process_midi(pm)
    # bm = isolate_midi_channels(pm)
   #  pprint(pm)