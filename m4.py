import ssl
import getpass
import json
from unicodedata import name
from pyVmomi import vim
from pyVim.connect import SmartConnect, vim


# The function below (get_all_objs) was taken from:
# https://vthinkbeyondvm.com/pyvmomi-tutorial-how-to-get-all-the-core-vcenter-server-inventory-objects-and-play-around/
# This makes it easier to grab the objects that make up the server inventory.
def get_all_objs(content, vimtype):
    obj = {}
    container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
    for managed_object_ref in container.view:
        obj.update({managed_object_ref:managed_object_ref.name})
    return obj

# This function presents the user some choices in which they can use to implement the functions. 


def main_menu(vm_content, vcent):

    choice = 0
    while choice == 0:
        print("[1] Login Info")
        print("[2] List VMs by Name")
        print("[3] Print AboutInfo")
        print("[4] Quit the program")
        userChoice = input("Choose an option: ")
        if userChoice == "0":
            print("0 is not a valid option, please choose one of the listed options")
        elif userChoice == "1":
            s = vm_content.sessionManager.currentSession
            print("You have selected the Login Info option.")
            print("Information from current session: ")
            print("Your username is: " + s.userName)
            print("Your IP Address is: " + s.ipAddress)
            print("Your vCenter Server is: " + vcent)
        elif userChoice == "2":
            print("You have chosen the List VMs by Name option.")
            search = input("Please enter a filter (Leave blank to print all VMs): ")
            scan = [vm for vm in get_all_objs(content, [vim.VirtualMachine])]
            vms = host_info(scan, search)
            parse_the_vms = vmParse(vms)
            print(parse_the_vms)

        elif userChoice == "3":
            print("You have chosen to display the AboutInfo option.")
            print(vm_content.about)
            print("Your content version number is: " + content.about.version)
        elif userChoice == "4":
            print("You have chosen to terminate the program.")
            print("Exiting program...")
            break

# For this one, I looked over https://github.com/vmware/pyvmomi-community-samples/blob/master/samples/vminfo_quick.py
def vmParse(vmac):
    for virtual in vmac:
            print("---" * 5)
            print("Name of Virtual Machine: {0}".format(virtual["vm_name"]))
            print("IP Address: {0}".format(virtual["ip_address"]))
            print("Power State: {0}".format(virtual["power_state"]))
            print("Total RAM:  {0}".format(virtual["memory"]) + " GB")
            print("Number of CPUs: {0}".format(virtual["cpu_count"]))
            print("---" * 5)

# This was slightly adapted from https://github.com/vmware/pyvmomi-community-samples/blob/master/samples/getallvms.py
# Only had to change to make the filter work correctly, as well as have it iterate through the list a bit differently.

def host_info(vm, search):

    vm_information = []
    print("The search filter you chose is: " + search)
    for virtual in vm:
        vm_name = virtual.name
        if search in vm_name:
            host_summary = vars(virtual.summary)
            host = {}
            host["vm_name"] = virtual.name
            host["ip_address"] = host_summary["guest"].ipAddress
            host["power_state"] = host_summary["runtime"].powerState
            host["memory"] = int(host_summary["config"].memorySizeMB / 1024)
            host["cpu_count"] = host_summary["config"].numCpu
            vm_information.append(host)
    return vm_information


# This was adapted from our intial lines of code in class from your (logging in), the only thing that is more-or-less added was
# opening it with a creds file (rather than hardcoding it in like we did previously). 
def user_login():
    with open('/home/champuser/SYS350/automation/SYS350/info.json')  as credfile:
        object = json.load(credfile)
        passw = getpass.getpass()
        s=ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        s.verify_mode=ssl.CERT_NONE
        si = SmartConnect(host=object["vcenter_host"], user=object["username"], pwd=passw, sslContext=s)
        vmInfo = si.content
        return vmInfo, object["vcenter_host"]


if __name__ == "__main__":
    info = user_login()
    content = info[0]
    vcenter_name = info[1]
    main_menu(content, vcenter_name)