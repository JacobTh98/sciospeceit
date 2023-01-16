# This sadly doesn´t work

from connect import connect_COM_port
from time import sleep

ser = connect_COM_port()

print(f"Connected to:{ser.name}")

config = [
    b"B0 01 01 B0",
    b"B0 03 02 00 0A B0",
    b"B0 09 05 3F 50 62 4D D2 F1 A9 FC B0",
    b"B0 02 0D 02 B0",
    b"B0 03 09 01 00 B0",
    b"B0 03 08 02 01 B0",
    b"B0 02 0C 01 B0",
    b"B0 05 03 3F 80 00 00 B0",
    b"B0 0C 04 47 C3 50 00 47 C3 50 00 00 01 00 B0",
    b"B0 03 06 01 02 B0",
    b"B0 03 06 02 03 B0",
    b"B0 03 06 03 04 B0",
    b"B0 03 06 04 05 B0",
    b"B0 03 06 05 06 B0",
    b"B0 03 06 06 07 B0",
    b"B0 03 06 07 08 B0",
    b"B0 03 06 08 09 B0",
    b"B0 03 06 09 0A B0",
    b"B0 03 06 0A 0B B0",
    b"B0 03 06 0B 0C B0",
    b"B0 03 06 0C 0D B0",
    b"B0 03 06 0D 0E B0",
    b"B0 03 06 0E 0F B0",
    b"B0 03 06 0F 10 B0",
    b"B0 03 06 10 01 B0",
    b"B1 01 03 B1",
    b"B2 02 01 01 B2",
    b"B2 02 03 01 B2",
    b"B2 02 02 01 B2",
    b"B4 01 01 B4",
]

for cnf in config:
    print(cnf)
    ser.write(cnf)

sleep(11)
ser.write(b"B0 01 00 B4")
print("fertig")
