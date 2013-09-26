# text.py

# A plaintext outputter for ChordBook

from _base import CbkOutputter

class text(CbkOutputter):

    def make_underline(self, s, char):
        """Take a string and underline char, return underlined version"""
        s = s + "\n" +(char * len(s)) + "\n\n"
        return s
    
    def make_tune(self, t):
        """Format an individual tune"""
        s = t.name
        s = self.make_underline(s, "-")

        seen = {}
        for section in t.structure:
            if section.title() in seen:
                s += section.title() + "\n\n"
            else:
                s += section.title() + ":\n"
                chunks = t.chunk_section(t.__getattribute__(section))
                for c in chunks:
                    s += c + "\n"
                s += "\n"
                seen[section.title()] = True

        s += "\n"

        return s

    def make_contents(self, b):
        """Return a string for the contents of the output"""
        c = b.get_contents()

        s = self.make_underline("Contents", "-")
        for title in c:
            s += title
            s += "\n"
        s += "\n"
        return s

    def make_header(self, b):
        """Return a string for the header of the output"""
        s = b.band + " (version " + b.version + ")"
        s = s.encode('utf-8')
        s = self.make_underline(s, "=")
        return s

    def make_book(self, b):
        """Output plaintext version of book data"""
        o = ""
        
        s = self.make_header(b)
        o += s

        s = self.make_contents(b)
        o += s

        for t in b.tunes:
            o += self.make_tune(t)

        print o
