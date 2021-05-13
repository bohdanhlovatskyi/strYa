## strYa

## Table of contents
 - [Description](#description)
 - [Getting started](#getting-started)
   - [Prerequisites](#prerequisites)
   - [Installing](#installing)
   - [Usage](#usage)
 - [Team](#team)
 - [License and Copyright](license-and-copyright)

## Description

## Getting started

### Prerequisites
| **Component**                 | **function**                            |
|------------------------------	|---------------------------------------	|
| Arduino Nano MCU    	        | data transfer/processing              	|
| 2x MPU 6050 (GY 521) IMU      | collecting measurements on the posture  |
| Mini-USB Cable               	| power supply                           	|
| LED                           | indicates that the bad posture (will be rpelaced) |
| 220 Resistor                  | to connect LED                          |
| HC-05 (ZS-040) BLE module     | Serial data trnasmission via bluetooth low energy |

### Installing
  1. Clone project.
  ```bash
  $ git clone https://github.com/bohdanhlovatskyi/strYa  
  ```
  1. Connect the components in the following way: ![Alt text](wiki/schematic.png?raw=true "Title")
  2. Connect the Arduino microcontroller to your computer via serail port.
  3. Build and run the project.

### Usage 


## Team
| **Bohdan Hlovatskyi** | **Karyna Volokhatiuk** | **Yuriy Sukhorskyy** |

## License and Copyright
This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/).

© 2021 Bohdan Hlovatskyi, Karyna Volokhatiuk