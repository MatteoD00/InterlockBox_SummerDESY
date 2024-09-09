# DESY ATLAS - Interlock Box system
This project has been developed during the [DESY Summer Student Programme 2024](https://summerstudents.desy.de/).
It contains the core implementations for the interlock system of the coldbox used during petal testing carried out at DESY for the ATLAS ITk Strip End-Cap upgrade.
The system is based on a [Arduino MKR 1010 WiFi](https://store.arduino.cc/products/arduino-mkr-wifi-1010?gad_source=1&gclid=CjwKCAjwufq2BhAmEiwAnZqw8iXjAt4RWqqJGL7zI3tP4rbXPJu4RwE8WYN8DDa7gnnDwo2Ng7A8BxoCW3YQAvD_BwE) connected to a custom board (Sentuino) designed by IFIC in Valencia.
The main goal of this board is to read different (analog/digital) signals from sensors inside the coldbox and on the petal with the possibility to shutdown the setup in case of any detected issue.
Final goal is to implement a real-time web-based dashboard (via [Grafana](https://grafana.com/)) to have remote access to the status of the different components.
The code provided is composed by a Arduino script (for collecting raw data and basic manipulation) beside a Python script to stream data to the dashboard using an external PC connected via serial port.
