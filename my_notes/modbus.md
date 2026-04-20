# './modbus/modbus.md'

# MODBUS on SMET

MODBUS is a fieldbus protocol, smet supports RTU and TCP.

## Document Changelog

Date | firmware version | Author  
---|---|---  
2023-09-22 | `04.xx/7-214-gf786956` | Roland Lezuo  
  
## MODBUS Interfaces

MODBUS variant | protocol specific details  
---|---  
TCP | IPv6, bind address ::, port 502  
TCP | IPv4, bind address 0.0.0.0, port 502  
RTU | RS485 modbus, 38400 8O1, slave address 1  
RTU | USB-CDC, slave address 1 (2nd serial port when attaching USB)  
  
slave address, baudrate and parity can be configured (IO config).

## MODBUS mapping

c.f. modbus-mapping.xlsx
