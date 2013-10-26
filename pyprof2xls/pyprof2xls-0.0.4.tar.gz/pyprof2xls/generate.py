import StringIO
import pstats
import xlwt

descriptions = {
        'calls' : 'call count',
        'cumulative' : 'cumulative time',
        'file' : 'file name',
        'module' : 'file name',
        'pcalls' : 'primitive call count',
        'line' : 'line number',
        'name' : 'function name',
        'nfl' : 'name/file/line',
        'stdname' : 'standard name',
        'time' : 'internal time',
        }

fixedwidth_font = xlwt.Font()
fixedwidth_font.name = 'Courier New'
fixedwidth_font.height = 160

fixedwidth_style = xlwt.XFStyle()
fixedwidth_style.font = fixedwidth_font

header_font = xlwt.Font()
header_font.bold = True

header_style = xlwt.XFStyle()
header_style.font = header_font

default_width_ncalls = 9

def width_ncalls(s):
    if s:
        first_space = s.index(' ')
        if first_space > default_width_ncalls:
            return first_space
        else:
            return default_width_ncalls

def generate(prof_file, output_file):
    """
    Generates an excel output_file based on the profile data in prof_file.
    """
    wb = xlwt.Workbook()
    ws = wb.add_sheet('stats')
    
    data = StringIO.StringIO()
    s = pstats.Stats(prof_file, stream = data)
    s.sort_stats('cumulative').print_stats()
    
    pstats_output = data.getvalue().splitlines()
    assert "filename:lineno(function)" in pstats_output[6], "this should be header row"
    
    ## first few lines are metadata
    for i in xrange(6):
        ws.write(i, 0, pstats_output[i], fixedwidth_style)
    
    ## write header row
    ws.write(6, 0, 'ncalls', header_style)
    ws.write(6, 1, 'tottime', header_style)
    ws.write(6, 2, 'percall', header_style)
    ws.write(6, 3, 'cumtime', header_style)
    ws.write(6, 4, 'percall', header_style)
    ws.write(6, 5, 'filename:lineno(function', header_style)
    
    ## write actual data
    for i in xrange(7, len(pstats_output)-2):
        line = pstats_output[i]
    
        n = width_ncalls(line)
    
        try:
            ws.write(i, 0, line[0:(n+1)].strip())
            ws.write(i, 1, float(line[(n+1):(n+11)].strip()))
            ws.write(i, 2, float(line[(n+11):(n+19)].strip()))
            ws.write(i, 3, float(line[(n+19):(n+28)].strip()))
            ws.write(i, 4, float(line[(n+28):(n+36)].strip()))
            ws.write(i, 5, line[(n+36):].strip(), fixedwidth_style)
        except ValueError:
            print "ERROR in line %06d: %s" % (i, line)
    
    
    
    for sort_key in ['cumulative', 'time']:
        for stat_type in ['callees', 'callers']:
            arrow = {'callees' : '->', 'callers' : '<-'}[stat_type]
    
            ws = wb.add_sheet("%s by %s" % (stat_type, sort_key))
            ws.col(0).width = 20000
            pstats_output = get_data_for_stat_type_and_sorting(prof_file, stat_type, sort_key)
    
            header_row = None
            for i in xrange(0, 10):
                line = pstats_output[i]
                if 'ncalls' in line:
                    header_row = i
                    break
    
            if not header_row:
                raise Exception("no header row found in first 10 lines")
            
            for i in xrange(header_row):
                ws.write(i, 0, pstats_output[i], fixedwidth_style)
            
            # write headers
            ws.write(header_row, 1, 'ncalls', header_style)
            ws.write(header_row, 2, 'tottime', header_style)
            ws.write(header_row, 3, 'percall', header_style)
            
            first_data_row = pstats_output[header_row+1]
            assert arrow in first_data_row
            arrow_pos = first_data_row.index(arrow) + 2
            
            for i in xrange(header_row+1, len(pstats_output)-header_row-1):
                line = pstats_output[i]
        
                n = width_ncalls(line[(arrow_pos+1):])
                if n:
                    ss = [0, arrow_pos, arrow_pos+n, arrow_pos+n+9, arrow_pos+n+18]
                    try:
                        ws.write(i, 0, line[ss[0]:ss[1]].strip(), fixedwidth_style)
                        ws.write(i, 1, line[ss[1]+1:ss[2]].strip())
                        ws.write(i, 2, float(line[ss[2]+1:ss[3]].strip()))
                        ws.write(i, 3, float(line[ss[3]+1:ss[4]].strip()))
                        ws.write(i, 4, line[ss[4]+1:].strip(), fixedwidth_style)
                    except ValueError as e:
                        print "ERROR:", line, e
                        raise
                else:
                    ws.write(i, 0, line, fixedwidth_style)
                    ws.write(i, 1, ' ') # stop first cell from spilling over visually
    
    wb.save(output_file)

def get_data_for_stat_type_and_sorting(prof_file, stat_type, sort_key):
    data = StringIO.StringIO()
    s = pstats.Stats(prof_file, stream = data)

    if stat_type == 'callees':
        s.sort_stats(sort_key).print_callees()
    elif stat_type == 'callers':
        s.sort_stats(sort_key).print_callers()
    else:
        raise Exception("Stat type '%s'" % stat_type)

    return data.getvalue().splitlines()
