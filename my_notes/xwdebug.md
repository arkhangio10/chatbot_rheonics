# './xwdebug.md'

# Viewing debug logs using `xwdebug` command

Many components inside the firmware can produce log messages. By default, the RCP terminal does not show any of them (since they would interfere with the ASB strings being printed), but using the `xwdebug` command, they can be selectively enabled.

Each log message has one of four different log levels: `ERR`, `WRN`, `INF` or `DBG`. For each log source (corresponding to firmware modules) the most verbose level of log messages to be printed can be configured. Running the `xwdebug` command without any arguments produces a list of all log sources, along with their current log level and their maximum supported log level:
    
    
    wdebug
    ;start;1
    source                         | current | maximum
    -------------------------------|---------|---------
    adc_stm32                      | none    | inf
    asb                            | none    | inf
    bluetooth                      | none    | inf
    bt_adv                         | none    | inf
    bt_att                         | none    | inf
    bt_conn                        | none    | inf
    bt_crypto                      | none    | inf
    bt_data                        | none    | inf
    bt_dis                         | none    | inf
    bt_driver                      | none    | inf
    bt_ecc                         | none    | inf
    bt_gatt                        | none    | inf
    bt_hci_core                    | none    | inf
    bt_host_crypto                 | none    | inf
    bt_id                          | none    | inf
    bt_keys                        | none    | inf
    bt_l2cap                       | none    | inf
    bt_rpa                         | none    | inf
    bt_smp                         | none    | inf
    cbprintf_package               | none    | inf
    chip_temp                      | none    | inf
    config                         | none    | inf
    config_io                      | none    | inf
    dac_mcp4728                    | none    | inf
    disk                           | none    | inf
    display_st7528i                | none    | inf
    eeprom_at2x                    | none    | inf
    eth_stm32_hal                  | none    | inf
    ethernetip                     | none    | inf
    flash_stm32                    | none    | inf
    fs                             | none    | inf
    fymodem                        | none    | inf
    getopt                         | none    | inf
    gpio_mcp230xx                  | none    | inf
    gpio_mcp23xxx                  | none    | inf
    hart_serial                    | none    | inf
    hart_state                     | none    | inf
    i2c                            | none    | inf
    i2c_ll_stm32                   | none    | inf
    i2c_ll_stm32_v2                | none    | inf
    led                            | none    | inf
    log                            | none    | inf
    log_mgmt                       | none    | inf
    log_uart                       | none    | inf
    lvgl                           | none    | inf
    lwip_ftpd                      | none    | inf
    main                           | none    | inf
    mbport                         | none    | inf
    modbus                         | wrn     | inf
    mpu                            | none    | inf
    mpy                            | none    | inf
    msgqueues                      | none    | inf
    net_arp                        | none    | none
    net_buf                        | none    | inf
    net_buf_simple                 | none    | inf
    net_conn                       | none    | none
    net_core                       | none    | none
    net_ctx                        | none    | none
    net_dhcpv4                     | none    | none
    net_dns_resolve                | none    | none
    net_ethernet                   | none    | none
    net_ethernet_mgmt              | none    | none
    net_ethernet_stats             | none    | none
    net_hostname                   | none    | none
    net_icmpv4                     | none    | none
    net_icmpv6                     | none    | none
    net_if                         | none    | none
    net_ipv4                       | none    | none
    net_ipv6                       | none    | none
    net_mgmt                       | none    | none
    net_nbr                        | none    | none
    net_pkt                        | none    | none
    net_route                      | none    | none
    net_sock                       | none    | none
    net_sock_addr                  | none    | none
    net_sock_packet                | none    | none
    net_sockets_raw                | none    | none
    net_stats                      | none    | none
    net_tc                         | none    | none
    net_tcp                        | none    | none
    net_udp                        | none    | none
    net_utils                      | none    | none
    network                        | none    | inf
    opener                         | none    | inf
    os                             | none    | inf
    parameter                      | none    | inf
    parameter_calculation          | none    | inf
    parameter_env                  | none    | inf
    parameter_script               | none    | inf
    pnet                           | none    | inf
    processio                      | none    | inf
    rh_msgqueues                   | none    | inf
    rh_rtc                         | none    | inf
    rh_terminal_ini                | none    | inf
    rh_terminal_script             | none    | inf
    rh_units                       | none    | inf
    smet_adc                       | none    | inf
    smet_display                   | none    | inf
    smet_hart                      | none    | inf
    smet_logger                    | none    | inf
    smet_net_rcp                   | none    | inf
    smet_terminal                  | none    | inf
    spi_ll_stm32                   | none    | inf
    stm32_sdmmc                    | none    | inf
    stm32_temp                     | none    | inf
    task_wdt                       | none    | inf
    terminal                       | none    | inf
    uart_stm32                     | none    | inf
    usb_cdc_acm                    | none    | none
    usb_dc_stm32                   | none    | inf
    usb_descriptor                 | none    | inf
    usb_device                     | none    | inf
    usb_transfer                   | none    | inf
    ;end;1;0;OK

In this example, the `modbus` module is the only one showing any messages (up to `WRN` level), and most modules (except for `net_*` modules) could be configured to show messages up to `INF` level.

The maximum possible log level is configured at build-time, if a higher log level is required, a special debug build needs to be created.

The active log level for a given source can be changed as follows:
    
    
    xwdebug smet_net_rcp inf
    ;start;2
    ;end;2;0;OK

Now, opening a connection to NET-RCP shows the `INF` level messages from the `smet_net_rcp` module on the terminal:
    
    
    [00:28:38.711,000] <inf> smet_net_rcp: Got new NET-RCP client
    [00:28:42.251,000] <inf> smet_net_rcp: NET-RCP client disconnected

Each message is prefixed by the `HH:MM:SS` timestamp measured since startup of the unit (uptime), the log level of the message, and the module that emitted the message.
