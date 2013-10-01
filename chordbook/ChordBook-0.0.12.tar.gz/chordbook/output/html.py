"""An HTML outputter for Chordbook"""

from chordbook.output._base import CbkOutputter

class CbkHtmlOutputter(CbkOutputter):

    """An HTML outputter for Chordbook"""

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

    def __init__(self, outputdir):
        CbkOutputter.__init__(self, outputdir)
        self.outputfilesuffix = "html"

    def replace_entities(self, chord):
        """Take a bar of chords, replace suitable HTML entities"""

        # replace '#' with &#x266f
        chord = chord.replace("#", "&#x266f;")
        # replace m7b5 with oslash
        chord = chord.replace("m7b5", "&oslash;7")
        # replace 'b' with &#x266d
        chord = chord.replace("b", "&#x266d;")
        # replace 'maj7' with &Delta;
        chord = chord.replace("maj7", "&Delta;")
        # replace 'LR' with left repeat sign
        # Eat the trailing space so it doesn't get its own td
        # Add trailing &nbsp; so it displays correctly
        chord = chord.replace("LR ", "&#x1d106;&nbsp;")
        # replace 'RR' with right repeat sign
        chord = chord.replace("RR", "&#x1d107;")
        # replace 'pause' with pause sign
        chord = chord.replace("pause", "&#x1d110;")

        return chord

    def make_tune(self, tune):
        """Format an individual tune"""
        html = "<div class=\"tune\">\n"
        anchor = tune.name.replace(" ", "")
        html += "<table><tr>"
        key = self.replace_entities(tune.key)
        if tune.transpose != "":
            key = self.replace_entities(tune.transpose) + " (orig " + key + ")"
        html += "<td><a name=\"" + anchor + "\"></a><h3>" + tune.name + \
                "</h3></td><td class=\"directive\"><i>" + tune.time + \
                " " + key + "</i></td>\n"
        html += "</tr></table>"
        

        seen = {}
        for section in tune.structure:
            if section.title() in seen:
                html += "<h4 class=\"repeat\">" + section.title() + "</h4>\n"
            else:
                html += "<h4>" + section.title() + "</h4>\n"
                html += "<table>\n"
                chunks = tune.chunk_section(tune.__getattribute__(section))
                for chunk in chunks:
                    html += "<tr>"
                    chords = tune.process_section(chunk)
                    i = 0
                    for crds in chords:
                        # Replace plaintext with musical HTML equivalents
                        crds = self.replace_entities(crds)
                        # Each bar is a td, last bar has no | on right
                        if (i < len(chords) - 1):
                            html += "<td class=\"bar\">"
                        else:
                            html += "<td>"
                        # Spread chords within bar out using another table
                        html += "<table><tr>"
                        for crd in crds.split(" "):
                            html += "<td><p class=\"chords\">" + crd + "</p></td>"
                        html += "</tr></table>"
                        # End of bar td
                        html += "</td>"
                        i += 1
                    html += "</tr>"
                seen[section.title()] = True
                html += "</table>\n"

        html += "</div>\n<p class=\"spacer\">&nbsp;</p>\n"

        return html

    def make_contents(self, book):
        """Make the contents part of the HTML output"""
        contents = book.get_contents()

        html = "<h2>Contents</h2>\n<ol>"

        for title in contents:
            name, credit = title.split("-", 1)
            anchor = name.replace(" ", "")
            html += "<li><a href=\"#" + anchor + "\">" + name.strip() + \
                    "</a> - " + credit.strip() + "</li>\n"

        html += "</ol>\n"

        html += "</div>\n<p class=\"spacer\">&nbsp;</p>\n"

        return html

    def make_header(self, book):
        """Make the header part of the HTML output"""
        html = "<div class=\"titlepage\">\n"
        html += "<h1>" + book.band + "</h1>\n"
        html += "<p><i>Version " + book.version + "</i></p>\n"

        return html

    def make_book(self, book):
        """Output HTML version of book data"""

        self.output = self.html_head

        self.output = self.output.replace("{{TITLE}}", book.band)

        self.output += self.make_header(book)

        self.output += self.make_contents(book)

        for tune in book.tunes:
            self.output += self.make_tune(tune)

        self.output += self.html_foot

        # Do actual output
        self.output_book(book.filename)

