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

def parse(virtmach_list):
    for vmac in virtmach_list:
        if vmac != None:
            print("----------")
            print("Name of Virtual Machine: " + vmac["vm_name"])
            print("IP Address: " + str(vmac["ip_address"]))
            print("Power State: " + vmac["power_state"])
            print("RAM: " + str(vmac["memory"]) + " GB")
            print("CPU Count: " + str(vmac["cpu_count"]))

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
            vm_scan = [vm for vm in get_all_objs(content, [vim.VirtualMachine])]
            vms = host_info(vm_scan, filt)
            vms_parse = parse(vms)
            print(vms_parse)

        elif answer == "3":
            print("You have chosen to display the AboutInfo option.")
            print(content.about)
            print("Your content version number is: " + content.about.version)
        elif answer == "4":
            print("You have chosen to terminate the program.")
            print("Exiting program...")
            break

# This was slightly adapted from https://github.com/vmware/pyvmomi-community-samples/blob/master/samples/getallvms.py
# Only had to change to make the filter work correctly, as well as have it iterate through the list a bit differently.
def host_info(vms, filt):
    vm_info = []
    print("The chosen filter is: " + filt)
    for virtual_machine in vms:
        virtual_machine_name = virtual_machine.name
        if filt in virtual_machine_name:
            vcenter_summary = vars(virtual_machine.summary)
            v_host = {}
            v_host["vm_name"] = virtual_machine.name
            v_host["ip_address"] = vcenter_summary["guest"].ipAddress
            v_host["power_state"] = vcenter_summary["runtime"].powerState
            v_host["memory"] = int(vcenter_summary["config"].memorySizeMB / 1024)
            v_host["cpu_count"] = vcenter_summary["config"].numCpu
            vm_info.append(v_host)
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
    vmInfo = info[0]
    vcenter_name = info[1]
    main(vmInfo, vcenter_name)