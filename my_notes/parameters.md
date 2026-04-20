# './bluetooth/parameters.md'

# Device Name and Serial/Type

The device name encodes the serial number and device type, e.g. `RH B09-0623 SRV`, where: - `RH`: Rheoncis - `B09-0623`: analog sensor board serial - `SRV`: sensor type

# Configuration (legacy Bluetooth profile)

## Service b1bee998-1b19-49c9-b357-18c16c5cccad

### CH1/4mA: c0bdc9da-2400-4bd5-b09e-77047efbd152

8 byte - double (current output, value low)

### CH1/20mA: 30977e44-4758-4994-b023-53fd4a3a373d

8 byte - double (current output, value high)

### CH2/4mA: 35ac88eb-aa64-4446-994f-a13d-80113db4

8 byte - double (current output, value low)

### CH2/20mA: 53ab851c-bc9e-4c76-9485-83ae2dbd33f5

8 byte - double (current output, value high)

### CH3/4mA: b76ca95d-5d5f-4d45-a006-1cfde2c577f0

8 byte - double (current output, value low)

### CH3/20mA: f8d9e7a1-326f-48c2-b587-89c2f1140089

8 byte - double (current output, value high)

### Densitity: d0eb5a80-b267-46d5-bad5-aeeec3bccc29

8 byte - double (analog senso board Do0)

# Dynamic Parameters

This document describes the export of dynamic parameters using Bluetooth LE GATT charactersitics. The reason why this is done this way are hardware limitations of the BlueNRG-1 Chip which can only export a maximum of 68 characteristics and only a total of 1248 bytes.

For this reason all (currently 22) parameters are streamed using 3 characteristics, this document describes the format.

Author | Date | Comment  
---|---|---  
Roland Lezuo | 2020-12-11 | Document created  
Roland Lezuo | 2020-12-17 | Updates status (V03.10/0)  
Roland Lezuo | 2020-12-18 | added Sensor Status (V03.10/1)  
Roland Lezuo | 2021-04-23 | added Status (V03.20/0)  
  
## Service 1995a701-ef _ea_ -4d2c-9c84-a0b6 _01_ a4304b

The dynamic Parameter Sevice consists of 3 characterstics, each is 12 bytes long (althogh the exact length may be longer), when new measurement date is available all three characteristics will be updated in short intervals streaming the data of all exported parameters.

### Raw Values: 1995a701-efea-4d2c-9c84-a0b6 _02_ a4304b

Offset into package (bytes): | 0 | 1-4 | 5-8 | 9-  
---|---|---|---|---  
Meaning | Parameter Index | Raw Value (float) | Value (float) | 0x00  
  
There will be a short burst of updates, one for each exported parameter, each containing the parameter number (index) and the current raw value (as float)

### Parameter Names: 1995a701-efea-4d2c-9c84-a0b6 _03_ a4304b

Offset into package (bytes): | 0 | 1 | 2-  
---|---|---|---  
Meaning | Parameter Index | Chunk Index | Parameter Name (part of)  
  
Parameter names may exceed the size of a single package and are thus chunked. For each parameter (index) and number of chunks (starting with 0) is transmitted including a terminating 0 character. The last chunk will be filled with 0x00. The receiver is responsible to concatenate the string and handle the (possible) loss of chunks during transmission.

### Parameter Units: 1995a701-efea-4d2c-9c84-a0b6 _04_ a4304b

Offset into package (bytes): | 0 | 1 | 2-3 | 4-5 | 6-7 | 8-  
---|---|---|---|---|---|---  
Meaning | Parameter Index | Unit | Status | Private Status | Sensor Status | 0x00  
  
The unit is transmitted as value representation of the `enum parameter_units_t` (`Inc/parameter.h`). The receiver needs to translate this according to the firmware version of the device.

## Service 1995a701-ef _06_ -4d2c-9c84-a0b6 _01_ a4304b

This service 1995a701-ef06-4d2c-9c84-a0b602a4304bis used to stream status information which are not mapped to parameters.

### Status Values: 1995a701-ef _06_ -4d2c-9c84-a0b6 _02_ a4304b

Offset into package (bytes): | 0 | 1-  
---|---|---  
Meaning | Package Index | Stream Data  
  
The receiver collects all packages until received one with index equals to 0. He then concatenates all packages in ascending order of the package index. If an index is missing that specific package got lost. She then restarts the process until a complete package sequence is captured. The meaning of a full sequence is dependend on the status value stream version (the first byte of the full sequence). Currently only version ‘0’ (48, 0x30) is defined:

Byte position in Stream: | 0 | 1-(x-1) | x  
---|---|---|---  
Meaning | Version (‘0’) | 0-terminated String (Firmware Version) | 0 (string terminator)  
Byte position in Stream: | x+1 | x+5 | x+9 | x+13 | x+17 | x+21 | x+25 | x+29  
---|---|---|---|---|---|---|---|---  
Meaning | Fv (int) | ph (int) | im (int) | ip (int) | q (float) | fr (float) | dfm (float) | fdp (float)  
  
int and float values are transferred in little-endian format. The last package may contain additional bytes, which are to be ignored.

## Testing

`Tools/dyn_params.py` is a Python program which can be executed under Linux (tested Ubuntu 20.04) to receive and and pring the parameter data of the sensor.

Usage: `./dyn_params.py -b MAC_ADDRESS_OF_SENSOR`

The oupt looks like this, please note that the first time a data inconsistency is reported this is expected as the data stream will be picked up somewhere in the middle.
    
    
    rlezuo@m42-p51:~/rheonics$ ./dyn_params.py  -b 70:B3:D5:D2:02:7B
    [70:B3:D5:D2:02:7B] Services resolved
        b1bee998-1b19-49c9-b357-18c16c5cccad
        1995a701-efea-4d2c-9c84-a0b601a4304b
        1995a701-ef06-4d2c-9c84-a0b601a4304b
        00001801-0000-1000-8000-00805f9b34fb
    [70:B3:D5:D2:02:7B] dyn params charactersistics
        1995a701-efea-4d2c-9c84-a0b604a4304b
        1995a701-efea-4d2c-9c84-a0b603a4304b
        1995a701-efea-4d2c-9c84-a0b602a4304b
    [70:B3:D5:D2:02:7B] dyn status charactersistics
        1995a701-ef06-4d2c-9c84-a0b602a4304b
    [70:B3:D5:D2:02:7B] all characteristics found
    ************* pretty printing complete data set
    [70:B3:D5:D2:02:7B] data inconsistency
    ************* pretty printing complete data set
    idx=00 unit=01 value=    0.0026 name=Viscosity
    idx=01 unit=24 value=    1.0000 name=Density
    idx=02 unit=20 value=   21.3020 name=Temperatur
    idx=03 unit=00 value=    0.0026 name=
    idx=04 unit=24 value=    1.0000 name=Density
    idx=05 unit=01 value=    0.0026 name=Viscosity
    idx=06 unit=24 value=    1.0000 name=Density
    idx=07 unit=20 value=   21.3020 name=Temperatur
    idx=08 unit=56 value= 7340.1680 name=Fres
    idx=09 unit=56 value= 7340.1680 name=Fres Comp
    idx=10 unit=56 value=    1.1719 name=Damping
    idx=11 unit=20 value=       nan name=Coil
    idx=12 unit=01 value=    0.0026 name=Viscosity
    idx=13 unit=24 value=    1.0000 name=Density
    idx=14 unit=00 value=    0.0000 name=Ex-1
    idx=15 unit=00 value=    0.0000 name=Ex-2
    idx=16 unit=00 value=    0.0000 name=Ex-3
    idx=17 unit=20 value=   20.8003 name=Temp Est
    idx=18 unit=20 value=   21.3020 name=Temp PT
    idx=19 unit=00 value=       nan name=Script 0
    idx=20 unit=00 value=       nan name=Script 1
    idx=21 unit=00 value=       nan name=Script 2
    VERSION: 03.10/2-ge003.10/2-gefd7cfc-dirty
    STATUS: Fv=594 ph=18 im=1 ip=1 q=0.9840357899665833 fr=7338.4892578125 dfm=7337.958984375 dfp=7339.009765625
