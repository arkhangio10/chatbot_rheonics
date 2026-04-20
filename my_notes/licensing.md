# './licensing.md'

# LICENSING module

Several firmware components can be disabled selectively through the “licensing” module:

  * Modbus TCP
  * Modbus RTU
  * Bluetooth
  * File logger



To change these settings, a signed license file has to be supplied through the `xwlicense` RCP command.

## Document Changelog

Date | firmware version | Author  
---|---|---  
2023-07-31 | `04.xx/7-72-g43a0c45a3c` | Armin Brauns  
2023-08-01 | `04.xx/7-88-g0cbc50def2` | Armin Brauns  
2023-08-03 | `04.xx/7-126-gde517eba80` | Armin Brauns  
2023-08-04 | `04.xx/7-151-gff37730cc3` | Armin Brauns  
|  |   
  
## License files

License files are simple INI files containing the desired license settings as well as the UUID of the device they should apply to. They are then cryptographically signed to prevent unauthorized modification.

An example unsigned license file looks like this:
    
    
    UUID=0042002A-3037510B-39313636
    datalogger=permanent
    modbus_tcp=2023-08-01
    bluetooth=permanent
    analog_out=none

The `UUID` is the `If_UUID` value reported by `xrsenconf`. All other entries consist of the name of a license module, and the state of that license:

  * `permanent`: module is always available
  * `none`: module is never available
  * a date in `YYYY-MM-DD` format: the module is available until the specified date.



Currently, the following license modules are available on SMET:

  * `datalogger`
  * `modbus_rtu`
  * `modbus_tcp`
  * `bluetooth`
  * `analog_out`
  * `hart`
  * `ethernet_ip`
  * `profinet`
  * `display`
  * `parameter_scripts`
  * `calibration`



In order to sign a file for use with `xwlicense`, the `sign_license.py` script in the `scripts/` directory is used. The AES key is supplied using the `-k` option:
    
    
    $ scripts/sign_license.py -k a10c613cd4d3bfe4f080bad2055634de license.txt
    [...]
    # license created on 2023-07-24T14:19:08.383950 by user
    UUID = 0042002A-3037510B-39313636
    datalogger = permanent
    modbus_tcp = 2023-08-01
    bluetooth = permanent
    analog_out = none
    sign = 477f2dd64125576823c98dfb655a251ae7c8b780a535522bd4444839b9cad720

It can also be written directly to a file as follows:
    
    
    $ scripts/sign_license.py -k a10c613cd4d3bfe4f080bad2055634de license.txt license.sgn
    [...]
    signed license file written to license.sgn.

## Installing a license

To install a license file on a unit, execute the `xwlicense` command via RCP, then paste the contents of the signed license file:
    
    
    xwlicense
    ;start;1
    UUID = 0042002A-3037510B-39313636
    datalogger = permanent
    modbus_tcp = 2023-08-01
    bluetooth = permanent
    analog_out = none
    sign = 477f2dd64125576823c98dfb655a251ae7c8b780a535522bd4444839b9cad720
    ;end;1;0;OK

### As superuser

Superusers have access to the `pwlicense` command, which works like `xwlicense`, but ignores the `UUID` and `sign` fields. This allow a single license file (signed or unsigned) to be installed to any device, e.g. in production.

## Viewing license information

The `xrlicense` command can be used to view license information:
    
    
    xrlicense
    ;start;1
    (*) datalogger=permanent
    ( ) modbus_rtu=none
    (*) modbus_tcp=2023-08-01
    (*) bluetooth=permanent
    ( ) analog_out=none
    ;end;1;0;OK

A `(*)` means that the license is currently active.

## Internals

To ensure authenticity, a hash of the license file’s contents is formed, then that hash is encrypted using AES128 in ECB mode. The firmware decrypts the hash and compares it to the hash of the actual contents, ensuring that the file has not been tampered with.

To create the hash, all INI keys and values are first concatenated in order without any separators, the resulting string is then hashed with SHA256. For example:
    
    
    foo=bar
    baz=9001
    
    
    $ echo -n foobarbaz9001 | sha256sum | cut -d' ' -f1
    e52be5978bac14a1edfdf1aa1760e28d30e7a3df44d0963d1c92e5595d56c466
    $ echo -n e52be5978bac14a1edfdf1aa1760e28d30e7a3df44d0963d1c92e5595d56c466 |\
        xxd -r -p |\
        openssl aes-128-ecb -nopad -K a10c613cd4d3bfe4f080bad2055634de |\
        xxd -p -c 32
    1d186ebd0aa284d70c076f200f936401d041d89a26439e9984b5648964c5037d
