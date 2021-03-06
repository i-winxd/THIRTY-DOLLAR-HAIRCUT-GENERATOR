# DON'T YOU LECTURE ME WITH YOUR THIRTY DOLLAR HAIRCUT WEBSITE MIDI GENERATOR
MIDI -> 30 DOLLAR WEBSITE

Tired of clicking every panel on that site? This program's your solution.

**PLEASE CREDIT THIS TOOL IF YOU'RE MAKING ANY VIDEO ON ANY SITE USING THIS TOOL**

## How do I open this?

Download this by going to code > download ZIP. Extract everything to the same folder.

1. Install Python. I have a tutorial here: https://gist.github.com/i-winxd/0af33288536c155ac06690d3953156a4 though all you really need to do is download and install __Python 3.10 (You MUST use this version or higher otherwise the program will break)__ from the official Python website. If you already have Python installed, you can skip this step. **If you have multiple versions of Python installed, I'm leaving this up to you to resolve for yourself.**
2. Type `pip install mido` in the command prompt (you may need to restart your computer if you just installed python)
3. **If you're using windows:** Click on `run30dollar.bat` This runs the application in the command line interface. Note that if you haven't completed the two steps above, the program won't work (clicking on the bat file will literally do nothing). If you're curious what this file does, it just opens command prompt and autoinputs `py main.py`. By the way, you better have your files ready by this point. If you're not using windows, you should just download pycharm and run the program from there.

## Setting up your midi

### USING A PREEXISTING MIDI
I'm assuming you know a bit about midis. Each midi file
has different midi channels. The best way to figure them out
is to drag the file into fl studio, and look at the FL studio midi prompt.

![image](https://user-images.githubusercontent.com/31808925/151501848-020489ef-534b-4a35-8209-070f4ca38e86.png)

By the way, count channels from 1 here so no one gets confused. Now, you need to map each channel to an instrument on GDColon's website. Here's how you do it:

1. CREATE A NEW .TXT FILE (ANY NAME)

2. FORMAT IT LIKE THIS

![image](https://user-images.githubusercontent.com/31808925/151502169-e619bc55-c6c0-4c7a-aa8c-d1dca17a5b7c.png)

Definitions:
* inst name: the name of the instrument as visible in GDColon's website. If you don't know what instrument a sample is, here's how you find it

![image](https://user-images.githubusercontent.com/31808925/151502407-0fcef460-dc00-4978-9b64-48ca56b6d4c4.png)

(Open inspect element on a website by pressing F12)
* inst root note: the pitch of the sample when you right click it on the website. For example, ``noteblock_harp``'s root note is ``F#5``. And you must type it like that, exactly how it appears in FL Studio. ``C5`` is the middle C. We accept stuff like ``C#5, Db5, Ab4, G#4``, etc. The number at the end denotes the octave. We recommend you have perfect pitch to make this easy for you. If you don't have perfect pitch, consider searching up an online piano so you can compare pitches.
* semicolon: the character that splits the inst name and the inst root note.

If your inst name is ``nothing`` for a channel then that channel will be skipped.

### CREATING YOUR OWN MIDI
We will assume you know how to create that ``.txt`` file I mentioned above. Create your midi in FL Studio using MIDI out plugins (I'm expecting you to know how MIDI OUTs work in FL Studio. If you don't, search up how to use it.) Each channel maps to a seperate instrument you mapped in the ``.txt`` file you may or may not have created.

It is up to you to set the instrument to `perc` in channel 10.

MIDI out doesn't play sound unless you set stuff up. I would sequence your notes somewhere not in MIDI out, and then copy-paste your notes.

### Percussion

`perc` as an instrument will cause the channel in question to be treated as a percussion channel. This
completely changes how the MIDI file is interpreted - pitches are now
treated like indiviual instruments, with each pitch being mapped to
whatever is in `percussion.txt` (do not rename that file). **Typically, channel 10s are percussion channels (one-based).**

On MIDI and percussion:
https://usermanuals.finalemusic.com/SongWriter2012Win/Content/PercussionMaps.htm (you'll see the instrument names when working
with FL Studio's MIDI out when you set it to channel 10.)

And use the method in the above image to know what each "FL STUDIO PERCUSSION INSTRUMENT" actually is on GD's website.

![image](https://user-images.githubusercontent.com/31808925/151503801-1dbdd7a7-830d-4c65-a106-d3b5b08a3072.png)

If you choose a note that isn't in the dictionary I stated it will just be ignored (the program won't crash).

## How to use this program
1. Click on the midi file you want to import when prompted. If you don't, the program will stop and shut down.
2. Answer the prompts the program gives you.

* **FORCE STOP**: If you say "y", this program will insert an ???? before every note (excluding times where >=2 notes play at the same time). In other words, it prevents unwanted sustaining. Remember the last time you held that right pedal down playing the piano? This prevents it, but increases the note count.
* **BPM MULTIPLIER**: You should at least say ``4``, or ``8`` if your song is really fast. Basically, this multiplies the bpm by the number you say. Whatever you say should be a power of 2. Because GDcolon's website is limited, this program automatically quantisizes notes to the nearest beat; the higher the **BPM MULT**, the less quantisizing is done.
* **BPM_DIV (type 0.5 if you want...)**: Sometimes, this program generates a chart that has a tempo way too high (this is VERY different from BPM multiplier). Type 0.5 if you want the exported chart to have a tempo half of it would be, or 2.0 if you want it double. Think of it like youtube's playback slider - this ONLY affects the tempo that shows up when you import your (moai emoji) file into GDColon's website.
* **MAXIMUM BEATS** - how long in beats should this song last AFTER BPM multipliers are applied. I suggest 850.

3. Click on the corresponding ``.txt`` file you created (the ``.txt`` file is the file that lets you know what instruments you want each midi channel mapped to... scroll up to see where I explained that). If you don't and just decide to close the filer opener, I'll map channel 1 to ``noteblock_banjo`` and channel 2 to ``mariopaint_car``.
4. This program will close afterwards and you should see your new .(moai emoji) file in the same directory as the .py or exe file. The file will always be named based off your midi file you opened.

## NOTES
* You can modify my hard coded stuff if you want.
* I wrote this at 2 in the morning. If there is anything confusing, let me know VIA my twitter DMs.
* If your MIDI isn't tailored for this site it will likely sound terrible (note because the timing is wrong, because the midi was likely not meant for that).
