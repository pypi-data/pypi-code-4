# libcbk.py

# Library to read .cbk files

import json

class Tune(object):
    def __init__(self):
        pass 
    
    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)

    def get_keyname(self, c):
        """Take a key name which may have 'm' at end; strip 'm' if present"""
        if c[len(c) - 1] == "m":
            return c[:len(c) - 1]
        else:
            return c

    def do_transpose(self, c):
        """Take a chord and transpose it according to transpose element if present"""

        # Make sure we have a transpose attribute before we go any further
        if hasattr(self, 'transpose') == False:
            return c

        majors = ["A", "Bb", "B", "C", "Db", "D", "Eb", "E", "F", "F#", "G", "Ab"]
        minors = ["F#", "G", "Ab", "A", "Bb", "B", "C", "C#", "D", "Eb", "E", "F"]

        missing = { 'A#':'Bb', 'B#':'C', 'C#':'Db', 'D#':'Eb', 'E#':'F', 'G#':'Ab',
                    'Cb':'B', 'Db':'C#', 'Fb':'E', 'Gb':'F#' }

        # Preserve prefixed '('
        prefix = ""
        if c[0] == "(":
            prefix = "("
            c = c[1:]

        # Split c into chord and suffix if present
        # Look mum, no regexes :)
        minor = False
        c = c + "    " # guarantee we have enough chars for below to work
        index = 1
        if c[index] == "#" or c[index] == "b":
            index += 1
        if ((c[index] == "m") and (c[index:index+4] != "maj7")) or (c[index:index+3] == "dim"):
            minor = True
        chord = c[:index]
        suffix = c[index:].strip() # lose spurious w/s we just added
            
        # Move c that distance
        ki = majors
        if minor == True:
            ki = minors

        key = self.get_keyname(self.key)
        if key not in ki:
            key = missing[key]
        ikey = ki.index(key)
        transpose = self.get_keyname(self.transpose)
        if transpose not in ki:
            transpose = missing[transpose]
        tkey = ki.index(transpose)
        if chord not in ki:
            chord = missing[chord]
        ckey = ki.index(chord)

        chord = ki[(ckey + tkey - ikey) % 12]

        newchord = prefix + chord + suffix

        # Return new key
        return newchord

    def process_section(self, s):
        """Take a section and return an array of bars of chords"""
        inbars = s.split("|")
        outbars = []
        nonchords = ["LR", "RR"]

        for b in inbars:
            chords = b.strip().split(" ")
            outchords = []
            for c in chords:
                c = c.strip()
                if c in nonchords:
                    outchords.append(c)
                else:
                    outchords.append(self.do_transpose(c.strip()))
            outbars.append(" ".join(outchords))

        return outbars

    def chunk_section(self, s):
        """Take a section and return an array of 4 bar chunks"""
        # Transform "|:" and ":|" into LR and RR
        s = s.replace("|:", "LR")
        s = s.replace(":|", "RR")

        bars = s.split("|")

        chunks = []
        sep = "|"
        for i in range(0, len(bars), 4):
            # Avoid orphans
            if i+8 > len(bars):
                chunks.append(sep.join(bars[i:]).strip())
                break
            else:
                chunks.append(sep.join(bars[i:i+4]).strip())

        return chunks


class Book(object):
    def __init__(self):
        self.tunes = []

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)

    def get_contents(self):
        """Return an array of the names of the tunes"""

        c = []
        for t in self.tunes:
            title = t.name
            if hasattr(t, 'composer'):
                title += " - " + t.composer
            if hasattr(t, 'credit'):
                title += " - " + t.credit 
            c.append(title)
        c.sort()

        return c

def load_json(infile):
    json_data = json.load(infile)

    b = Book()

    b.band = json_data['band']
    b.version = json_data['version']

    for tune_data in json_data['tunes']:
        t = Tune()
        for k in tune_data.keys():
            t.__setattr__(k, tune_data[k])
        b.tunes.append(t)

    return b

if __name__ == '__main__':

    print "Transposition test."

    aeolian = ["A", "B", "C", "D", "E", "F", "G"]
    keys = []
    for k in aeolian:
        keys.append(k)
        keys.append(k + "#")
        keys.append(k + "b")

    suffixes = ["", "m", "7", "maj7", "sus4", "aug", "dim", "m7b5", "9", "13"]

    t = Tune()

    for inkey in keys:
        for outkey in keys:
            for chord in keys:
                for suffix in suffixes:
                    c = chord + suffix
                    t.key = inkey
                    t.transpose = outkey
                    out = t.do_transpose(c)
                    print "Original key: %s. Transposed to: %s. Chord %s becomes %s" % (inkey, outkey, c, out)

    print "Done testing."        


    
