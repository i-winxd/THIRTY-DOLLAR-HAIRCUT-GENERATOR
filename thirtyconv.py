import json
from dataclasses import dataclass
from fractions import Fraction
import math
from os.path import splitext
from typing import TypeVar, Optional

import mido
from pydantic import BaseModel

from function_from_command_line import run_function_from_cmdline
from midi_processor import Note, generate_bar_midi_representation, midi_to_representation, Bar, BarMidiRepresentation


class DebugConfig(BaseModel):
    no_pause_truncation: bool


class Config(BaseModel):
    velocity: bool
    percussion_file: str
    percussion_keywords: list[str]
    find_and_replace: bool


class FindAndReplace(BaseModel):
    find: str
    replace: str


class AllSettings(BaseModel):
    MAX_DENOMINATOR: int
    DEFAULT_INSTRUMENT: str
    SAMPLE_MAPPINGS: dict  # Modify this according to your sample mappings structure
    DEBUG_MODE: bool
    DEBUG_CONFIG: DebugConfig
    CONFIG: Config
    FIND_AND_REPLACE: list[FindAndReplace]


DEFAULT_CONFIGURATION = {
    "MAX_DENOMINATOR": 48,
    "DEFAULT_INSTRUMENT": "noteblock_harp",
    "SAMPLE_MAPPINGS": {},
    "DEBUG_MODE": False,
    "DEBUG_CONFIG": {
        "no_pause_truncation": True
    },
    "CONFIG": {
        "velocity": False,
        "percussion_file": "percussion.txt",
        "percussion_keywords": ["perc", "percussion", "drum", "drums", "percs"],
        "find_and_replace": True
    },
    "FIND_AND_REPLACE": [
        {"find": "kick", "replace": "🥁"},
        {"find": "dimrainsynth", "replace": "mariopaint_flower"}
    ]
}

configuration = AllSettings(**DEFAULT_CONFIGURATION)


def find_and_replace_multiple(text: str, replacements: list[FindAndReplace]) -> str:
    for find_replace_instance in replacements:
        text = text.replace(find_replace_instance.find, find_replace_instance.replace)
    return text


def o(text: str) -> str:
    return find_and_replace_multiple(text, configuration.FIND_AND_REPLACE)


def note_name_to_pitch(pitch: str) -> int:
    """Note name to pitch
    Return the note to subtract. For example, if a C is passed and our root note is A, then
    we need to add by C - cur.

    inst_name-C#5
    """
    pitch_relative = pitch[:-1]
    octave = int(pitch[-1])
    octave_offset = octave * 12
    note_dict = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6,
                 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}

    cur_note = note_dict.get(pitch_relative, None)  # a value from 0 to 11 representing offset
    if cur_note is None:
        print("Current note is invalid")
        return -1
    note_you_want_to_play = cur_note + octave_offset
    return note_you_want_to_play


def remove_comment(text: str) -> str:
    """Return a str such that if // in str,
    remove // and all text after // and strip
    both sides afterward.
    """
    slash_location = text.find('//')
    if slash_location == -1:
        return text
    else:
        return text[:slash_location].strip()


class ThirtyDollarCell:
    def __str__(self) -> str:
        return ""


@dataclass
class ThirtyDollarNote(ThirtyDollarCell):
    pitch: int  # the absolute pitch of this
    instrument: str  # the instrument this note belongs to
    volume: int  # the volume of this
    base_pitch: int

    def __str__(self) -> str:
        finalized_pitch = self.pitch - self.base_pitch
        if configuration.CONFIG.velocity:
            return f"{self.instrument}@{finalized_pitch}%{self.volume}"
        else:
            return f"{self.instrument}@{finalized_pitch}"


@dataclass
class ThirtyDollarTempoChange(ThirtyDollarCell):
    tempo: int

    def __str__(self) -> str:
        return f"!speed@{self.tempo}"


@dataclass
class ThirtyDollarCombine(ThirtyDollarCell):
    def __str__(self) -> str:
        return "!combine"


@dataclass
class ThirtyDollarBlank(ThirtyDollarCell):
    flag: int = 0

    def __str__(self) -> str:
        if not configuration.DEBUG_MODE:
            return "_pause"
        else:
            return f"_pause@{self.flag}"


def read_perc_file(path_to_file: str) -> dict[int, str]:
    """Read the percussion file.
    """
    with open(path_to_file, "r", encoding="UTF-8") as f:
        file_contents = f.read().split('\n')

    dict_so_far = {}
    for i, f_line in enumerate(file_contents):
        # guard clauses:
        f_line = remove_comment(f_line)
        split_line = f_line.split('|')
        if len(split_line) != 2:
            continue
        inst_name = split_line[1].strip()
        # add only if the instrument name is declared
        if len(inst_name) != 0:
            dict_so_far[i + 1] = inst_name
    return dict_so_far


@dataclass
class ThirtyDollarStop(ThirtyDollarCell):
    duration: int

    def __str__(self) -> str:
        return f"!stop@{self.duration}"


perc_map = read_perc_file(configuration.CONFIG.percussion_file)


@dataclass
class ThirtyDollarPercussionNote(ThirtyDollarCell):
    pitch: int
    volume: int

    def __str__(self) -> str:
        instrument = perc_map.get(self.pitch)
        if instrument is None:
            return ""
        return f"{instrument}%{self.volume}"


def get_instrument_from_track_name(name: str) -> str:
    """The naming convention for a track is:
    INST_NAME-C#5
    """
    split_name = name.split("-")
    if split_name != "":
        return split_name[0]
    else:
        return configuration.DEFAULT_INSTRUMENT


def get_base_pitch_from_track_name(name: str) -> int:
    """The naming convention for a track is:
    INST_NAME-C#5
    """
    name_after_split = name.split("-")
    if len(name_after_split) <= 1:
        return -1
    return note_name_to_pitch(name_after_split[-1])


T = TypeVar('T')


def flatten_2d_list(lst: list[list[T]]) -> list[T]:
    return [item for sublist in lst for item in sublist]


def run_conv(path_to_file: str, conf: Optional[AllSettings] = None) -> str:
    """Convert the path to the midi file stated here into a $30"""
    global configuration
    if conf is not None:
        configuration = conf
    else:
        configuration = DEFAULT_CONFIGURATION
    note_packs = generate_note_packs(path_to_file)
    # by default, I would flatten it
    flattened = flatten_2d_list(note_packs)
    # post-process the output
    flattened = post_process(flattened)
    inner_output = "|".join([s.__str__() for s in flattened])
    return inner_output


def run_conv_split(path_to_file: str, bars_per_export: int, conf: Optional[AllSettings] = None) -> list[str]:
    """Convert the path to the midi file stated here into a $30 in many fragments"""
    global configuration
    if conf is not None:
        configuration = conf
    else:
        configuration = DEFAULT_CONFIGURATION
    note_packs = generate_note_packs(path_to_file)
    total_bars = math.ceil(len(note_packs) / bars_per_export)
    opts: list[str] = []
    for i in range(total_bars):
        flattened = flatten_2d_list(note_packs[bars_per_export * i:bars_per_export * (i + 1)])
        flattened2 = post_process(flattened)
        inner_output = "|".join([s.__str__() for s in flattened2])
        opts.append(inner_output)
    return opts


def generate_note_packs(path_to_file: str) -> list[list[ThirtyDollarCell]]:
    midi_file = mido.MidiFile(path_to_file)
    midi_representation = midi_to_representation(midi_file)
    bar_midi_representation = generate_bar_midi_representation(midi_representation)
    note_packs = to_note_packs(bar_midi_representation)
    return note_packs


def to_note_packs(bar_midi_representation: BarMidiRepresentation) -> list[list[ThirtyDollarCell]]:
    note_packs: list[list[ThirtyDollarCell]] = []
    for bar in bar_midi_representation.bars:
        note_pack = bar_to_note_pack(bar)
        note_packs.append(note_pack)
    return note_packs


def post_process(flattened: list[ThirtyDollarCell]) -> list[ThirtyDollarCell]:
    """Cheapest operation ever"""
    # duplicate tempos - for all tempos, no two consecutive tempo changes may have the same tempo
    flattened = post_process_empty(flattened)
    flattened = post_process_tempo_dupes(flattened)
    flattened = post_process_consecutive_tempos(flattened)
    if not (configuration.DEBUG_MODE and configuration.DEBUG_CONFIG["no_pause_truncation"]):
        flattened = post_process_consecutive_blanks(flattened)
    return flattened


def post_process_empty(flattened: list[ThirtyDollarCell]) -> list[ThirtyDollarCell]:
    """MANDATORY: Removes all invalid ThirtyDollarCell instances"""
    return [x for x in flattened if x.__str__() != ""]


def post_process_consecutive_blanks(flattened: list[ThirtyDollarCell]) -> list[ThirtyDollarCell]:
    """.. -> [||2]"""
    count = 0
    result: list[ThirtyDollarCell] = []
    for cell in flattened:
        if isinstance(cell, ThirtyDollarBlank):
            count += 1
        else:
            if count > 1:
                result.append(ThirtyDollarStop(count))
            elif count == 1:
                result.append(ThirtyDollarBlank(1))
            result.append(cell)
            count = 0
    if count > 1:
        result.append(ThirtyDollarStop(count))
    elif count == 1:
        result.append(ThirtyDollarBlank(1))
    return result


def post_process_consecutive_tempos(flattened: list[ThirtyDollarCell]) -> list[ThirtyDollarCell]:
    """Should there be multiple b2b tempo changes, the last one remains."""
    remove_these = set()
    previous_was_tempo = False
    for i, cell in enumerate(flattened):
        is_tempo = isinstance(cell, ThirtyDollarTempoChange)
        if previous_was_tempo and is_tempo:
            assert (i > 0)
            remove_these.add(i - 1)
        previous_was_tempo = is_tempo
    return [x for i, x in enumerate(flattened) if i not in remove_these]


def post_process_tempo_dupes(flattened: list[ThirtyDollarCell]) -> list[ThirtyDollarCell]:
    """Removes redundant tempos (two-in-a-row)"""
    remove_these = set()
    last_tempo: int = -99
    # identical tempo runs
    for i, cell in enumerate(flattened):
        if isinstance(cell, ThirtyDollarTempoChange):
            if cell.tempo == last_tempo:
                remove_these.add(i)
            last_tempo = cell.tempo
    return [x for i, x in enumerate(flattened) if i not in remove_these]


def bar_to_note_pack(bar: Bar) -> list[ThirtyDollarCell]:
    flattened_notes: list[Note] = []
    for _, track in bar.tracks.items():
        flattened_notes.extend(track.notes)
    # absolutely no discreteness
    fractional_notes = [Fraction(x.beat).limit_denominator(configuration.MAX_DENOMINATOR) for x in flattened_notes]
    forced_denominator = math.lcm(*[x.denominator for x in fractional_notes])
    note_pack: list[list[ThirtyDollarCell]] = [[] for _ in range(0, forced_denominator * bar.time_signature.numerator)]
    note_pack_tempo_changes: list[list[ThirtyDollarCell]] = [[] for _ in range(0,
                                                                               forced_denominator *
                                                                               bar.time_signature.numerator)]

    # POPULATE NOTES
    for _, track in bar.tracks.items():
        instrument_name = get_instrument_from_track_name(track.track_name)
        if configuration.CONFIG.find_and_replace:
            instrument_name = o(instrument_name)
        base_pitch = get_base_pitch_from_track_name(track.track_name)
        if base_pitch == -1:
            base_pitch = configuration.SAMPLE_MAPPINGS.get(instrument_name, 60)
        for note in track.notes:
            numerator_obtained = numerator_of(note.beat, forced_denominator)
            if numerator_obtained >= len(note_pack):
                print(f"Note {note} is out of bounds, fix this bug")
            if instrument_name.lower() not in configuration.CONFIG.percussion_keywords:
                new_note = ThirtyDollarNote(note.note, instrument_name, note.velocity, base_pitch)
            else:
                new_note = ThirtyDollarPercussionNote(note.note, note.velocity)
            note_pack[min(numerator_obtained, len(note_pack) - 1)].append(
                new_note)
    # TEMPO CHANGES
    for tempo_change in bar.tempo_changes:
        numerator_obtained = numerator_of(tempo_change.beat, forced_denominator)
        if numerator_obtained >= len(note_pack_tempo_changes):
            print(f"Tempo change {tempo_change} is out of bounds, fix this bug")
        note_pack_tempo_changes[min(numerator_obtained, len(note_pack_tempo_changes) - 1)].append(
            ThirtyDollarTempoChange(round(tempo_change.new_bpm * forced_denominator)))

    # FILL BLANKS
    # for i in range(len(note_pack)):
    #     if not note_pack[i]:
    #         note_pack[i].append(ThirtyDollarBlank())

    first_note_has_a_tempo_change = len(note_pack_tempo_changes) > 0 and len(note_pack_tempo_changes[0]) > 0
    # COMPILE UP STUFF
    prelim_stuff = [ThirtyDollarTempoChange(
        round(bar.starting_tempo * forced_denominator))] if not first_note_has_a_tempo_change else []
    compiled_bar = compile_bar(note_pack, note_pack_tempo_changes)
    final_stuff = prelim_stuff + compiled_bar
    return final_stuff


def compile_bar(beat_packs: list[list[ThirtyDollarCell]], note_pack_tempo_changes: list[list[ThirtyDollarCell]]) -> \
        list[ThirtyDollarCell]:
    acc: list[ThirtyDollarCell] = []
    for beat_pack, beat_tempo_change in zip(beat_packs, note_pack_tempo_changes):
        assert len(acc) == 0 or not isinstance(acc[-1], ThirtyDollarCombine)
        if len(beat_tempo_change) > 0:
            acc.append(beat_tempo_change[-1])
        if len(beat_pack) > 0:
            for i, note in enumerate(beat_pack):
                acc.append(note)
                if i < len(beat_pack) - 1:
                    acc.append(ThirtyDollarCombine())
        else:
            acc.append(ThirtyDollarBlank(2))
    return acc


def numerator_of(decimal: float, forced_denominator: int) -> int:
    """Determines the value closest to decimal in the form RETURN / forced_denominator"""
    return round(decimal * forced_denominator)


def run_program(path_to_midi: str, path_to_output: str, conf: AllSettings) -> None:
    opt = run_conv(path_to_midi, conf)
    path_to_output = path_to_output
    with open(path_to_output, "w", encoding="UTF-8") as f_export:
        f_export.write(opt)


def run_program_2(path_to_midi: str, output_file_name: str, bars_per_file: int, conf: AllSettings) -> None:
    if bars_per_file < 10:
        bars_per_file = 10
    conv_result = run_conv_split(path_to_midi, bars_per_file, conf)
    name, ext = splitext(output_file_name)
    for i, txt in enumerate(conv_result):
        with open(f"{name}_{i + 1}.{ext}", "w", encoding="UTF-8") as f_export:
            f_export.write(txt)


def run_conversion(path_to_midi: str, output_file_name: str, config: str = "configuration.json",
                   bars_per_file: int = 0) -> None:
    """Converts a MIDI file into a Thirty-Dollar-Website compatible file.
    """
    with open(config, "r", encoding="UTF-8") as f:
        data = json.load(f)
    conf = AllSettings(**data)
    if bars_per_file <= 0:
        run_program(path_to_midi, output_file_name, conf)
    else:
        run_program_2(path_to_midi, output_file_name, bars_per_file, conf)


run_conversion.param_descriptions = {
    "path_to_midi": "The path to the MIDI file yu want to convert",
    "output_file_name": "The file name of the 30 dollar website file you want this program to export",
    "config": "Configuration settings. Check the README for what each field means",
    "bars_per_file": "Leave blank if you want all in a single file. "
                     "Otherwise, this program will split up your exported files into chunks to not "
                     "crash the thirty dollar website when you load them in."
}

if __name__ == '__main__':
    run_function_from_cmdline(run_conversion)
