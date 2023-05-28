import serial
import time

ser = serial.Serial('/dev/ttyS0',9600,timeout = 1)

def waitForModulePower():
    state = 0
    while(state == 0):
        data = ser.read_until(b"\r\n")
        print(data.decode('utf-8'))
        if data == (b'+QIND: PB DONE\r\n'):
            state = 1 
            print("modem-ready")
    return state

def writeCommand(command :str ,response = "OK\r\n", timeout = 2, repeat_count = 1):
    ret = False
    send_command = bytes(command+"\r\n" , 'ascii')
    # ser.write((send_command))
    # end_time = timeout+time.time()
    # print("et>")
    # print(end_time)
    for i in range(repeat_count):
        print("i-"+str(i))
        ser.write((send_command))
        end_time = timeout+time.time()
        while(1):
            # print(time.time())
            received_response = ser.readline() #read from uart

            print("R:"+str(received_response)) #print whats been red

            if(str(received_response.decode('ascii')).find(response) != -1):
                print(command+"'s"+' response ok')
                ret = True
                break

            if(time.time() > end_time):
                ret = False
                break
        if(ret == True):
            break    

    return ret

def sendDAta(data:str):
    new_data = bytes(data+"\r\n" , 'ascii')
    print("data to send > "+data)
    if(writeCommand("AT+QISEND=0",">") == True):
        print("found >")
        ser.write((new_data))
        ser.write(chr(26).encode("ascii"))
        # end_time = time.time()+10
        while(1):
            received_response = ser.readline()
            if(str(received_response.decode('utf-8')).find("SEND OK") != -1):
                # print(command+"'s"+' response ok')
                ret = True
                break
            elif(str(received_response.decode('utf-8')).find("SEND FAIL") != -1):
                # print(command+"'s"+' response ok')
                ret = False
                break
            elif(str(received_response.decode('utf-8')).find("ERROR") != -1):
                # print(command+"'s"+' response ok')
                ret = False
                break



def openTcp(ip:str,port:str):
    ret = False
    tcp_creds = bytes('AT+QIOPEN=1,0,"TCP",{0},{1},0,1\r\n'.format(ip,port),"ascii")
    ser.write(tcp_creds)
    end_time = (time.time()+5)
    while(1):
        received_response = ser.readline()
        print(received_response)
        if(str(received_response.decode('utf-8')).find("+QIOPEN: 0,0") != -1):
            ret = True
            break
        if(str(received_response.decode('utf-8')).find("+QIOPEN: 0,563") != -1):
            ret = False
            break
        if(str(received_response.decode('utf-8')).find("ERROR") != -1):
            ret = False
            break
        if(time.time() > end_time):
            ret = False
            break
    return ret



def setup():
    state = 0
    if(waitForModulePower() == 1):
        while(state != 10):
            if(state == 0):
                if(writeCommand("AT\r\n","OK\r\n")):
                    print("> AT OK")
                    state = 1
                else:
                    state = 0
            if(state == 1):
                if(writeCommand("AT+CPIN?\r\n","+CPIN: READY\r\n")):
                    print("> CPIN OK")
                    state = 2
                # else:
                #     state = state-1        
            if(state == 2):
                if(writeCommand("AT+CMEE=2\r\n")):
                    print("> CMEE=2 OK")
                    state = 4
                # else:
                #     state = state-1        
            if(state == 4):
                if(writeCommand("AT+IPR=9600&W\r\n")):
                    print("> IPR OK")
                    state = 5
                # else:
                #     state = state-1 
            if(state == 5):
                if(writeCommand("AT+CREG?\r\n","+CREG: 0,1\r\n",repeat_count=20)):
                    print("> CREG OK")
                    state = 6
                # else:
                #     state = state-1  
            if(state == 6):
                if(writeCommand("AT+COPS?\r\n","AirTel",repeat_count=5)):
                    print("> COPS OK")
                    state = 7
                # else:
                #     state = state-1
            if(state == 7):
                if(writeCommand("AT+QICSGP=1,1,\"airtelgprs.com\"\r\n",repeat_count=10)):
                    print("> QICSGP OK")
                    state = 8
                # else:
                #     state = state-1
            if(state == 8):
                if(writeCommand("AT+QIACT=1\r\n")):
                    print("> QIACT OK")
                    state = 9
                # else:
                #     state = state-1
            if(state == 9):
                if(writeCommand("AT+CGREG?\r\n","+CGREG: 0,1\r\n",repeat_count=10)):
                    print("> CGREG OK")
                    state = 10
                # else:
                #     state = state-1
    return True
#run

def pdpDeact():
    if(writeCommand("AT+QIDEACT=1")):
        return 1
    else:
        return 0

def closeIp():
    if(writeCommand("AT+QICLOSE=0")):
        return 1
    else:
        return 0

    

if(setup()):
    if(openTcp("34.73.143.220","10235")):
        print("device online")
        time.sleep(15) #wait for 10 seconds
        print("sending")
        sendDAta("HI THIS IS FROM CORAL")
        print("sent")
        closeIp()
        if(openTcp("34.73.143.220","10235")):
            print("device online")
            time.sleep(15) #wait for 10 seconds
            print("sending")
            sendDAta("HI THIS IS FROM CORAL AGAIN")

    pass