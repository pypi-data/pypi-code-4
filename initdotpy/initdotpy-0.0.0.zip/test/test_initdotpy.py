import pytest, os, sys
from mock import sentinel, patch, MagicMock


sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'examples_zip.zip'))


def test_example1():
    """Simplest test - importing modules"""
    import examples.example1 as package
    assert set(dir(package)).issuperset(['__all__', 'module1', 'module2'])
    assert sorted(package.__all__) == ['module1', 'module2']
    assert package.module1.__name__ == 'examples.example1.module1'
    assert package.module2.__name__ == 'examples.example1.module2'
    assert "auto_import" not in dir(package)
    assert "auto_import_contents" not in dir(package)


def test_example1_zip():
    """Test it works in a zipped package"""
    import examples_zip.example1 as package
    assert set(dir(package)).issuperset(['__all__', 'module1', 'module2'])
    assert sorted(package.__all__) == ['module1', 'module2']
    assert package.module1.__name__ == 'examples_zip.example1.module1'
    assert package.module2.__name__ == 'examples_zip.example1.module2'
    assert "auto_import" not in dir(package)
    assert "auto_import_contents" not in dir(package)


def test_example2():
    """Tests importing modules with __all__ non empty"""
    import examples.example2 as package
    assert set(dir(package)).issuperset(['__all__', 'fox', 'module3', 'module4'])
    assert sorted(package.__all__) == ['fox', 'module3', 'module4']
    assert package.module3.__name__ == 'examples.example2.module3'
    assert package.module4.__name__ == 'examples.example2.module4'
    assert package.fox() == 'fox'
    assert "auto_import" not in dir(package)
    assert "auto_import_contents" not in dir(package)


def test_example3():
    """Tests importing module contents"""
    import examples.example3 as package
    assert set(dir(package)).issuperset(['__all__', 'X', 'Y', 'Z', 'A', 'B', 'C'])
    assert sorted(package.__all__) == ['A', 'B', 'C', 'X', 'Y', 'Z']
    assert package.X == sentinel.X
    assert package.Y == sentinel.Y
    assert package.Z == sentinel.Z
    assert package.A == sentinel.A
    assert package.B == sentinel.B
    assert package.C == sentinel.C
    assert "auto_import" not in dir(package)
    assert "auto_import_contents" not in dir(package)


def test_example3_zip():
    """Tests importing module contents - in a zipped package"""
    import examples_zip.example3 as package
    assert set(dir(package)).issuperset(['__all__', 'X', 'Y', 'Z', 'A', 'B', 'C'])
    assert sorted(package.__all__) == ['A', 'B', 'C', 'X', 'Y', 'Z']
    assert package.X == sentinel.X
    assert package.Y == sentinel.Y
    assert package.Z == sentinel.Z
    assert package.A == sentinel.A
    assert package.B == sentinel.B
    assert package.C == sentinel.C
    assert "auto_import" not in dir(package)
    assert "auto_import_contents" not in dir(package)

    
def test_example4():
    """Tests importing module contents with no __all__ defined in one module"""
    with pytest.raises(RuntimeError) as err:
        import examples.example4 as package
    assert str(err.value) == "Module or package module7 does not define __all__"

    
def test_example5():
    """Tests importing module contents with a duplicate name"""
    with pytest.raises(RuntimeError) as err:
        import examples.example5 as package
    assert str(err.value) == "The following names, defined in module9, are already defined elsewhere: set(['Z'])"
    

def test_example6():
    """Tests using auto_import on multiple levels of packages"""
    import examples.example6 as package
    assert set(dir(package)).issuperset(['A', 'B', 'C', '__all__', 'module11'])
    assert sorted(package.__all__) == ['A', 'B', 'C', 'module11']
    assert "auto_import" not in dir(package)
    assert "auto_import_contents" not in dir(package)


def test_example7():
    """Test excluding a module"""
    import examples.example7 as package
    assert set(dir(package)).issuperset(['__all__', 'module14'])
    assert 'module13' not in dir(package)
    assert sorted(package.__all__) == ['module14']
    assert package.module14.__name__ == 'examples.example7.module14'
    assert "auto_import" not in dir(package)
    assert "auto_import_contents" not in dir(package)


def test_example8():
    """Test function is automatically removed even if it is renamed"""
    import examples.example8 as package
    assert set(dir(package)).issuperset(['__all__', 'module15', 'module16'])
    assert sorted(package.__all__) == ['module15', 'module16']
    assert package.module15.__name__ == 'examples.example8.module15'
    assert package.module16.__name__ == 'examples.example8.module16'
    assert 'some_other_name' not in dir(package)
    assert "auto_import" not in dir(package)
    assert "auto_import_contents" not in dir(package)


def test_example9():
    """Test function is automatically removed even if it is imported under several names"""
    import examples.example9 as package
    assert set(dir(package)).issuperset(['__all__', 'module17', 'module18'])
    assert sorted(package.__all__) == ['module17', 'module18']
    assert package.module17.__name__ == 'examples.example9.module17'
    assert package.module18.__name__ == 'examples.example9.module18'
    assert 'some_other_name' not in dir(package)
    assert 'any_name_you_like' not in dir(package)
    assert "auto_import" not in dir(package)
    assert "auto_import_contents" not in dir(package)


def test_example10():
    """Test function is not automatically removed if it is mentioned in __all__"""
    import examples.example10 as package
    assert set(dir(package)).issuperset(['__all__', 'module19', 'module20', 'this_one_gets_through'])
    assert sorted(package.__all__) == ['module19', 'module20', 'this_one_gets_through']
    assert package.module19.__name__ == 'examples.example10.module19'
    assert package.module20.__name__ == 'examples.example10.module20'
    assert 'some_other_name' not in dir(package)
    assert 'any_name_you_like' not in dir(package)
    assert 'this_one_gets_through' in dir(package)
    assert "auto_import" not in dir(package)
    assert "auto_import_contents" not in dir(package)


def test_example11():
    """Test combining auto_import and auto_import_contents in the same __init__.py"""
    import examples.example11 as package
    assert set(dir(package)).issuperset(['__all__', 'X', 'Y', 'Z', 'A', 'B', 'C'])
    assert set(dir(package)).issuperset(['__all__', 'module21', 'module22'])
    assert sorted(package.__all__) == ['A', 'B', 'C', 'X', 'Y', 'Z', 'module21', 'module22']
    assert package.X == sentinel.X
    assert package.Y == sentinel.Y
    assert package.Z == sentinel.Z
    assert package.A == sentinel.A
    assert package.B == sentinel.B
    assert package.C == sentinel.C
    assert package.module21.__name__ == 'examples.example11.module21'
    assert package.module22.__name__ == 'examples.example11.module22'
    assert "auto_import" not in dir(package)
    assert "auto_import_contents" not in dir(package)


def test_example12():
    """Test combining auto_import and auto_import_contents in the same __init__.py the other way around"""
    import examples.example12 as package
    assert set(dir(package)).issuperset(['__all__', 'X', 'Y', 'Z', 'A', 'B', 'C'])
    assert set(dir(package)).issuperset(['__all__', 'module23', 'module24'])
    assert sorted(package.__all__) == ['A', 'B', 'C', 'X', 'Y', 'Z', 'module23', 'module24']
    assert package.X == sentinel.X
    assert package.Y == sentinel.Y
    assert package.Z == sentinel.Z
    assert package.A == sentinel.A
    assert package.B == sentinel.B
    assert package.C == sentinel.C
    assert package.module23.__name__ == 'examples.example12.module23'
    assert package.module24.__name__ == 'examples.example12.module24'
    assert "auto_import" not in dir(package)
    assert "auto_import_contents" not in dir(package)
