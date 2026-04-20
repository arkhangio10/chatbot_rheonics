# './display.md'

# SMET Display

The display consists of a header and footer showing general status information, and a central content window that shows context-dependent information.

## Header

### Sensor status

This field is set depending on the sensor status value as described in [error_codes.md.html](../parameter/error_codes.md.html).

  1. If the sensor status is 0, shows “RUNNING”.
  2. Otherwise, if “PLL frequency different from sensor frequency” (`0x0001`) is set, shows “UNSTABLE”.
  3. Otherwise, if “PLL not locked” (`0x0002`) or “Incorrect PLL lock” (`0x0004`) are set, shows “UNLOCKED”.
  4. Otherwise, if “Too hot” (`0x0020`) is set, shows “!!! DANGER !!!”.
  5. Otherwise, shows “ERROR”.



### Process status

This field is initially set to “UNAVAILABLE” on startup. Once initialization is complete and parameter values are being generated, its value depends on the parameters’ status values, as described in [error_codes.md.html](../parameter/error_codes.md.html):

  1. If an “Out-of-range warning” (`0x1000`/`0x2000`) or “Out-of-range alarm” (`0x4000`/`0x8000`) is raised on any parameter, shows “OUT OF RANGE”.
  2. Otherwise, shows “WITHIN LIMITS”.



## Footer

The footer alternates between showing the sensor’s serial numbers and software version, and, if enabled, the status of the ethernet interface.

## Content windows

### Process

The process window shows the values of three parameters. The shown parameters and their precision can be configured through the `[lcd/line*]` sections in the `xwchannel` RCP command.

### Bluetooth pairing

When an attempt is made to pair with the device over Bluetooth, the pairing code is shown on the display.
