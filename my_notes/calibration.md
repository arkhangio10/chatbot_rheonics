# './parameter/calibration.md'

# Parameter Calibration

Each parameter can optionally be calibrated using one of two methods:

  * Offset calibration: apply a constant offset to the raw value
  * Linear calibration: apply a constant slope and offset to the raw value



Calibration is performed using the following steps:

  1. The sensor is brought to a stable state in a test fluid with known parameter values
  2. The `wrparasample [parameter_idx] 0` command is used to store the currently measured value at sample index 0
  3. The `wrparalab [parameter_idx] 0 [lab_value]` command is used to store the actual value
  4. For linear calibration, steps 2 and 3 are repeated with a second liquid with different properties, using sample/lab index `1` instead of `0`
  5. The calibration coefficients are calculated and applied: 
     * For offset calibration, `wrparacalib [parameter_idx] offset`
     * For linear calibration, `wrparacalib [parameter_idx] linear`



Once a linear calibration has been performed, the slope of the calibration curve is left unchanged by subsequent offset calibrations. This allows the offset, which is expected to change more over time than the slope, to be recalibrated quickly using a single-point measurement, while keeping the slope unchanged.

To switch between factory and user calibration, use `wrparamode [parameter_idx] factory` and `wrparamode [parameter_idx] user`.

## Calibration propagation

Whenever calibration data (lab values, sample values, coefficients) for one parameter is changed, it is propagated to all _related parameters_.

  * For a POOL0 or POOL2 parameter, the _related parameters_ are all POOL1 parameters that derive from it using `parameter_source_idx`, either directly or through another _related_ POOL1 parameter.
  * For a POOL1 parameter, the _base parameter_ is obtained by recursively following `parameter_source_idx` relationships until a non-POOL1 parameter is encountered. The _related parameters_ are the _base parameter_ as well as its _related parameters_.



This ensures that calibration for a given physical quantity is applied to all parameters derived from that quantity.

## Interpolation to (0, 0)

To prevent negative values and discontinuities, user calibration is done in two pieces. Where both the raw value and calibrated value are larger than the parameter’s `interpolation_cutoff` parameter, the user calibration is applied as-is. From the point on the calibration curve where either raw value or calibrated value cross the cutoff value, the calibrated value is instead interpolated toward (0, 0). If this cutoff is being applied, the Out Of Calibration Range error flag (`0x0080`) is raised on the parameter.

Factory calibration is always applied as-is without any interpolation.

## Parameter calibration expiry

Each parameter can optionally be set to require re-calibration after a specific amount of time. If this time elapses, a Calibration Error (`0x0040`) is raised in the parameter status flags.

The `last_calibration_ts` and `required_calibration_interval` keys in the `xwparacalib` RCP command are used to update the calibration expiry: - `last_calibration_ts` is the UNIX timestamp of the last performed calibration. - `required_calibration_interval` is the number of seconds the calibration is valid for. If this is set to `0`, the calibration is valid forever/the expiry mechanism is disabled for this parameter.

If calibration expiry is enabled (`required_calibration_interval` is nonzero), the RTC must be set correctly. If an RTC error is detected, the Calibration Error flag is raised immediately.
