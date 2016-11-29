Data
====

InfluxDB
--------

All data is stored in `InfluxDB`_.  The following sections describe how the
data is stored.

Measurement
~~~~~~~~~~~

.. epigraph::

   The part of InfluxDB’s structure that describes the data stored in the
   associated fields. Measurements are strings.

   -- `InfluxDB`_ `measurement`_ documentation

Tags
~~~~

.. epigraph::

   The key-value pair in InfluxDB’s data structure that records metadata. Tags
   are an optional part of InfluxDB’s data structure but they are useful for
   storing commonly-queried metadata; tags are indexed so queries on tags are
   performant. Query tip: Compare tags to fields; fields are not indexed.

   -- `InfluxDB`_ `tag`_ documentation

.. note::

   The `tag`_ values are always interpreted as strings.

Each `tag`_ value should have very few possible values which yields a low
`series cardinality`_.

Fields
~~~~~~

.. epigraph::

   The key-value pair in InfluxDB’s data structure that records metadata and
   the actual data value. Fields are required in InfluxDB’s data structure and
   they are not indexed - queries on field values scan all points that match
   the specified time range and, as a result, are not performant relative to
   tags. Query tip: Compare fields to tags; tags are indexed

   -- `InfluxDB`_ `field`_ documentation

Structure
---------

``den`` records structure data in a measurement named ``structure``.

.. _structure-data-model:

Data Model
~~~~~~~~~~

An example of the structures data model, limited to thermostat read/write
permissions, from the Nest `Data Model Viewer`_ (as `JSON`_):

.. code-block:: js

   {
       "structures": {
           "VqFabWH21nwVyd4RWgJgNb292wa7hG_dUwo2i2SG7j3-BOLY0BA4sw": {
               "structure_id": "VqFabWH21nwVyd4RWgJgNb292wa7hG_dUwo2i2SG7j3-BOLY0BA4sw",
               "thermostats": [ "peyiJNo0IldT2YlIVtYaGQ", ... ],
               "smoke_co_alarms": [ "RTMTKxsQTCxzVcsySOHPxKoF4OyCifrs", ... ],
               "cameras": [ "awJo6rH…", ... ],
               "devices": {
               },
               "away": "home",
               "name": "Home",
               "country_code": "US",
               "postal_code": "94304",
               "peak_period_start_time": "2016-10-31T23:59:59.000Z",
               "peak_period_end_time": "2016-10-31T23:59:59.000Z",
               "time_zone": "America/Los_Angeles",
               "eta": {
               },
               "rhr_enrollment": true,
               "wheres": {
                   "Fqp6wJI...": {
                   }
               }
           }
       }
   }

`InfluxDB`_ Point
~~~~~~~~~~~~~~~~~

The :ref:`structure-data-model` example transformed into a list containing a
single `InfluxDB`_ `point`_ (as `Python`_):

.. code-block:: python

   [
       {
           "measure": "structure",
           "tags": {
               "away": "home",
               "country_code": "US",
               "name": "Home",
               "postal_code": "94304",
               "structure_id": "VqFabWH21nwVyd4RWgJgNb292wa7hG_dUwo2i2SG7j3-BOLY0BA4sw",
               "thermostat_id": "peyiJNo0IldT2YlIVtYaGQ",
               "time_zone": "America/Los_Angeles"
           },
           "fields": {
               "is_away": 0
           }
       }
   ]

.. note::

   The :ref:`structure-data-model` ``thermostats`` list is denormalized into a
   point per thermostat id.

Measurement
~~~~~~~~~~~

``den`` records structure data in a measurement named ``structure``.


Tags
~~~~

#. `away`_
#. `country_code`_
#. `name`_
#. `postal_code`_
#. `structure_id`_
#. `thermostat_id`_
#. `time_zone`_

Fields
~~~~~~

#. ``is_away`` is a numeric representation of the ``away`` tag, i.e., ``home``
   as ``0``, ``away`` as ``1``

Thermostat
----------

``den`` records thermostat data in `InfluxDB`_.

.. _thermostat-data-model:

Data Model
~~~~~~~~~~

An example of the devices data model, limited to thermostat read/write
permissions, from the Nest `Data Model Viewer`_ (as `JSON`_):

.. code-block:: js

   {
       "devices": {
           "thermostats": {
               "peyiJNo0IldT2YlIVtYaGQ": {
                   "ambient_temperature_c": 21.5,
                   "ambient_temperature_f": 72,
                   "away_temperature_high_c": 24.5,
                   "away_temperature_high_f": 80,
                   "away_temperature_low_c": 19.5,
                   "away_temperature_low_f": 65,
                   "can_cool": true,
                   "can_heat": true,
                   "device_id": "peyiJNo0IldT2YlIVtYaGQ",
                   "eco_temperature_high_c": 24.5,
                   "eco_temperature_high_f": 80,
                   "eco_temperature_low_c": 19.5,
                   "eco_temperature_low_f": 65,
                   "fan_timer_active": true,
                   "fan_timer_duration": 15,
                   "fan_timer_timeout": "2016-10-31T23:59:59.000Z",
                   "has_fan": true,
                   "has_leaf": true,
                   "humidity": 40,
                   "hvac_mode": heat,
                   "hvac_state": "heating",
                   "is_locked": true,
                   "is_online": true,
                   "is_using_emergency_heat": true,
                   "label": "Pat's room",
                   "last_connection": "2016-10-31T23:59:59.000Z",
                   "locale": "en-US",
                   "locked_temp_max_c": "24.5",
                   "locked_temp_max_f": "80",
                   "locked_temp_min_c": "19.5",
                   "locked_temp_min_f": "65",
                   "name": "Hallway (upstairs)",
                   "name_long": "Hallway Thermostat (upstairs)",
                   "previous_hvac_mode": heat,
                   "software_version": "4.0",
                   "structure_id": "VqFabWH21nwVyd4RWgJgNb292wa7hG_dUwo2i2SG7j3-BOLY0BA4sw",
                   "sunlight_correction_active": true,
                   "sunlight_correction_enabled": true,
                   "target_temperature_c": 21.5,
                   "target_temperature_f": 72,
                   "target_temperature_high_c": 24.5,
                   "target_temperature_high_f": 80,
                   "target_temperature_low_c": 19.5,
                   "target_temperature_low_f": 65,
                   "temperature_scale": "C",
                   "time_to_target": "~15",
                   "time_to_target_training": "training",
                   "where_id": "UNCBGUnN24...",
                   "where_name": "Hallway"
               }
           }
       }
   }

`InfluxDB`_ Point
~~~~~~~~~~~~~~~~~

The :ref:`thermostat-data-model` example transformed into a list containing a
single `InfluxDB`_ `point`_ (as `Python`_):

.. code-block:: python

   [
       {
           "measurement": "thermostat",
           "tags": {
               "can_cool": True,
               "can_heat": True,
               "device_id": "peyiJNo0IldT2YlIVtYaGQ",
               "fan_timer_active": True,
               "has_fan": True,
               "has_leaf": True,
               "hvac_mode": "heat",
               "hvac_state": "heating",
               "is_locked": True,
               "is_online": True,
               "is_using_emergency_heat": True,
               "label": "Pat's room",
               "locale": "en-US",
               "name": "Hallway (upstairs)",
               "name_long": "Hallway Thermostat (upstairs)",
               "previous_hvac_mode": "heat",
               "software_version": "4.0",
               "structure_id": "VqFabWH21nwVyd4RWgJgNb292wa7hG_dUwo2i2SG7j3-BOLY0BA4sw",
               "sunlight_correction_active": True,
               "sunlight_correction_enabled": True ,
               "temperature_scale": "C",
               "time_to_target": "~15",
               "time_to_target_training": "training" ,
               "where_id": "UNCBGUnN24...",
               "where_name": "Hallway"
           },
           "fields": {
               "ambient_temperature_c": 21.5,
               "ambient_temperature_f": 72,
               "away_temperature_high_c": 24.5,
               "away_temperature_high_f": 80,
               "away_temperature_low_c": 19.5,
               "away_temperature_low_f": 65,
               "eco_temperature_high_c": 24.5,
               "eco_temperature_high_f": 80,
               "eco_temperature_low_c": 19.5,
               "eco_temperature_low_f": 65,
               "fan_timer_duration": 15,
               "humidity": 40,
               "locked_temp_max_c": 24.5,
               "locked_temp_max_f": 80,
               "locked_temp_min_c": 19.5,
               "locked_temp_min_f": 65,
               "target_temperature_c": 21.5,
               "target_temperature_f": 72,
               "target_temperature_high_c": 24.5,
               "target_temperature_high_f": 80,
               "target_temperature_low_c": 19.5,
               "target_temperature_low_f": 65,
           }
       },
   ]

.. note::

   The following parameters are not recorded:

   - `last_connection`_
   - `fan_timer_timeout`_

Measurement
~~~~~~~~~~~

``den`` records thermostat data in a measurement named ``thermostat``.

Tags
~~~~

#. `can_cool`_
#. `can_heat`_
#. `device_id`_
#. `fan_timer_active`_
#. `has_fan`_
#. `has_leaf`_
#. `hvac_mode`_
#. `hvac_state`_
#. `is_locked`_
#. `is_online`_
#. `is_using_emergency_heat`_
#. `label`_
#. `locale`_
#. `name_long`_
#. `name`_
#. `previous_hvac_mode`_
#. `software_version`_
#. `structure_id`_
#. `sunlight_correction_active`_
#. `sunlight_correction_enabled`_
#. `temperature_scale`_
#. `time_to_target_training`_
#. `time_to_target`_
#. `where_id`_
#. `where_name`_

Fields
~~~~~~

#. `ambient_temperature_c`_
#. `ambient_temperature_f`_
#. `away_temperature_high_c`_
#. `away_temperature_high_f`_
#. `away_temperature_low_c`_
#. `away_temperature_low_f`_
#. `eco_temperature_high_c`_
#. `eco_temperature_high_f`_
#. `eco_temperature_low_c`_
#. `eco_temperature_low_f`_
#. `fan_timer_duration`_
#. `humidity`_
#. `locked_temp_max_c`_
#. `locked_temp_max_f`_
#. `locked_temp_min_c`_
#. `locked_temp_min_f`_
#. `target_temperature_c`_
#. `target_temperature_f`_
#. `target_temperature_high_c`_
#. `target_temperature_high_f`_
#. `target_temperature_low_c`_
#. `target_temperature_low_f`_

Weather
-------

.. _weather-data-model:

Data Model
~~~~~~~~~~

An example of the weather data model `Powered by Dark Sky`_, a "currently"
`data point object`_ (as `JSON`_):

.. note::

   ``time`` is the only value guaranteed to be present in a `data point
   object`_.

.. code-block:: js

   {
     "apparentTemperature": 46.93,
     "cloudCover": 0.73,
     "dewPoint": 47.7,
     "humidity": 0.96,
     "icon": "rain",
     "nearestStormDistance": 0,
     "ozone": 328.35,
     "precipIntensity": 0.1685,
     "precipIntensityError": 0.0067,
     "precipProbability": 1,
     "precipType": "rain",
     "pressure": 1009.7,
     "summary": "Rain",
     "temperature": 48.71,
     "time": 1453402675,
     "visibility": 4.3,
     "windBearing": 186,
     "windSpeed": 4.64
   }

`InfluxDB`_ Point
~~~~~~~~~~~~~~~~~

The :ref:`weather-data-model` example transformed into a list containing a
single `InfluxDB`_ `point`_ (as `Python`_):

.. note::

   The ``summary`` property "has millions of possible values" according to the
   `data point object`_ documentation.  This would result in a high `series
   cardinality`_.  It is therefore not included as a `tag`_.  It also has no
   value as `field`_ so it is not included in the `measurement`_ at all.

.. code-block:: python

   [
       {
           "measurement": "weather",
           "tags": {
               "icon": "rain",
               "precipType": "rain"
           },
           "fields": {
               "apparentTemperature": 46.93,
               "cloudCover": 0.73,
               "dewPoint": 47.7,
               "humidity": 0.96,
               "nearestStormDistance": 0,
               "ozone": 328.35,
               "precipIntensity": 0.1685,
               "precipIntensityError": 0.0067,
               "precipProbability": 1,
               "pressure": 1009.7,
               "temperature": 48.71,
               "time": 1453402675,
               "visibility": 4.3,
               "windBearing": 186,
               "windSpeed": 4.64
           }
       }
   ]

Measurement
~~~~~~~~~~~

``den`` records weather data in a measurement named ``weather``.

Tags
~~~~

#. ``icon``
#. ``precipType``

Fields
~~~~~~

#. ``apparentTemperature``
#. ``cloudCover``
#. ``dewPoint``
#. ``humidity``
#. ``nearestStormBearing``
#. ``nearestStormDistance``
#. ``ozone``
#. ``precipIntensity``
#. ``precipProbability``
#. ``pressure``
#. ``temperature``
#. ``time``
#. ``visibility``
#. ``windBearing``
#. ``windSpeed``

Propane
-------

``den`` records propane data in a measurement named ``propane``.

.. _propane-data-model:

Data Model
~~~~~~~~~~

InfluxDB Point
~~~~~~~~~~~~~~

Measurement
~~~~~~~~~~~

Tags
~~~~

Fields
~~~~~~

.. _Data Model Viewer: https://developers.nest.com/documentation/api-reference
.. _InfluxDB: https://www.influxdata.com/time-series-platform/influxdb/
.. _can_cool: https://developers.nest.com/documentation/api-reference/overview#cancool
.. _can_heat: https://developers.nest.com/documentation/api-reference/overview#canheat
.. _device_id: https://developers.nest.com/documentation/api-reference/overview#deviceid
.. _fan_timer_active: https://developers.nest.com/documentation/api-reference/overview#fantimeractive
.. _has_fan: https://developers.nest.com/documentation/api-reference/overview#hasfan
.. _has_leaf: https://developers.nest.com/documentation/api-reference/overview#hasleaf
.. _hvac_mode: https://developers.nest.com/documentation/api-reference/overview#hvacmode
.. _hvac_state: https://developers.nest.com/documentation/api-reference/overview#hvacstate
.. _is_locked: https://developers.nest.com/documentation/api-reference/overview#islocked
.. _is_online: https://developers.nest.com/documentation/api-reference/overview#isonline
.. _is_using_emergency_heat: https://developers.nest.com/documentation/api-reference/overview#isusingemergencyheat
.. _label: https://developers.nest.com/documentation/api-reference/overview#label
.. _locale: https://developers.nest.com/documentation/api-reference/overview#locale
.. _name: https://developers.nest.com/documentation/api-reference/overview#name
.. _name_long: https://developers.nest.com/documentation/api-reference/overview#namelong
.. _previous_hvac_mode: https://developers.nest.com/documentation/api-reference/overview#previoushvacmode
.. _software_version: https://developers.nest.com/documentation/api-reference/overview#softwareversion
.. _structure_id: https://developers.nest.com/documentation/api-reference/overview#structureid
.. _sunlight_correction_active: https://developers.nest.com/documentation/api-reference/overview#sunlightcorrectionactive
.. _sunlight_correction_enabled: https://developers.nest.com/documentation/api-reference/overview#sunlightcorrectionenabled
.. _temperature_scale: https://developers.nest.com/documentation/api-reference/overview#temperaturescale
.. _time_to_target_training: https://developers.nest.com/documentation/api-reference/overview#timetotargettraining
.. _where_id: https://developers.nest.com/documentation/api-reference/overview#whereid
.. _where_name: https://developers.nest.com/documentation/api-reference/overview#wherename
.. _ambient_temperature_c: https://developers.nest.com/documentation/api-reference/overview#ambienttemperaturec
.. _ambient_temperature_f: https://developers.nest.com/documentation/api-reference/overview#ambienttemperaturef
.. _away_temperature_high_c: https://developers.nest.com/documentation/api-reference/overview#awaytemperaturehighc
.. _away_temperature_high_f: https://developers.nest.com/documentation/api-reference/overview#awaytemperaturehighf
.. _away_temperature_low_c: https://developers.nest.com/documentation/api-reference/overview#awaytemperaturelowc
.. _away_temperature_low_f: https://developers.nest.com/documentation/api-reference/overview#awaytemperaturelowf
.. _eco_temperature_high_c: https://developers.nest.com/documentation/api-reference/overview#ecotemperaturehighc
.. _eco_temperature_high_f: https://developers.nest.com/documentation/api-reference/overview#ecotemperaturehighf
.. _eco_temperature_low_c: https://developers.nest.com/documentation/api-reference/overview#ecotemperaturelowc
.. _eco_temperature_low_f: https://developers.nest.com/documentation/api-reference/overview#ecotemperaturelowf
.. _fan_timer_duration: https://developers.nest.com/documentation/api-reference/overview#fantimerduration
.. _fan_timer_timeout: https://developers.nest.com/documentation/api-reference/overview#fantimertimeout
.. _humidity: https://developers.nest.com/documentation/api-reference/overview!#humidity
.. _last_connection: https://developers.nest.com/documentation/api-reference/overview#lastconnection
.. _locked_temp_max_c: https://developers.nest.com/documentation/api-reference/overview#lockedtempmaxc
.. _locked_temp_max_f: https://developers.nest.com/documentation/api-reference/overview#lockedtempmaxf
.. _locked_temp_min_c: https://developers.nest.com/documentation/api-reference/overview#lockedtempminc
.. _locked_temp_min_f: https://developers.nest.com/documentation/api-reference/overview#lockedtempminf
.. _target_temperature_c: https://developers.nest.com/documentation/api-reference/overview#targettemperaturec
.. _target_temperature_f: https://developers.nest.com/documentation/api-reference/overview#targettemperaturef
.. _target_temperature_high_c: https://developers.nest.com/documentation/api-reference/overview#targettemperaturehighc
.. _target_temperature_high_f: https://developers.nest.com/documentation/api-reference/overview#targettemperaturehighf
.. _target_temperature_low_c: https://developers.nest.com/documentation/api-reference/overview#targettemperaturelowc
.. _target_temperature_low_f: https://developers.nest.com/documentation/api-reference/overview#targettemperaturelowf
.. _time_to_target: https://developers.nest.com/documentation/api-reference/overview#timetotarget
.. _tag: https://docs.influxdata.com/influxdb/v1.0/concepts/glossary/#tag
.. _field: https://docs.influxdata.com/influxdb/v1.0/concepts/glossary/#field
.. _measurement: https://docs.influxdata.com/influxdb/v1.0/concepts/glossary/#measurement
.. _series cardinality: https://docs.influxdata.com/influxdb/v1.0/concepts/glossary/#series-cardinality
.. _JSON: http://json.org/
.. _Python: https://www.python.org/
.. _point: https://docs.influxdata.com/influxdb/v1.0/concepts/glossary/#point
.. _Powered by Dark Sky: https://darksky.net/poweredby/
.. _data point object: https://darksky.net/dev/docs/response#data-point
.. _thermostat_id: https://developers.nest.com/documentation/api-reference/overview#deviceid
.. _away: https://developers.nest.com/documentation/api-reference/overview#away
.. _country_code: https://developers.nest.com/documentation/api-reference/overview#countrycode
.. _name: https://developers.nest.com/documentation/api-reference/overview#name
.. _postal_code: https://developers.nest.com/documentation/api-reference/overview#postalcode
.. _structure_id: https://developers.nest.com/documentation/api-reference/overview#structureid
.. _time_zone: https://developers.nest.com/documentation/api-reference/overview#timezone
