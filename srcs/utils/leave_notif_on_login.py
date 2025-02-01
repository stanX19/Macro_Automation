import re
import os
from os.path import dirname
try:
    from .unique_name import unique_name
except ImportError:
    from unique_name import unique_name


def clean_message(text):
    """Escape special characters for VBScript message content"""
    # Escape backslashes
    text = text.replace('\\', '\\\\')
    # Escape double quotes
    text = text.replace('"', '""')
    # Convert newlines to VBScript line breaks
    text = text.replace("\n", "\" & vbCrLf & \"")
    return text


def leave_notif_on_login(message, title="Python"):
    """
    Creates a VBScript in the Startup folder to display
    a notification at login. Files will self-delete after execution.
    """
    message = clean_message(message)
    title = clean_message(title)

    # Get Windows Startup folder path
    startup_folder = os.path.expandvars(
        r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
    )
    task_name = re.sub(r'[^a-zA-Z0-9-]', '_', title)

    # Create path for the VBScript file
    vbs_path = unique_name(os.path.join(startup_folder,  f"{task_name}.vbs"))

    # VBScript content for message display
    vbs_content = f'''
Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")

' Create the PowerShell script file
psScriptPath = FSO.GetSpecialFolder(2) & "\\notification.ps1"
psScriptContent = "[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime]" & vbCrLf & _
    "$Template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastImageAndText02)" & vbCrLf & _
    "$ToastXml = $Template" & vbCrLf & _
    "$ToastXml.GetElementsByTagName('text')[0].AppendChild($ToastXml.CreateTextNode(""{message}""))" & vbCrLf & _
    "$Toast = [Windows.UI.Notifications.ToastNotification]::new($ToastXml)" & vbCrLf & _
    "$Notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier(""{title}"")" & vbCrLf & _
    "$Notifier.Show($Toast)"

Set psScriptFile = FSO.CreateTextFile(psScriptPath, True)
psScriptFile.WriteLine psScriptContent
psScriptFile.Close

' Run the PowerShell script
WshShell.Run "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File """ & psScriptPath & """", 0, True

' Delete the PowerShell script file
FSO.DeleteFile psScriptPath, True
FSO.DeleteFile WScript.ScriptFullName, True
'''

    with open(vbs_path, "w", encoding="utf-8") as vbs_file:
        vbs_file.write(vbs_content)

    return vbs_path


def main():
    title = "Awesome!"
    message = "Hello world!!\n:Yeah"
    path = leave_notif_on_login(message, title)
    print(path)
    os.system(f"\"{path}\"")


if __name__ == '__main__':
    main()