"""
===================================================================================
    ===================================================================================
        Lista_Anidada.py [UNIDAD 2: HEAD FIRST PYTHON]
    ===================================================================================
===================================================================================

        Este es el modulo "Lista_Anidada.py", y proporciona una llamada a la función
    print_lol() que imprime las listas que pueden o no pueden incluir listas anidada.

===================================================================================
        CREAR MODULO (import Lista_anidada)
===================================================================================
    1: Crear una carpeta para tu modulo "Lista_Anidada.py" con un nombre referencia "Lista_anidada.py".
    2: Crear un archivo llamado "setup.py" en la carpeta creada.
    
            from distutils.core import setup
            
            setup(
                name = 'Lista_Anidada.py',
                version = '1.0.0',
                py_modules = ['Lista_Anidada.py'],
                author = 'Germán Paz Méndez',
                author_email = 'germanmendez1988@gmail.com',
                url = 'http://www.headfirstlabs.com',
                description = 'Un simple imprimidor de listas anidadas.',
            )

    3: Construye un archivo de distribución.

        $ python3 setup.py sdist
            ...

    4: Instala tu distribución en tu copia local de python.

        $ python3 setup.py install
===================================================================================
"""

def print_lol(the_list, level):
    '''
        (list) -> list

        This function takes a positional argument called “the_list", which is any
        Python list (of, possibly, nested lists). Each data item in the provided list
        is (recursively) printed to the screen on its own line.

        Actualización: second argument called “level" is used to insert tab-stops
        when a nested list is encountered.



        >>> movies = ["The Holy Grail", 1975, "Terry Jones & Terry Gilliam", 91,
        ["Graham Chapman",
        ["Michael Palin", "John Cleese", "Terry Gilliam", "Eric Idle", "Terry Jones"]]]
        
        >>> print_lol(movies)
        The Holy Grail
        1975
        Terry Jones & Terry Gilliam
        91
        Graham Chapman
        Michael Palin
        John Cleese
        Terry Gilliam
        Eric Idle
        Terry Jones
        
    '''
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, level + 1)
        else:
            for tab_stop in range(level):
                print("\t", end='')
            print(each_item)

            
movies = ["The Holy Grail", 1975, "Terry Jones & Terry Gilliam", 91,
        ["Graham Chapman",
        ["Michael Palin", "John Cleese", "Terry Gilliam", "Eric Idle", "Terry Jones"]]]
