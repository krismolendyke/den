Data
====

Thermostats
-----------

Den store thermostat data in `InfluxDB`_.

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
                   "device_id": "peyiJNo0IldT2YlIVtYaGQ",
                   "locale": "en-US",
                   "software_version": "4.0",
                   "structure_id": "VqFabWH21nwVyd4RWgJgNb292wa7hG_dUwo2i2SG7j3-BOLY0BA4sw",
                   "name": "Hallway (upstairs)",
                   "name_long": "Hallway Thermostat (upstairs)",
                   "last_connection": "2016-10-31T23:59:59.000Z",
                   "is_online": true,
                   "can_cool": true,
                   "can_heat": true,
                   "is_using_emergency_heat": true,
                   "has_fan": true,
                   "fan_timer_active": true,
                   "fan_timer_timeout": "2016-10-31T23:59:59.000Z",
                   "has_leaf": true,
                   "temperature_scale": "C",
                   "target_temperature_f": 72,
                   "target_temperature_c": 21.5,
                   "target_temperature_high_f": 80,
                   "target_temperature_high_c": 24.5,
                   "target_temperature_low_f": 65,
                   "target_temperature_low_c": 19.5,
                   "eco_temperature_high_f": 80,
                   "eco_temperature_high_c": 24.5,
                   "eco_temperature_low_f": 65,
                   "eco_temperature_low_c": 19.5,
                   "away_temperature_high_f": 80,
                   "away_temperature_high_c": 24.5,
                   "away_temperature_low_f": 65,
                   "away_temperature_low_c": 19.5,
                   "hvac_mode": heat,
                   "previous_hvac_mode": heat,
                   "ambient_temperature_f": 72,
                   "ambient_temperature_c": 21.5,
                   "humidity": 40,
                   "hvac_state": "heating",
                   "where_id": "UNCBGUnN24...",
                   "is_locked": true,
                   "locked_temp_min_f": "65",
                   "locked_temp_max_f": "80",
                   "locked_temp_min_c": "19.5",
                   "locked_temp_max_c": "24.5",
                   "label": "Pat's room",
                   "where_name": "Hallway",
                   "sunlight_correction_enabled": true,
                   "sunlight_correction_active": true,
                   "fan_timer_duration": 15,
                   "time_to_target": "~15",
                   "time_to_target_training": "training"
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
           "measurement": "thermostats",
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
               "fan_timer_timeout": "2016-10-31T23:59:59.000Z",
               "humidity": 40,
               "last_connection": "2016-10-31T23:59:59.000Z",
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
               "time_to_target": "~15"
           }
       },
   ]

Measurement
~~~~~~~~~~~

.. epigraph::

   The part of InfluxDB’s structure that describes the data stored in the
   associated fields. Measurements are strings.

   -- `InfluxDB`_ `measurement`_ documentation

Den stores thermostat data in a measurement named ``thermostats``.

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
#. `name`_
#. `name_long`_
#. `previous_hvac_mode`_
#. `software_version`_
#. `structure_id`_
#. `sunlight_correction_active`_
#. `sunlight_correction_enabled`_
#. `temperature_scale`_
#. `time_to_target_training`_
#. `where_id`_
#. `where_name`_

Fields
~~~~~~

.. epigraph::

   The key-value pair in InfluxDB’s data structure that records metadata and
   the actual data value. Fields are required in InfluxDB’s data structure and
   they are not indexed - queries on field values scan all points that match
   the specified time range and, as a result, are not performant relative to
   tags. Query tip: Compare fields to tags; tags are indexed

   -- `InfluxDB`_ `field`_ documentation

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
#. `fan_timer_timeout`_
#. `humidity`_
#. `last_connection`_
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
#. `time_to_target`_

Weather
-------

WIP

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
