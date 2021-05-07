- потестити на більших частотах



- постворювати депенденси
- хардова частина: прототип + по трохи щось писати на сам контролер

- функція перекалібрації (якщо з ходу все зле, то юзер дельфін)
- ну й там всяке різне

- даш + візуалізація з текстом: командний проектік з оп

Questions:
- як відслідковували муви


Ideas behind the code:
- we create instances of gyroscopes and accelerometers
- each of them should be not only a container, but rather an
- allocated memoty that will be constantly rewritten
- based on this concept, gyros would contain a buffer
- that will calibrate their bias
- at the same moment, allocated sensor groups woulr
- contain a buffeer that will be used to calculate optimal position
- after the position is calibrated, it will go into posture position
- object (that before this will allocate memory for sensor group)
- then sensor groups within a posture position will be rewritten
- and compared to the oprimal position
- this will make it possible to make the comparisson