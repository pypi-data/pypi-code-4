import os

from datetime import datetime
from requests_forecast import Forecast


def main():
    forecast = Forecast(os.environ.get('FORECAST_IO_API'),
                        latitude=38.9717,
                        longitude=-95.235,
                        time=datetime.now())  # (year=2013, month=12, day=29, hour=12))
    print '+' * 20

    currently = forecast.get_currently()
    print 'current.temperature: {}'.format(currently.temperature)
    print 'current.cloudCover: {}'.format(currently.cloudCover)
    print 'current.humidity: {}'.format(currently.humidity)
    print 'current.icon: {}'.format(currently.icon)
    #print 'current.precipIntensity: {}'.format(currently.get('precipIntensity'))
    print 'current.precipIntensity: {}'.format(currently.precipIntensity)
    print 'current.pressure: {}'.format(currently.pressure)
    print 'current.summary: {}'.format(currently.summary)
    print 'current.time: {}'.format(currently.time)
    print 'current.visibility: {}'.format(currently.visibility)
    print 'current.windBearing: {}'.format(currently.windBearing)
    print 'current.windSpeed: {}'.format(currently.windSpeed)
    #print 'current: {}'.format(currently)
    print '-' * 20

    #{u'temperature': 47.68, u'humidity': 0.58, u'cloudCover': 0.63, u'summary': u'Mostly Cloudy',
    #u'pressure': 986.74, u'windSpeed': 11.12, u'visibility': 9.3, u'time': 1364422970, u'windBearing': 102, u'precipIntensity': 0, u'icon': u'partly-cloudy-day'}

    #print 'daily: {}'.format(len(daily['data']))
    #print 'daily: {}'.format(daily)
    daily = forecast.get_daily()
    print 'daily: {}'.format(len(daily))
    #print 'daily: {}'.format(daily.data)
    for day in daily.data:
        print '- {} | {} | {} | {}'.format(day.sunriseTime, day.sunsetTime, day.temperatureMin, day.temperatureMax)
    print '-' * 20
    print 'daily: {}'.format(daily['data'][0]['temperatureMin'])
    print 'daily: {}'.format(daily['data'][0]['temperatureMax'])
    print 'daily: {}'.format(daily)

    hourly = forecast.get_hourly()
    print 'hourly: {}'.format(len(hourly['data']))
    #print 'minutely: {}'.format(len(forecast.minutely['data']))

    alerts = forecast.get_alerts()
    print alerts


if __name__ == '__main__':
    main()
