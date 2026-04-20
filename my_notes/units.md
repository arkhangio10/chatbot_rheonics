# './parameter/units.md'

# Parameter unit conversion

The user can choose the physical units each parameter is represented in.

## Document Changelog

Date | firmware version | Author  
---|---|---  
2023-07-31 | `04.xx/7-72-g43a0c45a3c` | Armin Brauns  
2023-08-03 | `04.xx/7-122-gc1b34c8ab6` | Armin Brauns  
|  |   
  
## Internal vs. output units

All calculation is performed on _internal units_. For POOL2 parameters, these are the units _declared_ during script creation (`-u` parameter of `mkparascript.sh`). For POOL0 and POOL1 parameters, they are defined as follows:

Dimension | Unit  
---|---  
Temperature | °C  
Frequency | Hz  
Dynamic Viscosity | mPa*s  
Kinematic Viscosity | cSt  
Density | g/cm³  
  
Only once all calculation is complete are parameter values converted to their user-configured _output units_. These converted values are then sent to e.g. fieldbus modules and the display.

## Configuring parameter units

Configuration happens through the `xwparameter` RCP command. For every parameter, an `output_unit` property specifies the desired _output unit_ ; the numeric unit indices are listed on the [Rheonics website](https://support.rheonics.com/en/support/solutions/articles/81000393237-units-translation-table-for-field-devices).

As an example, setting the _output unit_ for parameter 12 (Viscosity) to cP (index 2):
    
    
    xwparameter
    ;start;1
    [parameter12]
    output_unit=2
    ;end;1;0;OK

Not all _output units_ are compatible with all _internal units_ , for example a density cannot be represented in °C. If such an invalid configuration is encountered, no conversion is performed and the parameter is emitted in its _internal unit_ , and its `PARAMETER_STATUS_CONFIG_ERROR` status flag is raised.

## Note on writing scripts

When writing scripts, all input values are in _internal units_. Unit conversion also affects POOL2 script output, i.e. the output conversion will take place according to the parameter’s `output_unit` value. A parameter referencing a script must have an `output_unit` compatible with the script’s _declared unit_.

## Note on Calibration and (non-configurable) Limits

For ease of use, values are passed to the `wrparasample` and `wrparacalib` RCP commands in _output units_. They are immediately converted back to _internal units_ by the firmware, those values are then used to calculate the calibration coefficients. The coefficients are applied to _internal units_ , so consumers of the parameter configuration (e.g. Rheonics Control Panel) must take care not to accidentally apply them to _output units_.

All limits are currently hard-coded in the source and are in _internal units_.

The values shown in `xrparacalib` (`lab`, `sample`, and `interpolation_cutoff`) are in _internal units_.
