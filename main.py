import random
import mido


# EVOLUTION SECTION


def new_individual():
    """
    :return: random note in interval from 60 to 71
    """
    return random.choice(range(60, 72))


def init_population(melody: mido.MidiFile):
    """
    :param melody: input melody
    :return: population with 70 random chords that are corresponds the melody's tonic
    """
    t = tonic(melody)[-1]
    population = []
    for i in range(70):
        note = new_individual()
        if t == 'm':
            population.append(minor_chord_list(note, random.choice(range(-2, 0))))
        else:
            population.append(major_chord_list(note, random.choice(range(-2, 0))))
    return population


def fitness(chord: list, note: int, melody: mido.MidiFile):
    """
    :param chord: 3-notes chord
    :param note: leading note that is going to be played just after the chord
    :param melody: input melody
    :return: fitness int value for the chord

    Significance scale (from most significant to less significant):
    1. Chord corresponds the tonic
    2. Chord is not too far and not too close to the note
    3. 1st and 3rd notes of the chord are the same as the leading note
    4. 1st note of the chord are the same as the leading note
    5. 2nd or 3rd notes of the chord are the same as the leading note
    6. Others
    7. Chord contains a key that is located next to the leading note
    """
    tonic_notes = get_tonic_notes(melody)
    if note - 1 in chord or note + 1 in chord:
        return 0
    if chord[0] in tonic_notes:
        if 11 < note - chord[0] < 24:
            if note_in_interval(chord[0]) == note_in_interval(note) and \
                    note_in_interval(chord[2]) == note_in_interval(note):
                return 40
            elif note_in_interval(chord[0]) == note_in_interval(note):
                return 39
            elif note_in_interval(chord[1]) == note_in_interval(note) or \
                    note_in_interval(chord[2]) == note_in_interval(note):
                return 38
            else:
                return 37
        else:
            if note_in_interval(chord[0]) == note_in_interval(note) and \
                    note_in_interval(chord[2]) == note_in_interval(note):
                return 30
            elif note_in_interval(chord[0]) == note_in_interval(note):
                return 29
            elif note_in_interval(chord[1]) == note_in_interval(note) or \
                    note_in_interval(chord[2]) == note_in_interval(note):
                return 28
            else:
                return 27
    else:
        if 11 < note - chord[0] < 24:
            if note_in_interval(chord[0]) == note_in_interval(note) and \
                    note_in_interval(chord[2]) == note_in_interval(note):
                return 20
            elif note_in_interval(chord[0]) == note_in_interval(note):
                return 19
            elif note_in_interval(chord[1]) == note_in_interval(note) or \
                    note_in_interval(chord[2]) == note_in_interval(note):
                return 18
            else:
                return 17
        else:
            if note_in_interval(chord[0]) == note_in_interval(note) and \
                    note_in_interval(chord[2]) == note_in_interval(note):
                return 10
            elif note_in_interval(chord[0]) == note_in_interval(note):
                return 9
            elif note_in_interval(chord[1]) == note_in_interval(note) or \
                    note_in_interval(chord[2]) == note_in_interval(note):
                return 8
            else:
                return 7


def terminate(generation: int):
    """
    :param generation: number of the current generation
    :return: terminate or not
    """
    return generation > 15


def selection(population: list, note: int, melody: mido.MidiFile):
    """
    Worst 1% of the population (according to the fitness) dies
    :param population: the current population of chords
    :param note: leading note that is going to be played just after the chord
    :param melody: input melody
    """
    population.sort(key=lambda x: fitness(x, note, melody), reverse=True)
    for i in range(len(population) // 10):
        population.pop()


def crossover(population: list):
    """
    The population becomes 30% larger
    :param population: the current population of chords
    """
    for i in range(len(population) // 3):
        parent1, parent2 = random.choice(population), random.choice(population)
        population.append([parent1[0], parent1[1], parent2[2]])


def mutation(population: list):
    """
    Every chord in population can mutate with a probability of 10%
    :param population: the current population of chords
    """
    for chord in population:
        if random.randint(0, 19) == 19:
            chord[random.randint(0, 2)] += 1
        elif random.randint(0, 19) == 18:
            chord[random.randint(0, 2)] -= 1


def evolution(note: int, melody: mido.MidiFile):
    """
    :param note: leading note that is going to be played just after the chord
    :param melody: input melody
    :return: the best chord after the evolution process ends
    """
    generation = 0
    population = init_population(melody)
    while not terminate(generation):
        selection(population, note, melody)
        crossover(population)
        mutation(population)
        generation += 1
    population.sort(key=lambda x: fitness(x, note, melody), reverse=True)
    return population[0]


# MUSIC SECTION


def note_on(note: int, time: int, velocity: int):
    """
    :param note: a note
    :param time: time when the note turns on
    :param velocity: velocity of the note
    :return: message with this note turning on in the mido format
    """
    return mido.Message('note_on', note=note, velocity=velocity, time=time)


def note_off(note: int, time: int, velocity: int):
    """
    :param note: a note
    :param time: time when the note turns off
    :param velocity: velocity of the note
    :return: message with this note turning off in the mido format
    """
    return mido.Message('note_off', note=note, velocity=velocity, time=time)


def octave_shift(num: int):
    """
    :param num: number of shifts
    :return: how much to add to the note to get this note in another octave
    """
    return num * 12


def build_chord(chord: list, time_on: int, time_off: int, velocity_on: int):
    """
    :param chord: 3-notes chord (3 numbers in the chord-list)
    :param time_on: time when the chord turns on
    :param time_off: time when the chord turns off
    :param velocity_on: velocity of the chord when it turns on
    :return: list of messages with this notes turning on and off in the mido format
    """
    return [note_on(chord[0], time_on, velocity_on),
            note_on(chord[1], time_on, velocity_on),
            note_on(chord[2], time_on, velocity_on),
            note_off(chord[0], time_off, 0),
            note_off(chord[1], time_off, 0),
            note_off(chord[2], time_off, 0)]


def major_chord_list(left_note: int, shift: int):
    """
    :param left_note: note from which the chord will be built
    :param shift: shift of the chord between octaves
    :return: major chord
    """
    return [left_note + octave_shift(shift), left_note + 4 + octave_shift(shift), left_note + 7 + octave_shift(shift)]


def minor_chord_list(left_note: int, shift: int):
    """
    :param left_note: note from which the chord will be built
    :param shift: shift of the chord between octaves
    :return: minor chord
    """
    return [left_note + octave_shift(shift), left_note + 3 + octave_shift(shift), left_note + 7 + octave_shift(shift)]


def note_in_interval(note: int):
    """
    :param note: a note
    :return: the same note in interval from 60 to 71
    """
    new_note = note
    while new_note > 71:
        new_note -= 12
    while new_note < 60:
        new_note += 12
    return new_note


def split_notes(melody: mido.MidiFile):  # 1. Split notes
    """
    :param melody: input melody
    :return: notes that this melody contains
    """
    notes = set()
    for i in range(2, len(melody.tracks[1]) - 1):
        note = melody.tracks[1][i].note
        notes.add(note_in_interval(note))
    return list(notes)


def get_last_note(melody: mido.MidiFile):
    """
    :param melody: input melody
    :return: the last note of the melody
    """
    return melody.tracks[1][-2].note


def find_black_keys(notes: list):  # 2. Find black keys
    """
    :param notes: notes that the melody contains
    :return:
    """
    black_keys = []
    for note in notes:
        if note not in WHITE_KEYS.values():
            black_keys.append(note)
    return black_keys


def complement_black_keys(notes: list):  # 3. Complement black keys
    """
    Some black notes may be not used in the melody, so it is important to complement them to determine the
    tonic correctly: SHARPS_ORDER and FLATS_ORDER lists are used for this
    :param notes: notes that the melody contains
    :return: complement black keys
    """
    black_keys = find_black_keys(notes)
    if len(black_keys) != 0:
        last_tonic_identifier_found = False
        if black_keys[0] - 1 in notes:
            for i in range(6, -1, -1):
                if last_tonic_identifier_found:
                    if FLATS_ORDER[i] not in black_keys:
                        black_keys.append(FLATS_ORDER[i])
                elif FLATS_ORDER[i] in black_keys:
                    last_tonic_identifier_found = True
        else:
            for i in range(6, -1, -1):
                if last_tonic_identifier_found:
                    if SHARPS_ORDER[i] not in black_keys:
                        black_keys.append(SHARPS_ORDER[i])
                elif SHARPS_ORDER[i] in black_keys:
                    last_tonic_identifier_found = True
    return black_keys


def find_sharps_flats(notes: list):  # 4. Find number of sharps or flats
    """
    :param notes: notes that the melody contains
    :return: how many sharps or flats the melody contains (example: '4#')
    """
    black_keys = complement_black_keys(notes)
    if len(black_keys) == 0:
        return '0'
    are_flats = False
    for key in black_keys:  # Determine if black keys are flats
        if key - 1 in notes:
            are_flats = True
            break
    if are_flats:
        return str(len(black_keys)) + 'b'
    else:
        return str(len(black_keys)) + '#'


def determine_note(note: str):
    """
    :param note: a note in string notation (example: 'A', 'Gb')
    :return: this note in integer notation
    """
    if note in WHITE_KEYS.keys():
        return WHITE_KEYS[note]
    else:
        return BLACK_KEYS[note]


def get_major_minor_notes(notes: list):
    """
    After the number of sharps or flats got known, it is possible to determine 2 tonics, one of which is
    a true one for the current melody. This function finds notes of this 2 tonics (major and minor) that can be used
    for chords composing
    :param notes: notes that the melody contains
    :return: major and minor notes
    """
    sf = find_sharps_flats(notes)
    major_notes = [determine_note(TONICS[sf][0][:-1])]
    minor_notes = [determine_note(TONICS[sf][1][:-1])]
    for i in range(6):
        major_notes.append(major_notes[i] + OFFSETS['M'][i])
        minor_notes.append(minor_notes[i] + OFFSETS['m'][i])
    return major_notes, minor_notes


def tonic(melody: mido.MidiFile):  # 5. Determine tonic
    """
    The function determines which one of the possible tonics is true for the melody
    by analyzing tonic, dominant, median and subdominant notes of the tonics
    :param melody: input melody
    :return: tonic of the melody
    """
    last_note = get_last_note(melody)
    notes = split_notes(melody)
    major_notes, minor_notes = get_major_minor_notes(notes)
    if last_note == major_notes[0]:
        return TONICS[find_sharps_flats(notes)][0]
    elif last_note == minor_notes[0]:
        return TONICS[find_sharps_flats(notes)][1]
    elif last_note == major_notes[4]:
        return TONICS[find_sharps_flats(notes)][0]
    elif last_note == minor_notes[4]:
        return TONICS[find_sharps_flats(notes)][1]
    elif last_note == major_notes[2]:
        return TONICS[find_sharps_flats(notes)][0]
    elif last_note == minor_notes[2]:
        return TONICS[find_sharps_flats(notes)][1]
    elif last_note == major_notes[3]:
        return TONICS[find_sharps_flats(notes)][0]
    elif last_note == minor_notes[3]:
        return TONICS[find_sharps_flats(notes)][1]
    else:
        return TONICS[find_sharps_flats(notes)][random.randint(0, 1)]


def get_tonic_notes(melody: mido.MidiFile):  # 6. Get tonic notes: chords should start with this notes
    """
    :param melody: input melody
    :return: tonic notes corresponding to the melody
    """
    t = tonic(melody)
    offset = OFFSETS[t[-1]]
    notes = [determine_note(t[:-1])]
    for i in range(6):
        notes.append(note_in_interval(notes[i] + offset[i]))
    return notes


def number_of_beats(melody: mido.MidiFile):  # 7. Determine number of beats
    """
    :param melody:
    :return: number of beats in the melody
    """
    time = 0
    for i in range(2, len(melody.tracks[1]) - 1):
        time += melody.tracks[1][i].time
    return time // melody.ticks_per_beat


def melody_evolution(melody: mido.MidiFile, velocity_on: int):
    """
    For each chord the 'evolution' function calls. The best chord supplements the accompaniment
    :param melody: input melody
    :param velocity_on: velocity of the chord when it turns on
    :return: accompaniment
    """
    melody_time = 0
    accompaniment_time = 0
    note_counter = 2
    chords = mido.MidiTrack()
    chords.append(melody.tracks[1][0])
    chords.append(melody.tracks[1][1])
    for i in range(number_of_beats(melody)):
        first_note = melody.tracks[1][note_counter].note
        accompaniment_time += melody.ticks_per_beat
        while melody_time < accompaniment_time and note_counter < len(melody.tracks[1]) - 2:
            melody_time += melody.tracks[1][note_counter].time
            note_counter += 1
        chord = evolution(first_note, melody)
        chords.extend(build_chord(chord, 0, melody.ticks_per_beat // 3, velocity_on))
    chords.append(melody.tracks[1][-1])
    accompaniment = mido.MidiFile(type=1, ticks_per_beat=melody.ticks_per_beat)
    accompaniment.tracks.append(melody.tracks[0])
    accompaniment.tracks.append(chords)
    return accompaniment


def merge_tracks(melody: mido.MidiFile, accompaniment: mido.MidiFile):
    """
    :param melody: input melody
    :param accompaniment: accompaniment that was built with evolution
    :return: composition of the melody and the accompaniment
    """
    composition = mido.MidiFile(type=1, ticks_per_beat=melody.ticks_per_beat)
    composition.tracks.extend(accompaniment.tracks)
    composition.tracks.extend(melody.tracks)
    return composition


# CONSTANTS


WHITE_KEYS = {'C': 60, 'D': 62, 'E': 64, 'F': 65, 'G': 67, 'A': 69, 'B': 71}
BLACK_KEYS = {'C#': 61, 'Db': 61, 'D#': 63, 'Eb': 63, 'F#': 66, 'Gb': 66, 'G#': 68, 'Ab': 68, 'A#': 70, 'Bb': 70}

TONICS = {'0': ['CM', 'Am'],
          '1#': ['GM', 'Em'], '2#': ['DM', 'Bm'], '3#': ['AM', 'F#m'], '4#': ['EM', 'C#m'],
          '5#': ['BM', 'G#m'], '6#': ['F#M', 'D#m'], '7#': ['C#M', 'A#m'],
          '1b': ['FM', 'Dm'], '2b': ['BbM', 'Gm'], '3b': ['EbM', 'Cm'], '4b': ['AbM', 'Fm'],
          '5b': ['DbM', 'Bbm'], '6b': ['GbM', 'Ebm'], '7b': ['CbM', 'Abm']}

OFFSETS = {'M': [2, 2, 1, 2, 2, 2, 1], 'm': [2, 1, 2, 2, 1, 2, 2]}

SHARPS_ORDER = [66, 61, 68, 63, 70, 65, 60]
FLATS_ORDER = [70, 63, 68, 61, 66, 71, 64]


# VARIABLES


input0 = mido.MidiFile('barbiegirl_mono.mid', clip=True)
input1 = mido.MidiFile('input1.mid', clip=True)
input2 = mido.MidiFile('input2.mid', clip=True)
input3 = mido.MidiFile('input3.mid', clip=True)

song = input0

song_notes = split_notes(song)
print('notes:', song_notes)
print('black keys:', find_black_keys(song_notes))
print('complement black keys:', complement_black_keys(song_notes))
print('sharps/flats:', find_sharps_flats(song_notes))
print('possible tonics:', TONICS[find_sharps_flats(song_notes)])
print('tonic:', tonic(song))
print('tonic notes:', get_tonic_notes(song))
print('number of beats:', number_of_beats(song))

print('\nevolution is happening')
acc = melody_evolution(song, 50)
print('evolution is happened')
comp = merge_tracks(song, acc)
comp.save('new_song.mid')
print('the composition is saved successfully')
