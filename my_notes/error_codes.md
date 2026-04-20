# './parameter/error_codes.md'

# Parameter/sensor error flags

Both the sensor itself and the subsequent parameter calculation can encounter failure conditions, which are signaled to applications using flag bits.

## Document Changelog

Date | firmware version | Author  
---|---|---  
2023-07-31 | `04.xx/7-72-g43a0c45a3c` | Armin Brauns  
2023-08-01 | `04.xx/7-104-gea821d3dc9` | Armin Brauns  
|  |   
  
## Example parameter output

The following output of an `xmonitor-csv`/`xmonitor-csv-od` invocation shows the relevant flag fields. Line breaks have been inserted to show its three main parts:
    
    
    1695912515;
    
    997.954285;81.231155;0100;0000;
    1.000000;1.000000;0000;0000;
    26.150000;26.150000;0000;0000;
    997.954285;997.954285;0002;0000;
    1.000000;1.000000;0000;0000;
    997.914978;81.191856;0100;0000;
    1.000000;1.000000;0000;0000;
    26.150999;26.150999;0000;0000;
    7421.672363;7421.672363;0000;0000;
    7421.672363;7421.672363;0000;0000;
    17.164062;17.164062;0000;0000;
    nan;nan;0001;0000;
    997.954285;81.231155;0100;0000;
    1.000000;1.000000;0000;0000;
    0.000000;0.000000;0000;0000;
    0.000000;0.000000;0000;0000;
    0.000000;0.000000;0000;0000;
    57.610840;57.610840;0000;0000;
    26.150999;26.150999;0000;0000;
    nan;nan;0003;0000;
    nan;nan;0003;0000;
    nan;nan;0001;0000;
    0.992631;0.992631;0000;0000;
    
    0000;1.00;1

The first field is the UNIX timestamp of the acquisition. It is followed by data for all 23 parameters, consisting of four fields each: \- value - raw value - status - private status

Finally, the last three fields show the sensor status, pressure, and delay between data acquisition and display (in seconds).

In the example, the sensor status is `0000`, and the parameter at index 3 has a status of `0002` and a private status of `0000`.

## Sensor status

These are global status flags that affect all parameter values.

Flag value | Description  
---|---  
`0x0001` | PLL frequency different from sensor frequency  
`0x0002` | PLL not locked  
`0x0004` | Incorrect PLL lock  
`0x0008` | ASB communication error  
`0x0010` | Temperature sensor HW error  
`0x0020` | Too hot  
`0x0040` | ASB serial number changed (SMET only)  
`0x0080` | Sensor serial number changed (SMET only)  
`0x0100` | Sensor is dirty  
`0x0200` | Sensor is in air  
`0x0400` | Maintenance required  
  
## Parameter status

These status flags apply only to the specific parameter they are raised on.

### Status

Flag value | Critical? | Description  
---|---|---  
`0x0001` | yes | General error  
`0x0002` | yes | Config error  
`0x0004` | yes | Hardware error  
`0x0008` | yes | Dependency loop  
`0x0010` | yes | Not ready yet  
`0x0020` | yes | Internal error (unused)  
`0x0040` | yes | Calibration error  
`0x0080` | yes | Value below calibrated range  
`0x0100` | no | Has user calibration  
`0x0200` | no | [User defined 1]  
`0x0400` | no | [User defined 2]  
`0x0800` | yes | Not stable  
`0x1000` | yes | Out-of-range warning (too low)  
`0x2000` | yes | Out-of-range warning (too high)  
`0x4000` | yes | Out-of-range alarm (too low)  
`0x8000` | yes | Out-of-range alarm (too high)  
  
### Private status

Flag value | Description  
---|---  
`0x0010` | Temperature too high  
`0x0020` | Temperature too low  
`0x0040` | Pressure too high  
`0x0080` | Pressure too low  
`0x0100` | Last good value too old  
`0x0200` | Value is “last good”, not current
