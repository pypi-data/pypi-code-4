from django.db import models


# noinspection PyShadowingBuiltins
class Album(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=160)
    artist = models.ForeignKey("Artist")

    def __unicode__(self):
        return u"%s" % self.title


# noinspection PyShadowingBuiltins
class Artist(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(blank=True, null=True, max_length=120)

    def __unicode__(self):
        return self.name


# noinspection PyShadowingBuiltins
class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    firstname = models.CharField(max_length=40)
    lastname = models.CharField(max_length=20)
    company = models.CharField(max_length=80, blank=True, null=True)
    address = models.CharField(max_length=70, blank=True, null=True)
    city = models.CharField(max_length=40, blank=True, null=True)
    state = models.CharField(max_length=40, blank=True, null=True)
    country = models.CharField(max_length=40, blank=True, null=True)
    postalcode = models.CharField(max_length=10, blank=True, null=True)
    phone = models.CharField(max_length=24, blank=True, null=True)
    fax = models.CharField(max_length=24, blank=True, null=True)
    email = models.CharField(max_length=60)
    support_rep = models.ForeignKey("Employee", null=True, blank=True)

    def __unicode__(self):
        return u"%s, %s" % (self.lastname, self.firstname)


# noinspection PyShadowingBuiltins
class Employee(models.Model):
    id = models.AutoField(primary_key=True)
    lastname = models.CharField(max_length=20)
    firstname = models.CharField(max_length=20)
    title = models.CharField(max_length=30, blank=True, null=True)
    reports_to = models.ForeignKey("Employee", null=True, blank=True)
    birthdate = models.DateTimeField(null=True, blank=True)
    hiredate = models.DateTimeField(null=True, blank=True)
    address = models.CharField(max_length=70, blank=True, null=True)
    city = models.CharField(max_length=40, blank=True, null=True)
    state = models.CharField(max_length=40, blank=True, null=True)
    country = models.CharField(max_length=40, blank=True, null=True)
    postalcode = models.CharField(max_length=10, blank=True, null=True)
    phone = models.CharField(max_length=24, blank=True, null=True)
    fax = models.CharField(max_length=24, blank=True, null=True)
    email = models.CharField(max_length=60, blank=True, null=True)

    def __unicode__(self):
        return u"%s, %s" % (self.lastname, self.firstname)


# noinspection PyShadowingBuiltins
class Genre(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=120, blank=True, null=True)

    def __unicode__(self):
        return u"%s" % self.name


# noinspection PyShadowingBuiltins
class Invoice(models.Model):
    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey("Customer")
    invoicedate = models.DateTimeField(db_column=u'InvoiceDate')
    billingaddress = models.CharField(max_length=70, blank=True, null=True)
    billingcity = models.CharField(max_length=40, blank=True, null=True)
    billingstate = models.CharField(max_length=40, blank=True, null=True)
    billingcountry = models.CharField(max_length=40, blank=True, null=True)
    billingpostalcode = models.CharField(max_length=10, blank=True, null=True)
    total = models.TextField(db_column=u'Total')

    def __unicode__(self):
        return u"%s: %s" % (self.id, self.customer)


# noinspection PyShadowingBuiltins
class Invoiceline(models.Model):
    id = models.AutoField(primary_key=True)
    invoice = models.ForeignKey("Invoice")
    track = models.ForeignKey("Track")
    unit_price = models.DecimalField(max_digits=5, decimal_places=2)
    quantity = models.IntegerField(db_column=u'Quantity')

    def __unicode__(self):
        return u"%s/%s/%s" % (self.track, self.invoice, self.unit_price)


# noinspection PyShadowingBuiltins
class MediaType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=120, blank=True, null=True)

    def __unicode__(self):
        return u"%s" % self.name


# noinspection PyShadowingBuiltins
class Playlist(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=120, blank=True, null=True)

    def __unicode__(self):
        return u"%s" % self.name


# noinspection PyShadowingBuiltins
class PlaylistTrack(models.Model):
    playlist = models.ForeignKey("Playlist")
    track = models.ForeignKey("Track")

    class Meta:
        unique_together = ('playlist', 'track')

    def __unicode__(self):
        return u"Playlist %s: %s" % (self.playlist, self.track)


# noinspection PyShadowingBuiltins
class Track(models.Model):
    id = models.AutoField(primary_key=True)
    playlist = models.ManyToManyField(Playlist, through=PlaylistTrack)
    name = models.CharField(max_length=200)
    album = models.ForeignKey("Album", null=True, blank=True)
    mediatype = models.ForeignKey("MediaType")
    genre = models.ForeignKey("Genre", null=True, blank=True)
    composer = models.CharField(max_length=220, blank=True, null=True)
    milliseconds = models.IntegerField(db_column=u'Milliseconds')
    bytes = models.IntegerField(null=True, blank=True)
    unit_price = models.DecimalField(max_digits=5, decimal_places=2)

    def __unicode__(self):
        return u"%s" % self.name