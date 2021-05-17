## strYa

## Table of contents
 - [Description](#description)
 - [Getting started](#getting-started)
   - [Prerequisites](#prerequisites)
   - [Installing](#installing)
   - [Usage](#usage)
 - [Team](#team)
 - [License and Copyright](license-and-copyright)

## Usage example (Real data button in upper lower corner of screen) https://str-ya.herokuapp.com/apps/real_life

## Description
**strYa** is a project aimed at helping one to track the quality of his posture. Using two Inertial Measurement Units (IMUs), the system can determine the quality of user's posture. After the system is setup, one may run an visualisation of one of the sensor, based on written dataset (one can pass to_file argument to main), as well as look at the statistics and graphs of the measurements from the files via simple web application written using python dash module

<br>

## Getting started

### Prerequisites
| **Component**                 | **function**                            |
|------------------------------	|---------------------------------------	|
| Arduino Nano MCU    	        | data transfer/processing              	|
| 2x MPU 6050 (GY 521) IMU      | collecting measurements on the posture  |
| HC-05 (ZS-040) BLE module     | Serial data trnasmission via bluetooth low energy |
| 220 ohm, 1K and 2K Resistors                 | to connect the components                        |
| LED                           | indicates that the bad posture (will be rpelaced) |
| Mini-USB Cable               	| power supply                           	|

### Installing
  1. Clone project.
  ```bash
  $ git clone https://github.com/bohdanhlovatskyi/strYa  
  ```
  2. Connect the components in the following way: ![Alt text](wiki/schematic.png?raw=true "Title")
  3. Connect the Arduino microcontroller to your computer via serail port.
  4. Build and run the project.

## Team
| **Bohdan Hlovatskyi** | **Karyna Volokhatiuk** | **Yuriy Sukhorskyy** |

## License and Copyright
This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/).

© 2021 Bohdan Hlovatskyi, Karyna Volokhatiuk
