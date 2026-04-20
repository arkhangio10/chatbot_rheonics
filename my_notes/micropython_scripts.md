# './parameter/micropython_scripts.md'

# Parameter Python Interface as implemented by the GPLL Firmware

This document describes the Python API implemented by the GPLL firmware. It is used by parameter scripts which can be provided by the user and are executed by the firmware as part of the parameter calculation.

## Document Changelog

Date | gpll firmware version | Author  
---|---|---  
2023-07-04 | `04.xx/6-29-g1b2de02` | Roland Lezuo  
2023-07-10 | `04.xx/6-32-g8939a86` | Armin Brauns  
2023-07-12 | `04.xx/6-38-g9d20b0f` | Armin Brauns  
2023-08-01 | `04.xx/7-93-g89ee5184c7` | Armin Brauns  
|  |   
  
## Relevant Source Files

  * `smet_gpll_fw/lib/shared_sources/rh_mpy/mpy_parameter_scripts.c`
  * `smet_gpll_fw/lib/shared_sources/rh_config/config_defaults.c`
  * `smet_gpll_fw/smet/include/msgtypes.h`



## Execution Model

Each parameter script is treated as an separate python module, i.e. their runtime environments are separated. A single non-blocking function _main_ has to be implemented by the user:
    
    
    main(rodata: dict[str, Any], params: list[Parameter])

_`rodata`_ contains read-only values which can be used by the parameter script for calculation. Any attempt to update the values will raise an exception.

Key | Type | Meaning  
---|---|---  
`T` | `float` | Sensor temperature  
`f` | `float` | Sensor resonant frequency  
`df` | `float` | Frequency difference  
`Q` | `float` | Q factor  
`fr` | `float` | Frequency at 0° phase shift  
`df-` | `float` | Frequency at -45° phase shift  
`df+` | `float` | Frequency at +45° phase shift  
`Fv` | `int` | ASB `Fv` field (SMET only)  
`ph` | `int` | ASB `ph` field (SMET only)  
`I-` | `int` | ASB `I-` field (SMET only)  
`I+` | `int` | ASB `I+` field (SMET only)  
`Do0`..`Do5` | `float` | `Do*` values from sensor config  
`Di0`..`Di5` | `float` | `Di*` values from sensor config  
`Fair0`..`Fair2` | `float` | `Fair*` values from sensor config  
`Dfair0`..`Dfair2` | `float` | `Dfair*` values from sensor config  
`Va1`.. `Va9` | `float` | `Va*` values from sensor config  
  
_`params`_ contains all current parameter values, indexed from 0. Each parameter is an object with the following attributes:

Attribute | Type | Writable  
---|---|---  
`value` | `float` | yes  
`status` | `int` | yes  
`unit` | `int` | no  
  
The _`main`_ function may modify value and status fields in _`params`_. Any updated parameter values will overwrite the older ones in the firmware’s copy of current parameter values after the function returns.

## Utility functions

The `rh_utils` module provides the following utility functions:

  * `def coeffs(coeffs, base, start=0):`  
Calculates a polynomial with coefficients `coeffs` to a base of `base`, with exponents starting at `start` and incrementing. E.g. `coeffs([7, 5, 9], x, 1)` is the same as `7*x**1 + 5*x**2 + 9*x**3`.

  * `def rho_p_t(p, t):`  
`p`: alcoholic strength by mass in %  
`t`: temperature in °C, from -20 °C to +40 °C

  * `def brent(func, lower_bound, upper_bound, max_iterations=100, tolerance=1e-6):`  
Brent’s method for root finding. Finds a value `x` between `lower_bound` and `upper_bound` where `func(x)` is equal or close to zero. `func` must be a continuous function, and `func(lower_bound)` and `func(upper_bound)` must be on opposite sides of the X axis.




## Example Script
    
    
    def main(rodata, params):
        if abs(params[13].value) > 1e-9:
            params[3].value = params[12].value / params[13].value
            params[3].status = 0x0000
        else:
            params[3].value = 0.0
            params[3].status = 0x0008

## Uploading scripts

To upload scripts to the unit, they first have to be compiled using the `mkparascript`/`mkparascript.exe` utility in the `scripts/` subdirectory. The utility expects the following command line arguments:

  * `-n parameter_name`: the name of the parameter calculated by the script
  * `-u parameter_unit`: the unit of the parameter calculated by the script (see [this table][RhUnitsList] on the Rheonics website)
  * `-i script_index`: the desired script index (0 to 2)
  * `script_file`: the file containing the micropython script



For example, to compile a script into script index 2, which produces a Density in °P:
    
    
    $ ./mkparascript -n Density -u 58 -i 2 Plato_smet_script.py
    xwscript 2
    Density|58|678|TQcAHxAiGnBhcmFfc2NyaXB0XzIADwhtYXRoAIFjgkUMc3RhdHVzABQ8bGlzdGNvbXA+AAJMAAJS
    AAJBAAZ3ZHIADHJvZGF0YQAMcGFyYW1zAIJLAmoACwjhGnZECJq5OEQI7MFARAiFC0dECEhRTUQI
    UphTRAhc31lECMMlYEQIhWtmRAhIsWxECGb2ckQIXmdLPwhRTF45CIj3RD8I1ehVOQi3fT8/CGr3
    KzkIbFo5PwgHQjI5CCkGND8IXqAkOQilFS8/CKinDzkIhBIqPwhOKwU5CA3jKj8IMGXgOQgdVSE/
    CHMwGzkIuI55RAg7/wdDCGiRHUQIe+SKRAiNNxpEiRxINgFGICJpICAiIiIiIiIiIkYgJycoJycn
    JyhLRIBRGwIWAiMAIwEiPIArBBYHIwIjAyMEIwUjBiMHIwgjCSMKKwkWCCML0SMMKwIjDdEjDisC
    Iw/RIxDRKwIjEdEjEisCIxPRIxQrAiMV0SMWKwIjF9EjGCsCIxnRIxrRKwIjG9EjHCsCKwkWCSMd
    FgoyABYDUWMBjhyaECkDCwyAISomHy0lTzIwJSEuUyU6SwmxjVUTBCKHaPTCsYJVEwTDEgeBVbJX
    W9dGBxIHgFXXQkJaWUSdgRIHg1WzV1vXRgcSB4JV10JCWllEh4GUs/MnCbkgAAESDRIIEgk0AjQB
    xBINtLSBUS4CVTQCX0tjMALFxrWyV1vXRgS210JCWllEzIC2tfMnCbK1EggSDlX3trLzJQn39LYS
    CBIOgfJV97K18yUJ9/Ty98e3Egr3yCMeuIP59CMfuIL59PMjILj08iMh87GVVRgEgLGVVRgFQpt/
    QkaBsZVVGAVRYwGCMGoKBg8PgCUrALFfSxgwAsIwAsPEsrMlAPTztCUAgvn08y8UQiZj

This entire output can then be copy-pasted into the RCP console:
    
    
    xwscript 2
    ;start;1
    Density|58|678|TQcAHxAiGnBhcmFfc2NyaXB0XzIADwhtYXRoAIFjgkUMc3RhdHVzABQ8bGlzdGNvbXA+AAJMAAJS
    AAJBAAZ3ZHIADHJvZGF0YQAMcGFyYW1zAIJLAmoACwjhGnZECJq5OEQI7MFARAiFC0dECEhRTUQI
    UphTRAhc31lECMMlYEQIhWtmRAhIsWxECGb2ckQIXmdLPwhRTF45CIj3RD8I1ehVOQi3fT8/CGr3
    KzkIbFo5PwgHQjI5CCkGND8IXqAkOQilFS8/CKinDzkIhBIqPwhOKwU5CA3jKj8IMGXgOQgdVSE/
    CHMwGzkIuI55RAg7/wdDCGiRHUQIe+SKRAiNNxpEiRxINgFGICJpICAiIiIiIiIiIkYgJycoJycn
    JyhLRIBRGwIWAiMAIwEiPIArBBYHIwIjAyMEIwUjBiMHIwgjCSMKKwkWCCML0SMMKwIjDdEjDisC
    Iw/RIxDRKwIjEdEjEisCIxPRIxQrAiMV0SMWKwIjF9EjGCsCIxnRIxrRKwIjG9EjHCsCKwkWCSMd
    FgoyABYDUWMBjhyaECkDCwyAISomHy0lTzIwJSEuUyU6SwmxjVUTBCKHaPTCsYJVEwTDEgeBVbJX
    W9dGBxIHgFXXQkJaWUSdgRIHg1WzV1vXRgcSB4JV10JCWllEh4GUs/MnCbkgAAESDRIIEgk0AjQB
    xBINtLSBUS4CVTQCX0tjMALFxrWyV1vXRgS210JCWllEzIC2tfMnCbK1EggSDlX3trLzJQn39LYS
    CBIOgfJV97K18yUJ9/Ty98e3Egr3yCMeuIP59CMfuIL59PMjILj08iMh87GVVRgEgLGVVRgFQpt/
    QkaBsZVVGAVRYwGCMGoKBg8PgCUrALFfSxgwAsIwAsPEsrMlAPTztCUAgvn08y8UQiZj
    ;end;1;0;OK

If you want to store the entire output into a file use bash redirection:
    
    
    $ ./mkparascript -n Density -u 58 -i 2 Plato_smet_script.py > Plato_smet_script.txt

the example above will create (and overwrite) a test-file names _Plato_smet_script.txt_.

## Deleting scripts

Parameter scripts can be deleted using the `xwscript` command, by passing `delete` as the second argument:
    
    
    xwscript 1 delete
    ;start;1
    ;end;1;0;OK

## Getting information about installed scripts

The `xrscript` command can be used to show information about installed scripts:
    
    
    xrscript 2
    ;start;1
    name=Plat
    unit=58
    length=678
    ;end;1;0;OK
