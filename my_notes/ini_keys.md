# config/ini_keys.json

##  channel 

###  write commands 

command  |  required security  |  sensor_types  |  accessible key groups   
---|---|---|---  
**xwchannel** |  NONE  |  ANY  |  BASE   
**pwchannel** |  SUPERUSER  |  ANY  |  BASE  
PROD_CONFIG  
PRIVILEGED   
  
###  read commands 

command  |  required security  |  sensor_types  |  accessible key groups   
---|---|---|---  
**xrchannel** |  NONE  |  ANY  |  BASE  
PROD_CONFIG  
PRIVILEGED   
  
section  |  key  |  groups   
---|---|---  
analog0  
analog1  
analog2  |  source  |  BASE   
lower_limit   
upper_limit   
calib_low   
calib_high   
mode   
modbus  |  address  |  BASE   
baudrate   
parity   
hart  |  SV_parameter  |  BASE   
TV_parameter   
short_addr   
loop_powered   
pnet  |  station_name  |  BASE   
ethernet  |  dhcp  |  BASE   
ip   
mask   
gw   
dns   
port_terminal   
mac  |  PROD_CONFIG   
bluetooth  |  mac  |  PROD_CONFIG   
lcd/pstatus  |  enabled  |  BASE   
source   
lcd/line1  
lcd/line2  
lcd/line3  |  enabled  |  BASE   
source   
precision   
device  |  Location_ID  |  BASE   
Location_Name   
Location_coord_Lat   
Location_coord_Long   
Location_coord_Alt   
terminal  |  output_interval_s  |  BASE   
ftp  |  enabled  |  BASE   
user   
pass   
sdcard  |  log_every_n_cycle  |  BASE   
log_max_files  |  PRIVILEGED   
  
##  licensing 

###  write commands 

command  |  required security  |  sensor_types  |  accessible key groups   
---|---|---|---  
**xwlicense** |  NONE  |  ANY  |  BASE   
**pwlicense** |  SUPERUSER  |  ANY  |  BASE   
  
###  read commands 

command  |  required security  |  sensor_types  |  accessible key groups   
---|---|---|---  
**xrlicense** |  NONE  |  ANY  |  BASE   
  
_See separate licensing documentation_

##  paracalib 

###  write commands 

command  |  required security  |  sensor_types  |  accessible key groups   
---|---|---|---  
**xwparacalib** |  SERVICE  |  ANY  |  BASE   
  
###  read commands 

command  |  required security  |  sensor_types  |  accessible key groups   
---|---|---|---  
**xrparacalib** |  NONE  |  ANY  |  READONLY  
BASE   
  
section  |  key  |  groups   
---|---|---  
para0  
para1  
para2  
para3  
para4  
para5  
para6  
para7  
para8  
para9  
para10  
para11  
para12  
para13  
para14  
para15  
para16  
para17  
para18  
para19  
para20  
para21  
para22  |  calibration types  |  READONLY   
lab 0   
lab 1   
sample 0   
sample 1   
current cal[0]  |  BASE   
current cal[1]   
user cal[0]   
user cal[1]   
factory cal[0]   
factory cal[1]   
interpolation_cutoff   
last_calibration_ts   
required_calibration_interval   
  
##  parameter 

###  write commands 

command  |  required security  |  sensor_types  |  accessible key groups   
---|---|---|---  
**xwparameter** |  NONE  |  ANY  |  BASE   
  
###  read commands 

command  |  required security  |  sensor_types  |  accessible key groups   
---|---|---|---  
**xrparameter** |  NONE  |  ANY  |  BASE  
READONLY   
  
section  |  key  |  groups   
---|---|---  
parameter0  
parameter1  
parameter2  
parameter3  
parameter4  
parameter5  
parameter6  
parameter7  
parameter8  
parameter9  
parameter10  
parameter11  
parameter12  
parameter13  
parameter14  
parameter15  
parameter16  
parameter17  
parameter18  
parameter19  
parameter20  
parameter21  
parameter22  |  pool  |  READONLY   
type   
parameter_source_idx   
script_idx   
name   
n_averages  |  BASE   
n_median   
n_lastgood   
n_ignore_mask   
precision   
output_unit   
  
##  senconf 

###  write commands 

command  |  required security  |  sensor_types  |  accessible key groups   
---|---|---|---  
**pwsenconf** |  SUPERUSER  |  ANY  |  CONFIG  
DENSITY  
CALIB_COEFF  
LIMITS  
MODULE_OPTIONS  
PROD_CONFIG   
**xwdensity** |  NONE  |  SRV  |  DENSITY   
**xwsenconf** |  USER  |  ANY  |  CONFIG  
SN_STR   
**xwsencalib** |  SERVICE  |  ANY  |  CALIB_COEFF   
  
###  read commands 

command  |  required security  |  sensor_types  |  accessible key groups   
---|---|---|---  
**xrsenconf** |  NONE  |  ANY  |  CONFIG  
MODULE_OPTIONS  
PROD_CONFIG  
UUID   
**xrsencalib** |  NONE  |  ANY  |  CALIB_COEFF  
LIMITS   
  
section  |  key  |  groups   
---|---|---  
|  Fair2  |  CONFIG   
Fair1   
Fair0   
Dfair2   
Dfair1   
Dfair0   
fplus_to_fAir_Tol   
densAir_Tol   
viscAir_Tol   
Meas_cr   
Do5  |  CALIB_COEFF  
DENSITY   
Do4   
Do3   
Do2   
Do1   
Do0   
press_coeff  |  CALIB_COEFF   
Dsp_raw_d   
Has_Temp_Sensor   
Meas_Timeout   
Tf   
To   
Clc_r   
Clc_vd   
Clc_d   
Clc_v   
Di5   
Di4   
Di3   
Di2   
Di1   
Di0   
TD4   
TD3   
TD2   
TD1   
TD0   
P4   
P3   
P2   
P1   
P0   
Idiff6   
Idiff5   
Idiff4   
Idiff3   
Idiff2   
Idiff1   
Idiff0   
R4   
R3   
R2   
R1   
Va9   
Va8   
Va7   
Va6   
Va5   
Va4   
Va3   
Va2   
Va1   
Vb9   
Vb8   
Vb7   
Vb6   
Vb5   
Vb4   
Vb3   
Vb2   
Vb1   
Vc9   
Vc8   
Vc7   
Vc6   
Vc5   
Vc4   
Vc3   
Vc2   
Vc1   
V4   
V3   
V2   
V1   
V0   
DC4   
DC3   
DC2   
DC1   
DC0   
dens_comp   
Tc2   
Tc1   
Tc0   
Calib_str   
Sn_H_Vis_mx  |  LIMITS   
Sn_H_Vis_mn   
Sn_H_Den_mn   
Sn_H_Den_mx   
Sn_H_Temp_mn   
Sn_H_Temp_mx   
Sn_H_VisStk_mn   
Sn_H_VisStk_mx   
Sn_H_Pres_mx   
Sn_H_Pres_mn   
Has_AnaOutCh  |  MODULE_OPTIONS   
Has_ModbusRTU   
Has_BLUETOOTH   
Has_ETHERNET   
Has_USB   
Has_HART   
Has_ModbusTCP   
Has_Display   
Has_LED   
Has_SDCard   
Has_Webserver   
Has_Analytics   
Has_CloudConnect   
Has_ENIP   
Has_PNET   
Has_ParameterScripts   
Has_Calibration   
Sn_str  |  PROD_CONFIG  
SN_STR   
Sys_Sn_str  |  PROD_CONFIG   
If_Sn_str   
Sensor_Type   
If_UUID  |  UUID   
  
##  smet_sensor_hw 

###  write commands 

command  |  required security  |  sensor_types  |  accessible key groups   
---|---|---|---  
**xwshwconf** |  SERVICE  |  ANY  |  BASE   
**pwshwconf** |  SUPERUSER  |  ANY  |  BASE  
PROD_CONFIG   
  
###  read commands 

command  |  required security  |  sensor_types  |  accessible key groups   
---|---|---|---  
**xrshwconf** |  NONE  |  ANY  |  BASE  
PROD_CONFIG   
  
section  |  key  |  groups   
---|---|---  
|  Amp_Lg  |  BASE   
Vsn   
E_fup   
E_flw   
Vco_o   
Dph   
Rph_def   
Rph_tol   
No_rph_adj   
Freq   
Phi_f_on   
Df_n_avr   
F_n_avr   
TRf   
TRo   
Is_PT1000   
Esn_str  |  PROD_CONFIG   
Ehw_str 
