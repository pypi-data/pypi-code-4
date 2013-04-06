# Copyright 2013 Mike Wakerly <opensource@hoho.com>
#
# This file is part of the Pykeg package of the Kegbot project.
# For more information on Pykeg or Kegbot, see http://kegbot.org/
#
# Pykeg is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Pykeg is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pykeg.  If not, see <http://www.gnu.org/licenses/>.

"""High-level interface to Django backend."""

from __future__ import absolute_import

import datetime
import logging

from django.conf import settings
from django.utils import timezone
from . import kb_common
from . import models
from . import time_series

if settings.HAVE_CELERY:
  from pykeg.web import tasks

class BackendError(Exception):
  """Base backend error exception."""

class NoTokenError(BackendError):
  """Token given is unknown."""

class KegbotBackend:
  """Django Backend."""

  def __init__(self, sitename='default', site=None):
    self._logger = logging.getLogger('backend')
    if site:
      self._site = site
    else:
      self._site = models.KegbotSite.objects.get(name=sitename)

  def _GetTapFromName(self, tap_name):
    try:
      return models.KegTap.objects.get(site=self._site, meter_name=tap_name)
    except models.KegTap.DoesNotExist:
      return None

  def _GetKegForTapName(self, tap_name):
    tap = self._GetTapFromName(tap_name)
    if tap and tap.current_keg and tap.current_keg.status == 'online':
      return tap.current_keg
    return None

  def _GetSensorFromName(self, name, autocreate=True):
    try:
      return models.ThermoSensor.objects.get(site=self._site, raw_name=name)
    except models.ThermoSensor.DoesNotExist:
      if autocreate:
        sensor = models.ThermoSensor(site=self._site, raw_name=name, nice_name=name)
        sensor.save()
        return sensor
      else:
        return None

  def _GetUserObjFromUsername(self, username):
    try:
      return models.User.objects.get(username=username)
    except models.User.DoesNotExist:
      return None

  def CreateNewUser(self, username):
    return models.User.objects.create(username=username)

  def CreateTap(self, name, meter_name, relay_name=None, ml_per_tick=None):
    tap = models.KegTap.objects.create(site=self._site, name=name,
        meter_name=meter_name, relay_name=relay_name, ml_per_tick=ml_per_tick)
    tap.save()
    return tap

  def CreateAuthToken(self, auth_device, token_value, username=None):
    token = models.AuthenticationToken.objects.create(
        site=self._site, auth_device=auth_device, token_value=token_value)
    if username:
      user = self._GetUserObjFromUsername(username)
      token.user = user
    token.save()
    return token

  def GetAllTaps(self):
    return list(models.KegTap.objects.all())

  def RecordDrink(self, tap_name, ticks, volume_ml=None, username=None,
      pour_time=None, duration=0, shout='', tick_time_series='',
      do_postprocess=True):

    tap = self._GetTapFromName(tap_name)
    if not tap:
      raise BackendError("Tap unknown")

    if volume_ml is None:
      volume_ml = float(ticks) * tap.ml_per_tick

    user = None
    if username:
      user = self._GetUserObjFromUsername(username)
    elif self._site.settings.default_user:
      user = self._site.settings.default_user

    if not pour_time:
      pour_time = timezone.now()

    keg = None
    if tap.current_keg and tap.current_keg.status == 'online':
      keg = tap.current_keg

    if tick_time_series:
      try:
        # Validate the time series by parsing it; canonicalize it by generating
        # it again.  If malformed, just junk it; it's non-essential information.
        tick_time_series = time_series.to_string(time_series.from_string(tick_time_series))
      except ValueError, e:
        self._logger.warning('Time series invalid, ignoring. Error was: %s' % e)
        tick_time_series = ''

    d = models.Drink(ticks=ticks, site=self._site, keg=keg, user=user,
        volume_ml=volume_ml, time=pour_time, duration=duration,
        shout=shout, tick_time_series=tick_time_series)
    models.DrinkingSession.AssignSessionForDrink(d)
    d.save()

    if do_postprocess:
      d.PostProcess()
      event_list = [e for e in models.SystemEvent.objects.filter(drink=d).order_by('id')]
      if settings.HAVE_CELERY:
        tasks.handle_new_events.delay(self._site, event_list)

    return d

  def CancelDrink(self, drink_id, spilled=False):
    try:
      d = self._site.drinks.get(id=drink_id)
    except models.Drink.DoesNotExist:
      return

    keg = d.keg
    user = d.user
    session = d.session

    # Transfer volume to spillage if requested.
    if spilled and d.volume_ml and d.keg:
      d.keg.spilled_ml += d.volume_ml
      d.keg.save()

    d.status = 'deleted'
    d.save()

    # Invalidate all statistics.
    models.SystemStats.objects.filter(site=self._site).delete()
    models.KegStats.objects.filter(site=self._site, keg=d.keg).delete()
    models.UserStats.objects.filter(site=self._site, user=d.user).delete()
    models.SessionStats.objects.filter(site=self._site, session=d.session).delete()

    # Delete any SystemEvents for this drink.
    models.SystemEvent.objects.filter(site=self._site, drink=d).delete()

    # Regenerate new statistics, based on the most recent drink
    # post-cancellation.
    last_qs = self._site.drinks.valid().order_by('-id')
    if last_qs:
      last_drink = last_qs[0]
      last_drink._UpdateSystemStats()

    if keg:
      keg.RecomputeStats()
    if user and user.get_profile():
      user.get_profile().RecomputeStats()
    if session:
      session.Rebuild()
      session.RecomputeStats()

    # TODO(mikey): recompute session.
    return d

  def LogSensorReading(self, sensor_name, temperature, when=None):
    now = timezone.now()
    if not when:
      when = now

    # The maximum resolution of ThermoSensor records is 1 minute.  Round the
    # time down to the nearest minute; if a record already exists for this time,
    # replace it.
    when = when.replace(second=0, microsecond=0)

    # If the temperature is out of bounds, reject it.
    min_val = kb_common.THERMO_SENSOR_RANGE[0]
    max_val = kb_common.THERMO_SENSOR_RANGE[1]
    if temperature < min_val or temperature > max_val:
      raise ValueError('Temperature out of bounds')

    sensor = self._GetSensorFromName(sensor_name)
    defaults = {
        'temp': temperature,
    }
    record, created = models.Thermolog.objects.get_or_create(site=self._site,
        sensor=sensor, time=when, defaults=defaults)
    record.temp = temperature
    record.save()

    # Delete old entries.
    keep_time = now - datetime.timedelta(hours=24)
    old_entries = models.Thermolog.objects.filter(site=self._site, time__lt=keep_time)
    old_entries.delete()

    return record

  def GetAuthToken(self, auth_device, token_value):
    if token_value and auth_device in kb_common.AUTH_MODULE_NAMES_HEX_VALUES:
      token_value = token_value.lower()
    try:
      return models.AuthenticationToken.objects.get(site=self._site,
        auth_device=auth_device, token_value=token_value)
    except models.AuthenticationToken.DoesNotExist:
      raise NoTokenError

