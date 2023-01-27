""" List of working commands. Just for an overview"""

def GeneralSystemMessages(serial, msg_old:list = []): # Why returns this function none?!?!?!
    """Reads the message buffer of a serial connection. Also prints out the general system message."""
    msg_dict = {
        b"\x02": "Timeout: Communication-timeout (less data than expected)",
        b"\x04": "Wake-Up Message: System boot ready",
        b"\x11": "TCP-Socket: Valid TCP client-socket connection",
        b"\x81": "Not-Acknowledge: Command has not been executed",
        b"\x82": "Not-Acknowledge: Command could not be recognized",
        b"\x83": "Command-Acknowledge: Command has been executed successfully",
        b"\x84": "System-Ready Message: System is operational and ready to receive data",
        b"\x91": "Data holdup: Measurement data could not be sent via the master interface",
    }
    msg_new = []
   
    start_cmd_tag = serial.read() # Read start tag.
    cmd_msg_len = int.from_bytes(serial.read(), "big") # Read length of the message.
    if msg_old: # msg_old has elements:
        msg_new.append(start_cmd_tag)
        msg_new = [serial.read() for i in range(cmd_msg_len)]
        end_cmd_tag = serial.read()# Read message end tag.
        msg_new.append(end_cmd_tag)
        msg_old.append(msg_new) # Reads the serial message in Hex and adds to msg_old
    else:
        msg_new.append(start_cmd_tag)
        msg_new = [serial.read() for i in range(cmd_msg_len)] # Reads the serial message in Hex.  
        end_cmd_tag = serial.read()# Read message end tag.
        msg_new.append(end_cmd_tag)
        msg_old = msg_new
    #msg_new = [int.from_bytes(m, "big") for m in msg_new] # Convert message to integer.
    #if start_cmd_tag == end_cmd_tag: # Concludes with the comparison of start and end tag   
    #print("start tag:",start_cmd_tag)
    #print("msg_new len:",cmd_msg_len)
    #print("end tag:",end_cmd_tag)

    if end_cmd_tag != b'\x18':
        print("Recall GeneralSystemMessages(serial, msg_new)\n")
        GeneralSystemMessages(serial, msg_new)
    if end_cmd_tag == b'\x18':
        print(msg_dict[msg_new[0]])
        print("msg_new:",msg_new)
        print("msg_old:",msg_old)
        return msg_old
    
    
def GetFirmwareIDs(serial) -> None:
    """Get firmware IDs"""
    serial.write(bytearray([0xD2, 0x00, 0xD2]))
    callback = GeneralSystemMessages(serial)
    print(callback)

def SoftwareReset(serial) -> None:
    serial.write(bytearray([0xA1, 0x00, 0xA1]))
    callback = GeneralSystemMessages(serial)
    print(callback)