# msfs2fltplango
 Connects Microsoft Flight Simulator 2020 (MSFS 2020) to the mobile FltPlan Go app. This tool allows you to specify the IP address of your mobile device running FltPlan Go, and is primarily for users who cannot run MSFS and FltPlan Go on the same local network.

## Install
1) Install the latest version of [Python 3](https://www.python.org/downloads/).
2) From a command-line, run `pip install SimConnect`.
3) Download [this respository](https://github.com/musurca/msfs2fltplango/archive/master.zip) and unzip to a directory of your choice, e.g. `C:\fltplan`

## How to Use
1) Run Microsoft Flight Simulator.
2) From a command-line, switch to the directory into which you installed this repository.
3) Run `connect [ip_address]` using the IP address of your mobile device running FltPlan Go. For example:
```
connect 10.20.223.11
```
4) In FltPlan Go, go to the External menu and select "X-Plane" from the Simulators category. After a few seconds, the Status should turn green and read "Connected."
5) Done! (If you don't see your plane on the map, make sure you've turned on "Enable Ship Position" in the FltPlan Go settings.)

## Dependencies
* [Python 3](https://www.python.org/downloads/)
* [python-simconnect](https://github.com/odwdinc/Python-SimConnect)
