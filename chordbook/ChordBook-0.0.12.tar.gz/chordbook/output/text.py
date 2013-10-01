"""A plaintext outputter for ChordBook"""

from chordbook.output._base import CbkOutputter


class CbkTextOutputter(CbkOutputter):
    """A plaintext outputter for ChordBook"""

    def __init__(self, outputdir):
        CbkOutputter.__init__(self, outputdir)
        self.outputfilesuffix = "txt"

    def make_underline(self, string, char):
        """Take a string and underline char, return underlined version"""
        string = string + "\n" +(char * len(string)) + "\n\n"
        return string
    
    def make_tune(self, tune):
        """Format an individual tune"""
        string = tune.name
        string = self.make_underline(string, "-")

        seen = {}
        for section in tune.structure:
            if section.title() in seen:
                string += section.title() + "\n\n"
            else:
                string += section.title() + ":\n"
                chunks = tune.chunk_section(tune.__getattribute__(section))
                for chunk in chunks:
                    chords = tune.process_section(chunk)
                    i = 0
                    for crds in chords:
                        crds = crds.replace("LR", "|:")
                        crds = crds.replace("RR", ":|")
                        string += crds
                        if (i < len(chords) - 1):
                            string += " | "
                        i += 1
                    string += "\n"
                seen[section.title()] = True

        string += "\n"

        return string

    def make_contents(self, book):
        """Return a string for the contents of the output"""
        contents = book.get_contents()

        string = self.make_underline("Contents", "-")
        for title in contents:
            string += title
            string += "\n"
        string += "\n"
        return string

    def make_header(self, book):
        """Return a string for the header of the output"""
        string = book.band + " (version " + book.version + ")"
        string = string.encode('utf-8')
        string = self.make_underline(string, "=")
        return string

    def make_book(self, book):
        """Output plaintext version of book data"""
        self.output = ""
        
        self.output += self.make_header(book)

        self.output += self.make_contents(book)

        for tune in book.tunes:
            self.output += self.make_tune(tune)

        self.output_book(book.filename)
