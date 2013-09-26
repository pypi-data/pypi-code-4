# html.py

# An html outputter for Chordbook

from _base import CbkOutputter

class html(CbkOutputter):

    # FIXME - templating should be external
    # For now let's just put it here
    html_head = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>{{TITLE}}</title>
<!-- <link rel="stylesheet" href="{{CSS_LOC}}" type="text/css" /> -->
<style type="text/css">

body {
    font-family: Helvetica, Arial, sans-serif;
    background-color: #faf0e6;
    margin: 0% 5%;
}

h1, h2, h5, p {
    text-align: center;
    padding: 0%;
    margin: 0%;
}

h3 {
    padding: 0%;
    margin: 0%;
}

h4 {
    padding: 0% 2%;
    margin: 0%;
    background-color: #b0e0e6;
}

h4.repeat {
    background-color: #e6e0b0;
}

p {
    margin: 0px;
    padding: 0px;
}

table {
    width: 100%;
    padding: 0% 2%;
}

td {
    width: 15%; 
}

td.bar {
    border-right: 1px solid black;
}

td.directive {
    text-align: right;
}

.titlepage {

    background-color: #ffefd5;
    height: 100%;
    border: thin solid #000;
    margin-top: 10px;
}

.tune {
   
    page-break-before: always;
    background-color: #ffefd5;
    height: 100%;
    margin: 5% 0%;
    border: thin solid #000;

}

.chords {
    text-align: left;
    font-size: 20pt;
}

.spacer {
    height: 600px;
}

@media print {
    .spacer { display: none; }
}

</style>
</head>
<body>
"""

    html_foot = """
<p class="spacer">&nbsp;</p>
</body>
</html>
"""

    def strip_spaces(self, s):
        """Take a string and strip spaces from it"""
        s = s.replace(" ", "")
        return s

    def replace_entities(self, c):
        """Take a bar of chords, replace suitable HTML entities"""

        # replace '#' with &#x266f
        c = c.replace("#", "&#x266f;")
        # replace m7b5 with oslash
        c = c.replace("m7b5", "&oslash;7")
        # replace 'b' with &#x266d
        c = c.replace("b", "&#x266d;")
        # replace 'maj7' with &Delta;
        c = c.replace("maj7", "&Delta;")
        # replace 'LR' with left repeat sign
        # Eat the trailing space so it doesn't get its own td
        # Add trailing &nbsp; so it displays correctly
        c = c.replace("LR ", "&#x1d106;&nbsp;")
        # replace 'RR' with right repeat sign
        c = c.replace("RR", "&#x1d107;")
        # replace 'pause' with pause sign
        c = c.replace("pause", "&#x1d110;")

        return c

    def make_tune(self, t):
        """Format an individual tune"""
        s = "<div class=\"tune\">\n"
        anchor = self.strip_spaces(t.name)
        s += "<table><tr>"
        key = self.replace_entities(t.key)
        if hasattr(t, 'transpose'):
            key = self.replace_entities(t.transpose) + " (orig " + key + ")"
        s += "<td><a name=\"" + anchor + "\"></a><h3>" + t.name + \
                "</h3></td><td class=\"directive\"><i>" + t.time + \
                " " + key + "</i></td>\n"
        s += "</tr></table>"
        

        seen = {}
        for section in t.structure:
            if section.title() in seen:
                s += "<h4 class=\"repeat\">" + section.title() + "</h4>\n"
            else:
                s += "<h4>" + section.title() + "</h4>\n"
                s += "<table>\n"
                chunks = t.chunk_section(t.__getattribute__(section))
                for chunk in chunks:
                    s += "<tr>"
                    chords = t.process_section(chunk)
                    i = 0
                    for c in chords:
                        # Replace plaintext with musical HTML equivalents
                        c = self.replace_entities(c)
                        # Each bar is a td, last bar has no | on right
                        if (i < len(chords) - 1):
                            s += "<td class=\"bar\">"
                        else:
                            s+= "<td>"
                        # Spread chords within bar out using another table
                        s += "<table><tr>"
                        for p in c.split(" "):
                            s += "<td><p class=\"chords\">" + p + "</p></td>"
                        s += "</tr></table>"
                        # End of bar td
                        s += "</td>"
                        i += 1
                    s += "</tr>"
                seen[section.title()] = True
                s += "</table>\n"

        s +="</div>\n<p class=\"spacer\">&nbsp;</p>\n"

        return s

    def make_contents(self, b):
        """Make the contents part of the HTML output"""
        c = b.get_contents()

        s = "<h2>Contents</h2>\n<ol>"

        for title in c:
            name, credit = title.split("-", 1)
            anchor = self.strip_spaces(name)
            s += "<li><a href=\"#" + anchor + "\">" + name.strip() + "</a> - " + credit.strip() + "</li>\n"

        s += "</ol>\n"

        s += "</div>\n<p class=\"spacer\">&nbsp;</p>\n"

        return s

    def make_header(self, b):
        """Make the header part of the HTML output"""
        s = "<div class=\"titlepage\">\n"
        s += "<h1>" + b.band + "</h1>\n"
        s += "<p><i>Version " + b.version + "</i></p>\n"

        return s

    def make_book(self, b):
        """Output HTML version of book data"""

        o = self.html_head

        o = o.replace("{{TITLE}}", b.band)

        s = self.make_header(b)
        o += s

        s = self.make_contents(b)
        o += s

        for t in b.tunes:
            o += self.make_tune(t)

        o += self.html_foot

        print o


