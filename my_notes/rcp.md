# './rcp.md'

# Rheonics Control Protocol (RCP)

The Rheonics Control Protocol allows interacting with a unit in the field for configuration and maintenance.

## Document Changelog

Date | firmware version | Author  
---|---|---  
2023-07-31 | `04.xx/7-72-g43a0c45a3c` | Armin Brauns  
2023-08-03 | `04.xx/7-126-gde517eba80` | Armin Brauns  
|  |   
  
## RCP command syntax

Most RCP commands start either with the letter `x` (for user-accessible commands) or `p` (for commands only used during production). The second letter then specifies whether the command reads data from the device (`r`) or writes data to the device (`w`). For example, `xruptime` is accessible to users and shows the system uptime, while `pwsenconf` is only accessible to production/superusers and modifies the sensor configuration.

After a valid command is entered, a line like `;start;N` is printed, where `N` is a sequence number that is incremented for each command invocation. After the command has finished, `;end;N;R;S` is printed, where `N` is the same sequence number as in the start tag, `R` is the return code, and `S` is either `OK` (if successful) or `NOK` (in case of error). The return code is zero in case of success.

## Connecting to the USB-RCP from a Linux PC

Most comfortable way to connect is picocom, replace /dev/ttyACM0 with the serial port suited for your system.
    
    
    $ picocom --omap crcrlf --echo -b 115200 /dev/ttyACM0

use the keyboard combo `ctrl+a ctrl+x` to exit. `ctrl+a ctrl+h` will give you help.

## Security levels

The RCP console has three different security levels:

  * None (0)
  * User (1)
  * Service (2)
  * Superuser (3)



Some commands, like those beginning with `p`, can only be accessed through higher security levels - command dependent.

The current security level can be changed using the `xwpass` command, which takes as its sole argument a password. This password determines the resulting security level. If the password is incorrect, or no password is specified, the security level is reset to “None” (0).

The current security level can be shown using the `xroperation` command.

## List of RCP commands

A complete list of RCP commands along with a short description for each can be printed using the `xhelp` command. Command arguments in `[square brackets]` are optional, arguments in `ALL CAPS` are placeholders and must be replaced with an actual value. The `|` pipe symbol means that exactly one of the specified arguments should be supplied (read as “or”).

## Filesystem commands

  * `fschdir DIR` [SMET]: Changes the working directory to `DIR`
  * `fsdir` [SMET]: Lists files and directories in the current directory
  * `fsgetcwd` [SMET]: Prints the current working directory
  * `fsmkdir DIR` [SMET]: Creates a new directory
  * `fsrm PATH` [SMET]: Deletes a file or empty directory
  * `fsdownload FILENAME` [SMET]: Enters YMODEM mode to download a file from the unit
  * `fsupload` [SMET]: Enters YMODEM mode to upload a file to the unit
  * `xdataformat` [SMET]: Reformats the SD card/eMMC, destroying all data



## Reboot commands

  * `xreset` [SMET, GPLL]: Resets the system
  * `fw_asb_bootloader` [SMET]: Enters ASB bootloader mode, allowing ASB firmware to be updated
  * `fw_ifb_bootloader` [SMET-DFU]: Reboots the device into DFU bootloader mode, only available in DFU builds
  * `fw_fault_reset` [SMET, GPLL]: Causes an addressing fault, resetting the system
  * `xwwdgtest` [SMET]: Purposefully lets the watchdog timer expire, triggering a device reset



## ASB commands

  * `pwasboff` [SMET, GPLL]: Powers the ASB off
  * `pwasbon` [SMET, GPLL]: Powers the ASB on
  * `pwasbsn` [SMET]: Powers the ASB on and updates `Esn_str`/`Ehw_str` from config
  * `pwasbrtd` [SMET]: Powers the ASB on and updates `TRf`/`TRo` coefficients from config



## Config commands

### Special

  * `xwconfigreload` [SMET, GPLL]: Forces all configuration to be reloaded from non-volatile storage
  * `xwconfigreset CONFIGS` [SMET, GPLL]: Resets the configurations specified by `CONFIGS` to their factory defaults. `CONFIGS` is the sum of: - 1 for IO config - 2 for sensor config - 4 for parameter config - 8 for sensor hardware config (e.g. 6 for sensor and parameter)



### IO config

  * `xrchannel` [SMET, GPLL]: Prints IO configuration data
  * `xwchannel` [SMET, GPLL]: Enters config mode. Allows updating common IO configuration fields
  * `pwchannel` [SMET, GPLL]: Enters config mode. Allows updating all IO configuration fields



### Sensor config

  * `xrsenconf` [SMET, GPLL]: Prints sensor configuration data
  * `xwsenconf` [SMET, GPLL]: Enters config mode. Allows writing common sensor config fields
  * `pwsenconf` [SMET, GPLL]: Enters config mode. Allows writing all fields of sensor configuration



### Parameter config

  * `xrparameter` [SMET, GPLL]: Prints parameter configuration data
  * `xwparameter` [SMET, GPLL]: Enters config mode. Allows updating parameter configuration



### License config

Further documentation can be found in `licensing.md`.

  * `xrlicense` [SMET, GPLL]: Prints software licensing information
  * `xwlicense` [SMET, GPLL]: Enters config mode. Allows updating licensing information for software components
  * `pwlicense` [SMET, GPLL]: Enters config mode. Allows updating licensing information (without signature check)



### Script config

  * `xwscript SCRIPT_IDX [delete]` [SMET, GPLL]: Allows updating the script at the specified index. If “delete” is specified, deletes the script. Otherwise enters config mode to upload a new script
  * `xrscript SCRIPT_IDX` [SMET, GPLL]: Prints information about the script at the specified index



### Calibration

  * `xrparacalib` [SMET, GPLL]: Prints parameter calibration data for all parameters

  * `xwparacalib` [SMET, GPLL]: Enters config mode. Allows writing parameter calibration data

  * `wrparasample PARA_IDX SAMPLE_IDX [SAMPLE_VALUE]` [SMET]: Takes a parameter calibration sample. If `SAMPLE_VALUE` is not specified, use the latest raw value

  * `wrparalab PARA_IDX LAB_IDX LAB_VALUE` [SMET]: Sets a parameter’s lab value to the given value

  * `wrparacalib PARA_IDX offset|linear` [SMET]: Performs offset or linear calibration of the given parameter

  * `wrparamode PARA_IDX user|factory` [SMET]: Sets the given parameter’s calibration source to either the user or factory provided values

  * `xrsencalib` [SMET, GPLL]: Prints sensor calibration coefficient configuration

  * `xwsencalib` [SMET, GPLL]: Enters config mode. Allows writing sensor calibration coefficients

  * `xwdensity` [SMET, GPLL]: Enters config mode. Allows writing density calibration data

  * `xwpressure PRESSURE|nan` [SMET, GPLL]: Sets the pressure compensation value. Pass “nan” to disable pressure compensation




### Limits

  * `xrlimits` [SMET, GPLL]: Prints the maximum critical values experienced by the unit
  * `pwlimitsreset` [SMET, GPLL]: Resets the recorded maximum critical values experienced by the unit



### FPGA config (GPLL)

  * `xrshwconf` [GPLL]: Prints FPGA configuration data
  * `xwshwconf` [GPLL]: Enters config mode. Allows updating FPGA configuration
  * `xrfpgaregs` [GPLL]: Prints the current value of FPGA SPI registers



### ASB config (SMET)

  * `xrshwconf` [SMET]: Prints ASB configuration data
  * `xwshwconf` [SMET]: Enters config mode. Allows updating ASB configuration
  * `pwshwconf` [SMET]: Enters config mode. Allows updating all ASB configuration



## Ethernet

  * `xrethernet` [SMET]: Prints information about the current state of the ethernet interface
  * `xrenew` [SMET]: Forces the ethernet interface’s DHCP lease to be renewed



## Misc

  * `xrdatetime` [SMET, GPLL]: Prints the current RTC date and time as a Unix timestamp (seconds since Unix epoch)
  * `pwdatetime UNIX_TIMESTAMP` [SMET, GPLL]: Sets the current RTC date and time using a Unix timestamp (seconds since Unix epoch)
  * `xdetect` [SMET]: Flashes device LEDs to identify the unit currently being communicated with
  * `xhelp` [SMET, GPLL]: Prints information about available shell commands
  * `xruptime` [SMET, GPLL]: Prints the system uptime
  * `xversion` [SMET, GPLL]: Prints the system version
  * `xwpass [PASSWORD]` [SMET, GPLL]: Authenticates the user. Resulting permission level depends on the password used
  * `xrunits` [SMET, GPLL]: Prints all available parameter units
  * `xrbtkey` [SMET]: Display the current bluetooth pairing key
  * `xwbtkey PASSKEY` [SMET]: Used to enter a bluetooth pairing key when no display is attached.



## Operational

  * `xmonitor-od` [SMET, GPLL]: Prints latest calculated output data in ASB string format
  * `xmonitor-csv-od` [SMET, GPLL]: Prints latest calculated output data in CSV format
  * `xmonitor` [SMET, GPLL]: Continously prints calculated output data in ASB string format
  * `xmonitor-csv` [SMET, GPLL]: Continously prints calculated output data in CSV format
  * `xrcurrentloop` [SMET, GPLL]: Prints the value of all 4-20mA current loop outputs (in mA)
  * `xrlisten` [SMET, GPLL]: Continuously prints raw data received from ASB (SMET)/user.py (GPLL). The string reflects the data parsed and actually understood by the IFB, rather than the exact text received from the ASB.
  * `xwsimulate [ASB_STRING]` [SMET]: Starts ASB simulation using the specified string instead of the real values. Omit the argument to stop simulation



## Internals

  * `xroperation` [SMET, GPLL]: Prints operational data of the device
  * `xrstat` [SMET, GPLL]: Prints statistics about currently running threads
  * `xwdebug [SOURCE none|err|wrn|inf|dbg]` [SMET, GPLL]: Sets the log level of the specified log source. Without arguments, lists all registered log sources and their configured log levels.
  * `xrcoredump` [SMET]: Prints the last captured crash dump, if any (long output)
  * `xwrcclear` [SMET, GPLL]: Clears the reset causes shown in xrstat



## Config Mode known INI sections and keys

See product-specific `ini_keys.json.html` documentation.
