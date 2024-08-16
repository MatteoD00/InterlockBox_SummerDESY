# DESY ATLAS - Interlock Box system
This Arduino script has been developed for the interlock and safety system of the coldbox used for the testing of petals during the System test carried out at DESY for the ATLAS ITk upgrade.
The system is based on a Arduino MKR 1010 WiFi connected to a custom board (Sentuino) designed by IFIC in Valencia.
Main goal of this board is to read different signals from sensors inside the coldbox and on the petal with the possibility to shutdown the setup in case of any unwanted parameter.
Final goal is to implement a real-time web-based dashboard (Grafana) to have remote access to the status of the different components.
