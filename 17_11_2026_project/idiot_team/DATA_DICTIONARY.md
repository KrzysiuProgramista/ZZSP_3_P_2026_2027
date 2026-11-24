# CityPulse data dictionary

| File | Primary key / join key | Grain | Rows |
|---|---|---|---:|
| traffic.csv | (timestamp, sensor_id) | One hourly reading per sensor | 13,392 |
| sensors.csv | sensor_id | One row per sensor | 18 |
| weather.csv | (timestamp, district) | One hourly reading per district (with a few missing observations) | 4,446 |
| incidents.csv | incident_id; join key (timestamp, sensor_id) | One event per sensor-hour; includes a few unmatched sensor IDs | 130 |

All timestamps are local naive timestamps for this classroom dataset. All data is synthetic.
