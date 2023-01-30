""" List of working commands. Just for an overview"""

def SystemMessageCallback(serial, prnt_msg:bool = True, ret_hex_int:int=0):
    """Reads the message buffer of a serial connection. Also prints out the general system message.
    serial      ... serial connection
    prnt_msg    ... print out the buffer
    ret_hex_int ... Parameters -> ['none','hex', 'int', 'both']
    
    """
    msg_dict = {
        "0x01": "No message inside the message buffer",
        "0x02": "Timeout: Communication-timeout (less data than expected)",
        "0x04": "Wake-Up Message: System boot ready",
        "0x11": "TCP-Socket: Valid TCP client-socket connection",
        "0x81": "Not-Acknowledge: Command has not been executed",
        "0x82": "Not-Acknowledge: Command could not be recognized",
        "0x83": "Command-Acknowledge: Command has been executed successfully",
        "0x84": "System-Ready Message: System is operational and ready to receive data",
        "0x91": "Data holdup: Measurement data could not be sent via the master interface",
    }
    timeout_count = 0
    received = []
    received_hex = []
    data_count = 0
    
    while True:
        buffer = serial.read()
        if buffer:
            received.extend(buffer)
            data_count += len(buffer)
            timeout_count = 0
            continue
        timeout_count += 1
        if timeout_count >= 1:
            # Break if we haven't received any data
            break

        received = ''.join(str(received))  # If you need all the data
    received_hex = [hex(receive) for receive in received]
    try:
        msg_idx = received_hex.index('0x18')
        print(msg_dict[received_hex[msg_idx+2]])
    except BaseException:
        print(msg_dict['0x01'])
        prnt_msg = False
    if prnt_msg:
        print("message buffer:\n",received_hex)
        print("message length:\t",data_count)
    
    
    if ret_hex_int=='none':
        return
    elif ret_hex_int=='hex':
        return received_hex
    elif ret_hex_int=='int':
        return received
    elif ret_hex_int=='both':
        return received, received_hex
    
    
def GetFirmwareIDs(serial):
    """Get firmware IDs"""
    serial.write(bytearray([0xD2, 0x00, 0xD2]))
    SystemMessageCallback(serial)

def SoftwareReset(serial):
    serial.write(bytearray([0xA1, 0x00, 0xA1]))
    SystemMessageCallback(serial)