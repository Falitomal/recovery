import argparse
import datetime
import winreg
import psutil
import os
import winapps
from browser_history.browsers import Chrome, Firefox, Edge
import logging
import wmi
import win32com.client
import win32evtlog
import tkinter as tk
import tkinter.ttk as ttk


def parse_arg():
    """
    Read arguments, start and end date
    """
    parse_arg = argparse.ArgumentParser(description="Program to get info from the windows system",
                                        epilog="By Jledesma")
    parse_arg.add_argument("-s", "--start", help="Start date in format dd/mm/aaaa")
    parse_arg.add_argument("-e", "--end", help="End date in format dd/mm/aaaa")

    parsers = parse_arg.parse_args()
    return parsers.start, parsers.end

def parse_date(date_init, date_end):
    """"
    Check the dates that are correct, or start them on dates, if they are not correct
    return: correct dates or default dates
    """
    try:
        if date_init and not date_end:
            date_end = datetime.datetime.now()
            date_init = datetime.datetime.strptime(date_init, "%d/%m/%Y")
        elif date_end and not date_init:
            date_init = datetime.datetime.strptime("01/01/1970", "%d/%m/%Y")
            date_end = datetime.datetime.strptime(date_end, "%d/%m/%Y")
        elif not date_init and not date_end:
            date_end = datetime.datetime.now()
            # only 30 days
            date_init = date_end - datetime.timedelta(days=30)
        else:
            # both dates are correct
            date_init = datetime.datetime.strptime(date_init, "%d/%m/%Y")
            date_end = datetime.datetime.strptime(date_end, "%d/%m/%Y")
            if date_init > date_end:
                print("The start date is greater than the end date, the default dates are set.")
                date_end = datetime.datetime.now()
                date_init = date_end - datetime.timedelta(days=30)
    except Exception as e:
        print("Error in the dates, the default dates are set.")
        date_end = datetime.datetime.now()
        date_init = date_end - datetime.timedelta(days=30)
    return date_init, date_end

def list_directory(directory, ext):
    """
    List directory files
    return: list of files
    """
    fileslist = []
    for route in directory:
        for root, directory, files in os.walk(route):
            for file in files:
                if file.endswith(ext):
                    fileslist.append(os.path.join(root, file))
    return fileslist

def recent_files(date_init, date_end):
    """ 
    Recent files in windows directory in a date range
    return: list of recent files
    """
    files = set()
    directory = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Roaming', 'Microsoft', 'Windows', 'Recent')
    shell = win32com.client.Dispatch("WScript.Shell")
    link_count = 0

    for file in os.listdir(directory):
        if file.endswith('.lnk'):
            link_count += 1
            try:
                path = os.path.join(directory, file)
                route = shell.CreateShortCut(path).targetpath
                if os.path.isfile(route):
                    date = datetime.datetime.fromtimestamp(os.path.getctime(path))
                    if date_init <= date <= date_end:
                        files.add((date, route))
            except Exception as e:
                print(f"Error while processing file {file}: {e}")
    print(f"\nTotal links in recent files: {link_count}")
    return files

def temp_files(date_init, date_end):
    """
    Gets temporary files in a date range
    return: list of temp files
    """
    files = set()
    path_directory = os.environ["USERPROFILE"] + "\\AppData\\Local\\Temp"
    try:
        for file in os.listdir(path_directory):
            file_path = os.path.join(path_directory, file)
            file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
            if date_init <= file_time <= date_end:
                files.add((file_time,file_path))
    except Exception as e:
        print("Error: ", e)
        pass
    return files

def register_changes(date_init, date_end):
    """
    Gets dates on which records were changed
    :return: set of tuples (date, key) on which the log was changed.
    """
    changes = set()
    key_types = [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]

    for key in key_types:
        try:
            handle = winreg.OpenKey(key, "Software")
            timestamp = winreg.QueryInfoKey(handle)[2] / 10000000 - 11644473600
            date = datetime.datetime.fromtimestamp(timestamp)
            if date_init <= date <= date_end:
                changes.add((date, key))

        except Exception as e:
            print(f"Error while processing key {key}: {e}")
        finally:
            winreg.CloseKey(handle)
    return changes

def navigation_history(date_init, date_end):
    """
    Obtain navigation history in a date range
    return: lista de historial navegacion
    """
    logging.disable(logging.CRITICAL)
    navigation_history = set()
    browsers = [Chrome(), Firefox(), Edge()]

    for browser in browsers:
        try:
            histories = browser.fetch_history().histories
            for entry in histories:
                date, url = entry
                date = date.replace(tzinfo=None)
                if date_init <= date <= date_end:
                    navigation_history.add((browser.name, date, url))
        except Exception as e:
            print(f"Error while fetching {browser.name} browser history: {e}")
            pass
    return navigation_history

def list_opens_program():
    """
    Get open programs
    return: list of open programs
    """
    list_open_programs = []
    for process in psutil.process_iter():
            try:
                if process.name() not in list_open_programs:
                    list_open_programs.append(process.name())
            except Exception as e:
                print("Error: ", e)
                pass
    return list_open_programs

def installed_programs(date_init, dadate_initte_end):
    """
    Get installed programs
    return: list of installed programs
    """
    wconection = wmi.WMI() 
    app_list = set(app.Name for app in wconection.Win32_Product())
    applications = set()
    for app in winapps.list_installed():
        try:
            name = app.name
            date = app.install_date
            route = app.uninstall_string
            if not date and route:
                if route[0] == route[-1] == "\"":
                    route = route[1:-1]
                date = datetime.datetime.fromtimestamp(os.path.getctime(route))
            if date is not None and date_init.date() <= date <= dadate_initte_end.date():
                applications.add((date, name))
                app_list.remove(name)
        except:
            pass
    return applications, app_list

def connected_media():
    """
    Gets physical connected removable media
    return: list of removable media
    """
    removable_media = set()
    connection = wmi.WMI()
    if not connection.Win32_PhysicalMedia():
        print("No physical devices found.")
    else:
        for device in connection.Win32_PhysicalMedia():
            if device.Name is not None:
                removable_media.add(device.Name)

    if not connection.Win32_LogicalDisk():
        print("No removable media found.")
    else:
        for media in connection.Win32_LogicalDisk():
            if media.VolumeName is not None:
                removable_media.add(media.VolumeName)
    if not connection.Win32_CDROMDrive():
        print("No CD-ROM found.")
    else:
        for media in connection.Win32_CDROMDrive():
            if media.Caption is not None:
                removable_media.add(media.Caption)

    if not connection.Win32_USBController():
        print("No USB Controller found.")
    else:
        for media in connection.Win32_USBController():
            if media.Caption is not None:
                removable_media.add(media.Caption)

    return removable_media

def system_events(start, end):
    """
    Gets the system event logs
    return: list of system events
    """
    handler = win32evtlog.OpenEventLog(None, 'Application')
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
    long_events = set()

    try:
        events = win32evtlog.ReadEventLog(handler, flags, 0)
        while events:
            for event in events:
                name = event.SourceName
                date = event.TimeWritten
                eventID = event.EventID
                event_warning = event.EventType
                category = event.EventCategory
                if start <= date <= end:
                    long_events.add((date, name, eventID, category, event_warning))
            events = win32evtlog.ReadEventLog(handler, flags, 0)
    except Exception as e:
        print(f"Error while fetching system events: {e}")
    return long_events

def main():
    """
    Mandatory arguments:

    """
    start, end = parse_arg()
    start, end = parse_date(start, end)
    print(start, end)

    #Register changes
    list_log_register = register_changes(start, end)
    print(f"Log register in: \n{start.strftime('%d-%m-%Y')} and {end.strftime('%d-%m-%Y')}:\n")
    for date, key in sorted(list_log_register):
        print(f"\t{date.strftime('%d-%m-%Y')} - Register id :{key}")
    
    #Files recents
    list_recent_files = recent_files(start, end)
    print(f"Recent files in: \n{start.strftime('%d-%m-%Y')} and {end.strftime('%d-%m-%Y')}:\n")
    for date, file in sorted(list_recent_files):
        print(f"\t{date.strftime('%d-%m-%Y')} - {file}")

    #Installed programs
    list_installed_programs, list_no_date = installed_programs(start, end)
    print(f"Installed programs in: \n{start.strftime('%d-%m-%Y')} and {end.strftime('%d-%m-%Y')}:\n")
    for date, program in sorted(list_installed_programs):
        print(f"\t{date.strftime('%d-%m-%Y')} - {program}")
    print(f"\nNo date of intall:\n")
    for program in list_no_date:
        print(f"\t{program}")
    
    #Open programs
    list_open_programs = list_opens_program()
    print(f"Open programs or process in \n:")
    for program in sorted(list_open_programs):
        print(f"\t{program}")
    
    #History navigation
    list_history_navigation = navigation_history(start, end)
    print(f"History navigation in  :\n")
    for browser, date, url in sorted(list_history_navigation):
        print(f"\t{browser} : {date.strftime('%d-%m-%Y')} - {url}")
    
    #Connected media
    list_connected_media = connected_media()
    print(f"Connected media in \n ")
    for media in sorted(list_connected_media):
        print(f"\t{media}")
    
    #System events
    list_system_events = system_events(start, end)
    print(f"System events in \n {start.strftime('%d-%m-%Y')} and {end.strftime('%d-%m-%Y')}:\n")
    for date, event, eventID, category, event_warning  in sorted(list_system_events):
        print(f"\t{date.strftime('%d-%m-%Y')} Warning level:{event_warning} Category:{category} - {eventID} - {event}")


def logo():
    """
    Credits and logo
    """
    time = datetime.datetime.now()
    print(f"\n\n\t {time.strftime('%d-%m-%Y %H:%M:%S')}")
    print(f"\t      R E C O V E R Y")
    print(f"\t Tool for Windows Systems\n")
    print(f"\t\t\t\t Credits J.L V 0.0.1\n\n")


def populate_listbox(listbox, path):
    for item in os.listdir(path):
        listbox.insert('end', item)

def tree_directory():
    root = tk.Tk()
    listbox = tk.Listbox(root)
    listbox.pack()
    populate_listbox(listbox, os.environ['USERPROFILE'])
    root.mainloop()

if __name__ == "__main__":
    logo()
    main()
    tree_directory()