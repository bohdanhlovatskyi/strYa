## strYa

## TODO
- винести аналіз дейти в інший клас
- потестити на більших частотах
- постворювати депенденси
- візуалізація в блокнотах
- !!!!!!!!! написати рідмі )))
- написати тести :=(

!!! Загалом кажучи, то коду для прототипу досить - попідкручувати основну логіку
та й досить - в майбутньому можна прописати хороше логування, але це варто робити
вже після аналізу наявних датасетів, що дозволить зрозуміти, що саме в ті логи включати
і як дібратись до тої інфи

Дуже в майбутньому :=) 
- хардова частина: прототип + по трохи щось писати на сам контролер

## Table of contents
 - [TODO](#todo)
 - [Getting started](#getting-started)
   - [Prerequisites](#prerequisites)
   - [Installing](#installing)
   - [Usage](#usage)
 - [Team](#team)
 - [License and Copyright](license-and-copyright)

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
  2. Connect the components in the following way: <img src="scheme.png" alt="connection scheme" width=600>
  3. Connect the Arduino microcontroller to your computer via serail port.
  4. Build and run the project.

### Usage 


## Team
| **Bohdan Hlovatskyi** | **Kayna Volokhatiuk** | **Yuriy Sukhorskyy** |

## License and Copyright
