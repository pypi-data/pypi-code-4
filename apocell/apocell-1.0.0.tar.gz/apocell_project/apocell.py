from bottle import route, run,template,request,get,post
import os
import scipy.io
import tempfile

@route('/')
def hello():
  return """
  This is a small webservice living mainly under <a href="/upload"> /upload </a>. It allows upload of cellprofilers .mat outputfiles for colocation and returns the for each data set and for each measurement inside this dataset

  the number of found speckles, the number of matched speckles and the number of nucleis. The methods accessible via /upload where the ones used in a publication and is thus included here without change for
  reproducibility <BR> A more general interface is available under <a href="/up"/> up </a> <BR><BR>
  """

@post('/up')
def up_mat_file():
    upload = request.files.get('upload')
    name,ext = os.path.splitext(upload.filename)

    f = tempfile.NamedTemporaryFile(delete=False,suffix='.jsn')
    mat = scipy.io.loadmat(upload.file,squeeze_me=True, chars_as_strings=True, mat_dtype=True,struct_as_record=False)

    data = mat['handles']



   # speckles = data.Measurements.__dict__['Speckles A3C']

    f.write("""<h2> All Measurements that are included in this file</h2> <BR>""")
    f.write(str(data.Measurements.__dict__.keys()))
    f.write("""<BR><BR>""")

    speckles = []
    for meas in data.Measurements.__dict__.keys():
        if "Speckles" in meas:
            speckles.append(meas)

    f.write("""<h2>First we show the number of objects, Speckles X.Number_Object_number<BR><BR></h2>""")


    for speckle in speckles:

        f.write("""{0}.Number_Object_number, Number of objects found for each measurement<BR>""".format(speckle))

        try:
            for measurement in mat['handles'].Measurements.__dict__[speckle].Number_Object_Number:
                try:
                    f.write(str(len(measurement)))
                except Exception as e:
                    f.write(str(0))
                    print e
                #for entry in measurement:
                #   f.write(str(entry) + '\t')

                #f.write('<BR><BR>')
                f.write('<BR>')
        except Exception as e:
            f.write(str(e))
            f.write('<BR>')


    f.write("""<h2>Parent Speckles: for all measurements we have True if collocation with nucleus could be found and False if not. By converting True to 1 and False to 0 and summation we get the number of collocations</h2><BR><BR>""")


    for speckle in speckles:
        f.write("""{0} Number of collocations found""".format(speckle))

        try:
            tempdata = mat['handles'].Measurements.__dict__[speckle].__dict__['Parent_Speckles L1']
            for measurement in tempdata:
                try:
                    f.write( str(scipy.sum( [ 1 if x > 0 else 0 for x in measurement] ) ))
                except Exception as e:
                    f.write(str(0))
                f.write("<BR>")
        except Exception as e:
            f.write(str(e))
            f.write('<BR>')


    f.write("""<h2>The total number of parent speckles are</h2><BR><BR>""")

    for speckle in speckles:
        f.write("""{0} Number of parent speckles found""".format(speckle))

        try:
            tempdata = mat['handles'].Measurements.__dict__[speckle].__dict__['Parent_Speckles L1']
            for measurement in tempdata:
                try:
                    f.write( str(len(measurement)) )
                except Exception as e:
                    f.write(str(0))
                f.write("<BR>")
        except Exception as e:
            f.write(str(e))
            f.write('<BR>')

    #f.write(""" Es gibt da noch ein "['handles'].Measurements.__dict__['Speckles L1'].__dict__['Children_Speckles A3C_Count'] das ganz spannend aussieht, ich weiss aber nicht was die Werte bedeuten ;) falls du die brauchst sind die fuer die jeweiligen Messreihen aufgelistet""")

    #try:
        #for measurement in mat['handles'].Measurements.__dict__['Speckles L1'].__dict__['Children_Speckles A3C_Count']:
            #for entry in measurement:
                #f.write(str(entry) + '\t')

            #f.write('<BR><BR>')
    #except Exception as e:
        #f.write(str(e))
        #f.write('<BR>')

    f.write("""<h2>Number of Nuclei</h2><BR><BR>""")
    try:
        for measurement in mat['handles'].Measurements.Nuclei.Number_Object_Number:
            f.write(str(len(measurement))+'\t')
    except Exception as e:
        f.write(str(e))
        f.write('<BR>')

    f.seek(0,0)
    return f

@get('/up')
def ask_up_mat_file():
    return """<form action="/up" method="post" enctype="multipart/form-data">
    Select a file: <input type="file" name="upload" />
      <input type="submit" value="Start upload" />
      </form>
"""

@post('/upload')
def upload_mat_file():
    upload = request.files.get('upload')
    name,ext = os.path.splitext(upload.filename)
    #if ext not in ('mat'):
        #return 'yeah... i have no idea what kind of file that is'

    f = tempfile.NamedTemporaryFile(delete=False,suffix='.jsn')
    mat = scipy.io.loadmat(upload.file,squeeze_me=True, chars_as_strings=True, mat_dtype=True,struct_as_record=False)

    data = mat['handles']
    speckles = data.Measurements.__dict__['Speckles A3C']

    f.write("""Falls an Format etwas geaendert werden soll, sag bescheid! :)<BR>""")
    #f.write("""als erstes: Speckles A3C.Number_Object_number, Datensaetze haben Format Messung 1 TAB Messung 2<BR>""")
    f.write("""als erstes: Speckles A3C.Number_Object_number, Anzahl der Eintraege<BR>""")

    try:
        for measurement in mat['handles'].Measurements.__dict__['Speckles A3C'].Number_Object_Number:
            try:
                f.write(str(len(measurement)))
            except Exception as e:
                f.write(str(0))
                print e
            #for entry in measurement:
            #   f.write(str(entry) + '\t')

            #f.write('<BR><BR>')
            f.write('<BR>')
    except Exception as e:
        f.write(str(e))
        f.write('<BR>')

    f.write("""als naechestes das gleiche fuer speckles L1<BR>""")

    try:
        for measurement in mat['handles'].Measurements.__dict__['Speckles L1'].Number_Object_Number:
            try:
                f.write(str(len(measurement)))
            except Exception as e:
                f.write(str(0))
                print e
            #for entry in measurement:
            #   f.write(str(entry) + '\t')

            #f.write('<BR><BR>')
            f.write('<BR>')
    except Exception as e:
        f.write(str(e))
        f.write('<BR>')

    f.write("""Parent Speckles L1, fuer jede Messreihe werden die Anzahl der Werte angezeigt die nicht Null sind<BR>""")

    try:
        tempdata = mat['handles'].Measurements.__dict__['Speckles A3C'].__dict__['Parent_Speckles L1']
        for measurement in tempdata:
            try:
                f.write( str(scipy.sum( [ 1 if x > 0 else 0 for x in measurement] ) ))
            except Exception as e:
                f.write(str(0))
            f.write("<BR>")
    except Exception as e:
        f.write(str(e))
        f.write('<BR>')

    f.write("""Die Gesamtanzahl der Parent Speckles L1, fuer jede Messreihe (einschliesslich null und nicht-null Werte) sind<BR>""")
    try:
        tempdata = mat['handles'].Measurements.__dict__['Speckles A3C'].__dict__['Parent_Speckles L1']
        for measurement in tempdata:
            try:
                f.write( str(len(measurement)) )
            except Exception as e:
                f.write(str(0))
            f.write("<BR>")
    except Exception as e:
        f.write(str(e))
        f.write('<BR>')

    f.write(""" Es gibt da noch ein "['handles'].Measurements.__dict__['Speckles L1'].__dict__['Children_Speckles A3C_Count'] das ganz spannend aussieht, ich weiss aber nicht was die Werte bedeuten ;) falls du die brauchst sind die fuer die jeweiligen Messreihen aufgelistet""")

    try:
        for measurement in mat['handles'].Measurements.__dict__['Speckles L1'].__dict__['Children_Speckles A3C_Count']:
            for entry in measurement:
                f.write(str(entry) + '\t')

            f.write('<BR><BR>')
    except Exception as e:
        f.write(str(e))
        f.write('<BR>')

    f.write("""Anzahl der Nuklei""")
    try:
        for measurement in mat['handles'].Measurements.Nuclei.Number_Object_Number:
            f.write(str(len(measurement))+'\t')
    except Exception as e:
        f.write(str(e))
        f.write('<BR>')

    f.seek(0,0)
    return f

@get('/upload')
def ask_upload_mat_file():
    return """<form action="/upload" method="post" enctype="multipart/form-data">
    Select a file: <input type="file" name="upload" />
      <input type="submit" value="Start upload" />
      </form>
"""

run(host='0.0.0.0',port=8000,debug=True,server='tornado')

