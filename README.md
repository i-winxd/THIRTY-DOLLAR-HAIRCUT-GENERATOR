# MIDI to Thirty Dollar Website Converter

A Thirty Dollar Website MIDI Converter, one for https://thirtydollar.website/ from GDColon.

## How to set up the MIDI file

We strongly recommend you make your MIDI file in FL Studio. FL Studio has great tools for editing existing MIDI files by simply dragging them in. The Macro "prepare for MIDI export" is pretty useful. Some recent updates in version 21 makes them very easy to edit.

In FL Studio, a single item in the **channel rack** can count as a unique instrument.

Your MIDI **track names** determines what instrument each track maps to. Here's how your FL Studio should look like:

![](.thirty_README_images/cc431b95.png)

The syntax should look like this:

- `<INSTRUMENT_NAME>-<ROOT_NOTE>` (the dash `-` is the delimiter)

No root note will have it default to C5

- `INSTRUMENT_NAME` - the name of the instrument found in the files that the $30 website exports. If you use inspect element, it uses the `str=` tag.
- `ROOT_NOTE` - this should be set to the pitch of the sample found on the 30 dollar website without any pitch shifts. How you set this should be very similar to how you would set the root note for any sample you would drag into FL Studio. It should always match this regex: `[A-G][#b]\d` (e.g. `A#4`, `Bb6`, and you should know that `A#5 == Bb5` for the purposes of this program)

## Tempo Changes

Tempo changes via automating the tempo (search this up!) in FL Studio should be stored in the MIDI, though I strongly suggest that you have no gradual tempo changes, but rather have your tempo snap instantly. This program will still work if you have gradual tempo changes, but then you're just going to have a bunch of tempo changes crammed in your file. It should still sound the same, despite it being a bit messy.

## Time signature changes

If you have any time signature changes, **make sure** that they would make sense when written to sheet music. Never have a 4/4 bar actually last 3 bars long. I might fix this in the future. I rarely expect people to need to use this, so it isn't really supported.

## The Config File

Here's an example of the configuration file with annotations. You can specify which `configuration.json` to use when running the program.

```JSON
{
    "MAX_DENOMINATOR": 48,  // don't change
    "DEFAULT_INSTRUMENT": "noteblock_harp",
    "SAMPLE_MAPPINGS": {},  // don't change
    // adds pitches to all "empty" notes so you can see what
    // empty notes are made by this program and what
    // empty notes are on the site due to an instrument
    // not existing
    "DEBUG_MODE": false,
    "DEBUG_CONFIG": {
        "no_pause_truncation": true  // not relevant
    },
    "CONFIG": {
        // have MIDI note velocity impact 30$ site note velocity
        "velocity": false,  
        // path to the percussion file
        "percussion_file": "percussion.txt",  
        // ANY track with any of these names will be treated as 
        // a "percussion channel" (similar to channel 10 of MIDIs),
        // with each note mapping to what was declared in 
        // the percussion file
        "percussion_keywords": ["perc", "percussion", "drum", "drums", "percs"], 
        // find and replace will run on every "INSTRUMENT_NAME" 
        // during conversions; use this for last minute changes
        // or compatability needs
        "find_and_replace": false  
    },
    "FIND_AND_REPLACE": [
        // self-explainatory
        {"find": "kick", "replace": "🥁"},
        {"find": "dimrainsynth", "replace": "mariopaint_flower"}
    ]
}
```

## Installation and Setup

Make sure you have Python 3.7 or later installed; I strongly recommend getting the latest one. You have it installed if you can type `python` in the command prompt and have the console show up (on MacOS and Linux, you may need to use `python3` instead).

`cd` to this folder, and run `python -m pip install -r requirements.txt`.

Then, you can run the program by running this in your command line:

```
python thirtyconv.py [-h] [--config CONFIG] [--bars_per_file BARS_PER_FILE] path_to_midi output_file_name
```

Let's break the arguments down:

- **Path to MIDI File:**
  - The path to the MIDI file you want to convert.

- **Output File Name:**
  - The file name of the $30 website file that you want this program to export.

- **Configuration Settings:**
  - Configuration settings. Check the README for an explanation of each field.
  - Default: `configuration.json`

- **Bars per File:**
  - Leave blank if you want all in a single file. 
  - Otherwise, this program will split up your exported files into chunks to avoid crashing the $30 website when you load them in.
  - Default: Single file; any value below 10 will be set to 10

Here are some sample usages:

Converts `input.mid` to `output.txt` ($30)

```
python thirtyconv.py input.mid output.txt
```

Converts `input.mid` to `output.txt` ($30) with a custom configuration file

```
python thirtyconv.py --config custom.json input.mid output.txt
```

Converts `input.mid` to `output.txt` ($30) with a custom configuration file split into 50-bar segments

```
python thirtyconv.py --bars_per_file 50 --config custom.json input.mid output.txt
```

## The Thirty Dollar Website is too slow! What do I do?

Use an instance of the thirty dollar rewrite, such as this for now. Note that some instrument names are changed, hence why some settings here exist:

https://kleeder.de/files/moai2/%F0%9F%97%BF.html

No really, there is a memory leak with the animations on the original site. Until that gets fixed, this is your only solution.

Did you know that you can put custom sounds in that site?

- https://github.com/i-winxd/thirty-dollar-custom-fork
- https://github.com/i-winxd/thirty-dollar-custom-sounds-maker

