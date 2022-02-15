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

# For this one, I looked over https://github.com/vmware/pyvmomi-community-samples/blob/master/samples/vminfo_quick.py

def main(content, vcenter):

    choice = 0
    while choice == 0:
        print("[1] Login Info")
        print("[2] List VMs by Name")
        print("[3] Print AboutInfo")
        print("[4] Quit the program")
        answer = input("Choose an option: ")
        if answer == "0":
            print("0 is not a valid option, please choose one of the listed options")
        elif answer == "1":
            session = content.sessionManager.currentSession
            print("You have selected the Login Info option.")
            print("Information from current session: ")
            print("Your username is: " + session.userName)
            print("Your IP Address is: " + session.ipAddress)
            print("Your vCenter Server is: " + vcenter)
        elif answer == "2":
            print("You have chosen the List VMs by Name option.")
            filt = input("Please enter a filter (Leave blank to print all VMs): ")
            scan = [vm for vm in get_all_objs(content, [vim.VirtualMachine])]
            vms = host_info(scan, filt)
            vms_parse = parsing_info(vms)
            print(vms_parse)

        elif answer == "3":
            print("You have chosen to display the AboutInfo option.")
            print(content.about)
            print("Your content version number is: " + content.about.version)
        elif answer == "4":
            print("You have chosen to terminate the program.")
            print("Exiting program...")
            break

# For this one, I looked over https://github.com/vmware/pyvmomi-community-samples/blob/master/samples/vminfo_quick.py
def parsing_info(vmac):
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
    vm_info = []
    print("The chosen filter is: " + search)
    for virtual_machine in vm:
        virtual_machine_name = virtual_machine.name
        if search in virtual_machine_name:
            
            summary = vars(virtual_machine.summary)
            vm_name = virtual_machine.name
            ip_address = summary.guest.ipAddress
            power_state = summary.runtime.powerState
            memory = int(summary.config.memorySizeMB / 1024)
            cpu_count = summary.config.numCpu
    return vm_info

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
    Info = info[0]
    vcenter_name = info[1]
    main(Info, vcenter_name)