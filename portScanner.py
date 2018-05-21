import argparse
import nmap
import json, os
import datetime
import ipaddress
from colorama import Style, Fore
import re

# -----------------------------------------------------#
ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
END = '\033[0m'

additional_options = ' -sV'

with open('Options.conf') as f:
    data = json.load(f)

inModule = False
allModules = []
modules = []
email = Fore.RED + "tinyb0y@protonmail.com"

header = """
 _____ _             _      ___
|_   _(_)_ __  _   _| |__  / _ \ _   _
  | | | | '_ \| | | | '_ \| | | | | | |
  | | | | | | | |_| | |_) | |_| | |_| |
  |_| |_|_| |_|\__, |_.__/ \___/ \__, |
               |___/             |___/
""" + "\t\t" + email


# -----------------------------------------------------#

for item in data:
    allModules.append([item['option'], item['help']])
    modules.append(item['option'])


def helpPrint(name, desc, usage):
    print("\t" + Fore.YELLOW + name + Fore.GREEN + ": " + Fore.BLUE + desc + Fore.GREEN + " - '" + usage + "'" + END)


def commands():
    print(Fore.GREEN + "\n[I] Available commands:\n" + END)
    helpPrint("MODULES", "List all modules", "modules")
    helpPrint("USE", "Use a module", "use module_name")
    helpPrint("OPTIONS", "Show a module's options", "options")
    helpPrint("SET", "Set an option", "set option_name option_value")
    helpPrint("RUN", "Run the selected module", "run")
    helpPrint("FULL SCAN", "Scan the whole network", "fullscan")
    helpPrint("BACK", "Go back to menu", "back")
    helpPrint("EXIT", "Shut down portSpider", "exit")
    print()


def checkCommandAvailable(module):
    if module in modules:
        return True
    else:
        return False


def logFileCreation():
    script_path = os.path.dirname(os.path.realpath(__file__))
    if not os.path.exists(script_path + "/logs"):
        os.makedirs(script_path + "/logs")
    dt = datetime.datetime.now()
    dt = str(dt).replace(" ", "_")
    dt = str(dt).replace(":", "-")
    fileName = script_path + "/logs/tinyb0y-ScanReport" + dt + ".log"
    print(fileName)
    file = open(fileName, 'w')
    file.write("Scan Report using Tinyb0y PortScanner " + str(dt))
    file.close()
    return fileName


def writeScanEvents(fileName, eventScan):
    file = open(fileName, "a")
    file.write(eventScan)
    file.close()


def getModuleOptions(module):
    commands_for_current_module = []
    if inModule:
        for item in data:
            if item['option'] == module:
                for key in item['commands'].keys():
                    if '->' in item['commands'][key]:
                        value = item['commands'][key].split('->')[1].strip()
                        description = item['commands'][key].split('->')[0]
                    else:
                        value = ''
                        description = item['commands'][key]
                    commands_for_current_module.append([key, description, value])
                return commands_for_current_module


def getOptionValue(option):
    for item in moduleOptions:
        if item[0] == option:
            return item[2]


def createIPList(network):
    net4 = ipaddress.ip_network(network)
    ipList = []
    for x in net4.hosts():
        ipList.append(str(x))
    return ipList


def createIPListRange(networkRange):
    end = int(networkRange.split('-')[1])
    ipaddressSplit = networkRange.split('-')[0].split('.')
    start = int(ipaddressSplit[3])
    IPList = []
    for num in range(start, end):
        IPList.append(ipaddressSplit[0] + '.' + ipaddressSplit[1] + '.' + ipaddressSplit[2] + '.' + str(num))
    return IPList


def getIPlist(ipvar):
    if '/' in ipvar:
        if len(ipvar.split('/')) > 1:
            return createIPList(ipvar)
        else:
            print(Fore.RED + "[!] Invalid IP subnet")
    elif '-' in ipvar:
        if len(ipvar.split('-')) > 1:
            return createIPListRange(ipvar)
        else:
            print(Fore.RED + "[!] Invalid IP Range")
    elif ',' in ipvar:
        if len(ipvar.split(',')) > 1:
            return list(filter(None, ipvar.split(',')))
    else:
        return [ipvar]


def scan(IP, options):
    fileName = logFileCreation()
    IPList = getIPlist(IP)
    for ip in IPList:
        if 'p' in options:
            nm = nmap.PortScanner()
            nm.scan(ip, arguments=options + additional_options)
            # print(nm.command_line())
        else:
            nm = nmap.PortScanner()
            nm.scan(ip, options, arguments=additional_options)
            # print(nm.command_line())
        try:
            if nm[ip].all_protocols():
                PrintOnScreen(ip, nm, fileName)
        except:
            pass
    print("Logs are saved in " + fileName)


def scan_from_file(options):
    fileName = logFileCreation()
    IPListFromFile = getListfromFile(getOptionValue('filename'))
    for IP in IPListFromFile:
        IPList =  getIPlist(IP)
        for ip in IPList:
            print(ip)
            if 'p' in options:
                nm = nmap.PortScanner()
                nm.scan(ip, arguments=options + additional_options)
            else:
                nm = nmap.PortScanner()
                nm.scan(ip, options, arguments=additional_options)
            try:
                if nm[ip].all_protocols():
                    PrintOnScreen(ip, nm, fileName)
            except:
                pass
    print("Logs are saved in " + fileName)


def getListfromFile(filename):
    iplist = open(filename).read().split()
    return iplist


def PrintOnScreen(host, nm, fileName):
    if getOptionValue('verbose') == 'true':
        finalStr = '\n'
        finalStr += '-' * 50 + '\n'
        finalStr += "| " + Fore.GREEN + str(host) + " |" + '\n'
        finalStr += '-' * 50 + '\n'
        hostname = Fore.YELLOW + "-unknown-" + '\n'
        if nm[host].hostname() != "":
            hostname = nm[host].hostname()

        finalStr += " " * (
            (len(host) + 4)) + "|_ " + Fore.GREEN + Style.DIM + "Hostname" + Style.RESET_ALL + " : %s" % (
        hostname) + '\n'

        if nm[host].all_protocols():
            finalStr += " " * (len(host) + 4) + "|_ " + Fore.GREEN + Style.DIM + "Ports" + Style.RESET_ALL + '\n'
            for proto in nm[host].all_protocols():

                ports = list(nm[host][proto].keys())
                ports.sort()
                finalStr += " " * ((len(
                    host) + 4)) + "|" + '\t' + "[" + Fore.GREEN + Style.DIM + "+" + Style.RESET_ALL + '] Protocol : %s' % proto + '\n'
                finalStr += " " * (len(host) + 4) + "|" + '\t\tPort\t\tState\t\tServiceVersion' + '\n'
                finalStr += " " * (len(host) + 4) + "|" + '\t\t====\t\t=====\t\t==============' + '\n'
                for port in ports:
                    VersionString = nm[host][proto][port]['product'] + " " + nm[host][proto][port][
                        'version'] + " ExtraInfo: " + nm[host][proto][port]['extrainfo'] + " " + nm[host][proto][port][
                                        'cpe']
                    finalStr += " " * (len(host) + 4) + "|" + '\t\t%s\t\t%s\t\t%s' % (
                    port, nm[host][proto][port]['state'], VersionString) + '\n'
        else:
            finalStr += " " * ((len(
                host) + 4)) + "|_ " + Fore.GREEN + Style.DIM + "Ports" + Style.RESET_ALL + " : %s" % (
                (Fore.YELLOW + "-none-")) + '\n'

        finalStr += " " * (
            (len(host) + 4)) + "|_ " + Fore.GREEN + Style.DIM + "OS fingerprinting" + Style.RESET_ALL + '\n'

        if 'osclass' in nm[host]:
            for osclass in nm[host]['osclass']:
                finalStr += '\t\t' + "[" + Fore.GREEN + Style.DIM + "+" + Style.RESET_ALL + "] Type : {0}".format(
                    osclass['type']) + '\n'
                finalStr += '\t\t    Vendor : {0}'.format(osclass['vendor']) + '\n'
                finalStr += '\t\t    OS-Family : {0}'.format(osclass['osfamily']) + '\n'
                finalStr += '\t\t    OS-Gen : {0}'.format(osclass['osgen']) + '\n'
                finalStr += '\t\t    Accuracy : {0}%'.format(osclass['accuracy']) + '\n'

        elif 'osmatch' in nm[host]:
            for osmatch in nm[host]['osmatch']:
                finalStr += '\t\t' + "[" + Fore.GREEN + Style.DIM + "+" + Style.RESET_ALL + "] Name : {0} (accuracy {1}%)".format(
                    osmatch['name'], osmatch['accuracy']) + '\n'

        elif 'fingerprint' in nm[host]:
            finalStr += '\t\t* Fingerprint : {0}'.format(nm[host]['fingerprint']) + '\n'

        print(finalStr)
        finalStr = ansi_escape.sub('', finalStr)
        writeScanEvents(fileName, finalStr)
        return True


def commandHandler(command):
    command = str(command)

    global inModule
    global currentModule
    global moduleOptions
    global currentModuleFile

    # HELP

    # commands
    if command == "help":
        commands()

    if command == "use":
        print(Fore.RED + "[!] Usage: 'use " + Fore.YELLOW + "module_name" + Fore.RED + "'" + END)

    # USE

    elif command.startswith("use "):
        command = command.replace("use ", "")
        if checkCommandAvailable(command):
            inModule = True
            currentModule = command
            moduleOptions = getModuleOptions(currentModule)
        else:
            print(Fore.RED + "[!] Module '" + Fore.YELLOW + command + Fore.RED + "' not found." + END)

    # OPTIONS
    elif command == "options":
        if inModule:
            print(Fore.GREEN + "\n Options for module '" + Fore.YELLOW + currentModule + Fore.GREEN + "':" + END)
            for option in moduleOptions:
                if option[2] == "":
                    print("\t" + Fore.YELLOW + option[0] + Fore.GREEN + " - " + Fore.BLUE + option[
                        1] + Fore.GREEN + " ==> " + Fore.RED + "[NOT SET]" + END)
                else:
                    print("\t" + Fore.YELLOW + option[0] + Fore.GREEN + " - " + Fore.BLUE + option[
                        1] + Fore.GREEN + " ==> '" + Fore.YELLOW +
                          option[2] + Fore.GREEN + "'" + END)
            print()
        else:
            print(Fore.RED + "[!] No module selected." + END)

    # SET
    elif command.startswith("set "):
        if inModule:
            command = command.replace("set ", "")
            command = command.split()
            error = False
            try:
                test = command[0]
                test = command[1]
            except:
                print(Fore.RED + "[!] Usage: 'set " + Fore.YELLOW + "option_name option_value" + Fore.RED + "'" + END)
                error = True
            if not error:
                inOptions = False
                for option in moduleOptions:
                    if option[0] == command[0]:
                        inOptions = True
                        option[2] = command[1]
                        print(Fore.YELLOW + option[0] + Fore.GREEN + " ==> '" + Fore.YELLOW + command[
                            1] + Fore.GREEN + "'" + END)
                if not inOptions:
                    print(Fore.RED + "[!] Option '" + Fore.YELLOW + command[0] + Fore.RED + "' not found." + END)
        else:
            print(Fore.RED + "[!] No module selected." + END)
    elif command == "set":
        print(Fore.RED + "[!] Usage: 'set " + Fore.YELLOW + "option_name option_value" + Fore.RED + "'" + END)

    elif command == "run":
        if inModule:
            ipFileName = getOptionValue('filename')
            if ipFileName == '':
                if currentModule == 'fullscan':
                    IP = getOptionValue('network')
                    args = '-Pn -p-'
                    if IP != '':
                        scan(IP, args)
                    else:
                        print(Fore.RED + "[!]" + " set network " + END)
                else:
                    IP = getOptionValue('network')  # pull network element
                    args = getOptionValue('port')  # pull port element
                    if IP != '':
                        scan(IP, args)
                    else:
                        print(Fore.RED + "[!] " + "set  network " + END)
            else:
                if currentModule == 'fullscan':
                    args = '-Pn -p-'
                    scan_from_file(args)
                else:
                    args = getOptionValue('port')  # pull port element
                    scan_from_file(args)

        else:
            print(Fore.RED + "[!] No module selected." + END)

    # BACK
    elif command == "back":
        if inModule:
            inModule = False
            currentModule = ""
            moduleOptions = []
    # EXIT
    elif command == "exit":
        print(Fore.GREEN + "[I] Shutting down..." + END)
        raise SystemExit

    # MODULES
    elif command == "modules":
        print(Fore.GREEN + "\nAvailable modules:" + END)
        for module in allModules:
            print(Fore.YELLOW + "\t" + module[0] + Fore.GREEN + " - " + Fore.BLUE + module[1] + END)
        print()

    # CLEAR
    elif command == "clear" or command == "cls":
        os.system("clear||cls")
        print(Fore.RED + header + END)

    # DEBUG
    elif command == "debug":
        try:
            print("inModule: " + str(inModule))
            print(currentModule)
            print(moduleOptions)
        except:
            pass

    elif command == "":
        pass

    else:
        print(Fore.RED + "[!] Unknown command: '" + Fore.YELLOW + command + Fore.RED
              + "'. Type '" + Fore.YELLOW + "help" + Fore.RED + "' for all available commands." + END)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="portSpider")
    parser.add_argument("--test", action='store_true')
    args, leftovers = parser.parse_known_args()

    if args.test:
        print("Test build detected. Exiting...")
        exit()
    print(Fore.GREEN + header + END + Style.RESET_ALL)

    while True:

        if inModule:
            inputHeader = Fore.BLUE + "tinyb0y" + Fore.RED + "/" + currentModule + Fore.BLUE + " $> " + END
        else:
            inputHeader = Fore.BLUE + "tinyb0y $> " + END

        try:
            commandHandler(input(inputHeader))
        except KeyboardInterrupt:
            print(Fore.GREEN + "\n[I] Shutting down..." + END)
            raise SystemExit
        except Exception as e:
            print(Fore.RED  + "\n[!] portSpider crashed...\n[!] Debug info: \n")
            print("\n" + END)
            exit()