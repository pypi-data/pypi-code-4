from django.db import models
from django.test import TestCase
from principals.fields import PrincipalField


# To run the tests:
# python manage.py test principals.PrincipalField


class SinglePrinc(models.Model):
    name = models.CharField(max_length=255)
    principal = PrincipalField(default=False)


class MultiplePrinc(models.Model):
    name = models.CharField(max_length=255)
    principal_1 = PrincipalField()
    principal_2 = PrincipalField()
    principal_3 = PrincipalField()


class Director(models.Model):
    name = models.CharField(max_length=255)


class Movie(models.Model):
    title = models.CharField(max_length=255)
    director = models.ForeignKey(Director, related_name='movies')
    genre = models.CharField(max_length=255)
    principal = PrincipalField(collection=('director',))
    principal_in_genre = PrincipalField(collection=('director', 'genre'))


class PrincipalField(TestCase):

    def test_principal_item(self):
        a = SinglePrinc.objects.create(name="a", principal=False)
        b = SinglePrinc.objects.create(name="b", principal=False)
        c = SinglePrinc.objects.create(name="c", principal=False)
        self.assertEqual( SinglePrinc.objects.filter(principal=True).count(), 0, "No item is principal by default" )
        a.principal = True
        a.save()
        self.assertEqual( SinglePrinc.objects.get(principal=True).name, 'a', "Can set principal=True" )
        b.principal = True
        b.save()
        self.assertEqual( SinglePrinc.objects.filter(principal=True).count(), 1, "Only one principal item at a time" )
        self.assertEqual( SinglePrinc.objects.get(principal=True).name, 'b', "Principal item is now 'b'" )

    def test_multiple_principal_fields(self):
        # Create 3 new objects
        a = MultiplePrinc.objects.create(name='a')
        b = MultiplePrinc.objects.create(name='b')
        c = MultiplePrinc.objects.create(name='c')
        # define them as principal and save them
        a.principal_1 = True
        a.save()
        b.principal_2 = True
        b.save()
        c.principal_3 = True
        c.save()
        self.assertEqual( MultiplePrinc.objects.get(principal_1=True).name, 'a', "Can set principal_1 correctly" )
        self.assertEqual( MultiplePrinc.objects.get(principal_2=True).name, 'b', "Can set principal_2 correctly" )
        self.assertEqual( MultiplePrinc.objects.get(principal_3=True).name, 'c', "Can set principal_3 correctly" )
        # Get new instances, and update them
        a = MultiplePrinc.objects.get(name='a')
        a.principal_3 = True
        a.save()
        c = MultiplePrinc.objects.get(name='c')
        c.principal_2 = True
        c.save()
        # Things just changed back there, so get new instances again
        a = MultiplePrinc.objects.get(name='a')
        c = MultiplePrinc.objects.get(name='c')
        self.assertTrue(a.principal_1, "'a' is still principal 1")
        self.assertTrue(a.principal_3, "'a' is now principal 3")
        self.assertTrue(c.principal_2, "'c' is now principal 2")
        self.assertTrue(not c.principal_3, "'c' is no longer principal 3")

    def test_collection(self):
        spielberg = Director.objects.create(name='Steven Spielberg')
        gilliam = Director.objects.create(name='Terry Gilliam')

        s1 = spielberg.movies.create(title="Jaws", genre="Thriller")
        s2 = spielberg.movies.create(title="Lincoln", genre="Drama")
        s3 = spielberg.movies.create(title="Minority Report", genre="Sci-Fi")
        s4 = spielberg.movies.create(title="War of The Worlds", genre="Sci-Fi")

        g1 = gilliam.movies.create(title="Time Bandits", genre="Fantasy")
        g2 = gilliam.movies.create(title="12 Monkeys", genre="Sci-Fi")
        g3 = gilliam.movies.create(title="Fear & Loathing in Las Vegas", genre="Drama")
        g4 = gilliam.movies.create(title="Life of Brian", genre="Comedy")
        g5 = gilliam.movies.create(title="Monty Python's THe Meaning of Life", genre="Comedy")

        s1.principal = True
        s1.principal_in_genre = True
        s1.save()

        s4.principal_in_genre = True
        s4.save()

        g1.principal_in_genre = True
        g1.save()

        g5.principal = True
        g5.principal_in_genre = True
        g5.save()

        self.assertEqual( Movie.objects.filter(principal_in_genre=True).count(), 4, "Four movies are principal in their respective director/genre set" )

        self.assertEqual( Movie.objects.filter(principal=True).count(), 2, "Two movies are principal in their respective director set")

        s4.principal = True
        s4.save()

        self.assertEqual( Movie.objects.filter(principal_in_genre=True).count(), 4, "Four movies are principal in their respective director/genre set" )

        self.assertEqual( Movie.objects.filter(principal=True).count(), 2, "Two movies are principal in their respective director set" )

        spielbergs_best_movie = Movie.objects.get( director=spielberg, principal=True )
        self.assertEqual(spielbergs_best_movie, s4, "Can update principal item with collection" )

        gilliams_best_movie = Movie.objects.get( director=gilliam, principal=True )
        self.assertEqual(gilliams_best_movie, g5, "Can update principal item with collection without changing others" )

        gilliams_best_comedy = Movie.objects.get( director=gilliam, genre="Comedy", principal_in_genre=True )
        self.assertEqual(gilliams_best_movie, g5, "Other principal fields are not affected" )

        g4.principal_in_genre = True
        g4.save()
        gilliams_best_comedy = Movie.objects.get( director=gilliam, genre="Comedy", principal_in_genre=True )
        self.assertEqual(gilliams_best_comedy, g4, "Can change complex collection properly" )

