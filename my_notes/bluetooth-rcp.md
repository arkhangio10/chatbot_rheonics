# './bluetooth/bluetooth-rcp.md'

# Bluetooth-RCP (service `1995a701-efa6-4d2c-9c84-a0b001a4304b`)

SMET exposes a bluetooth service that gives access to the RCP command interface. Unlike the other BLE services, the device needs to be paired in order to use this service. Two characteristics are used for communication:

## Write (`1995a701-efa6-4d2c-9c84-a0b011a4304b`)

Data written to this characteristic is interpreted as input to RCP. Lines need to be terminated with `\r\n`.

## Read (`1995a701-efa6-4d2c-9c84-a0b021a4304b`)

After subscribing to NOTIFY on this characteristic, output produced by RCP will be available as NOTIFY messages.

## Testing

The interface can be tested using https://github.com/wh201906/SerialTest on Linux and Android.

  1. On the “Connect” tab, choose “BLE Central”
  2. Choose the SMET device in the device list, press “Connect”
  3. Complete the pairing request offered by the OS
  4. On the right-hand side, pick the service and characteristic IDs listed above
  5. On the “Data” tab, tick “Enable echo” and set the “Suffix” to `\r\n`
  6. Enter an RCP command into the text box, press “Send”


