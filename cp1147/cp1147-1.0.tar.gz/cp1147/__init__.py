import codecs    

def cp1147_search_function(s):
    if s!="cp1147": 
        return None
    try:         
        import cp1147
    except ImportError:
         return None
    codec = cp1147.Codec()    
    return codecs.CodecInfo( name='cp1147',
                             encode=codec.encode,
                             decode=codec.decode,
                             streamreader=cp1147.StreamReader,
                             streamwriter=cp1147.StreamWriter)
  
codecs.register(cp1147_search_function)
