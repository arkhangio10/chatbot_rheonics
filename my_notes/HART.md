# './HART.md'  
  
# HART stack

Author | Date | Comment  
---|---|---  
Roland Lezuo | 2022-01-27 | Document created  
Roland Lezuo | 2022-03-01 | Blink patterns  
  
## General Information

Available on analog (mA) channel 1 only. HART stack is started per default, can be configured via `Has_HART` of `pwsenconf` command.

There are 4 Process Variables known to HART, they are mapped as follows:

  * **PV** (Primary variable) is mapped (hardcoded) to the parameter exported on Channel1 (`[analog0]`).

  * **SV** (Secondary variable) is mapped (configurable) to SV_parameter (default 2)

  * **TV** (ternary/third variable) is mapped (configurable) to TV_parameter (default 8)

  * **QV**(FV) (quad/fourth variable) is mapped (hardcoded) to sensor status (please not that QV is a float-encoded 16 bit integer)




The HART mapping is implemented as read-only mapping (i.e. we only export to the network). There would be options to configure certain HART specific value (Tags, Addresses). If need arises this can be implemented. Other things like date and serial number configuration is too limited (number of chars, limitations on chars) that it makes no sense to implement this functions.

## LED Blinking patterns

HART LED on Display | Meaning  
---|---  
always OFF | HART disabled (pwsenconf)  
always GREEN | HART enabled, idle state  
blinking GREEN | bytes received, command not completed yet  
blinking RED | bytes received, data corrupted  
always RED | loop is open, no HART communication possible  
  
## Configure parameter to SV,TV mapping

`xwchannel`

`[hart]` `SV_parameter=2` `TV_parameter=8` `short_addr=0`

## Implemented universal HART commands

The following HART commands are implemented and known to work:

  * 0 - READ UNIQUE IDENTIFIER: TODO document unit/mfg values
  * 1 - READ PV
  * 2 - READ LOOP CURRENT
  * 3 - READ PV,SV,TV,QV and LOOP CURRENT
  * 7 - READ LOOP CONFIG
  * 8 - READ DYN VAR CLASSIFICATION - always 0 (unclassified) for PV,SV,TV, 81 (analytic) for QV
  * 11 - READ UNIQ DEV FROM TAG
  * 12 - READ MESSAGE - always empty message
  * 13 - READ TAG, DESC, DATE - tag is constructed from MAC address of device, Descriptor is serial and sensor type, date is 01-01-1970 (always)
  * 15 - READ DEVICE INFORMATION
  * 20 - READ LONG TAG - will return same as description (e.g. “RH B05-0107 SRV”)



## Incomplete universal HART commands

  * 6 - WRITE POLLING ADDR - will fail, device is in read-only mode

  * 9 - READ DEV VAR WITH STATUS - not fully implemented

  * 14 - READ TRANSDUCER INFO - not fully implemented

  * 16 - READ ASSEMBLY INFO - not fully implemented

  * 17 - WRITE MESSAGE - will fail, device is in read-only mode

  * 18 - WRITE TAG, DESCR, DATE - will fail, device is in read-only mode

  * 19 - WRITE ASSEMBLY INFO - will fail, device is in read-only mode

  * 21 - READ UNIQ FROM LONG TAG - fails

  * 22 - WRITE TAG - will fail, device is in read-only mode

  * 38 - RESET CONFIG CHANGED FLAG - will fail, device is in read-only mode

  * 48 - READ ADD DEV STATUS - not fully implemented




## Device specific HART commands

### Command 128 - Set SRV Densitity

This command is available in HART-7 (only), it accepts 6 Float values which are the Do0 to Do5 (c.f. xwdensity).

#### Request Data Bytes

Bytes | Format | Description  
---|---|---  
0-3 | Float | Do0  
4-7 | Float | Do1  
8-11 | Float | Do2  
12-15 | Float | Do3  
16-19 | Float | Do4  
20-23 | Float | Do5  
  
#### Response Data Bytes

mirrors request data bytes

#### Command-Specific Response Codes

Code | Class | Description  
---|---|---  
0 | Success | Command accepted, does not guarantee that data will be accepted by sensor  
5 | Error | Command frames too short  
7 | Error | Device is not a SRV and thus does not accept density parameters  
64 | Error | Command not implemented (it’s only available in HART-7)  
  
### Command 129 - Get SRV Densitity

This command is available in HART-7 (only), it returns 6 Float values which are the Do0 to Do5 (c.f. xwdensity).

#### Request Data Bytes

there are no request data bytes

#### Response Data Bytes

See command 128 Response Data Bytes

#### Command-Specific Response Codes

There are no command specific response codes.
