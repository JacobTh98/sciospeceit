try:
    import serial
except ImportError:
    print("Could not import module: serial")


def available_serial_ports():
    print("This function has to be programmed...")


def connect_COM_port(port: str = "COM5", baudrate: int = 9600, timeout: int = 1):
    """Start a serial connection."""
    ser = serial.Serial(
        port=port,
        baudrate=baudrate,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        timeout=timeout,
    )
    ser.flushInput()

    try:
        ser.isOpen()
        print("Serial port is open")
    except:
        print("Error")
        exit()

    if ser.isOpen():
        try:
            while 1:
                print(ser.read())
        except Exception:
            print("error")
    else:
        print("can not open port")
