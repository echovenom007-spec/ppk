import ctypes
import sys
from ctypes import wintypes

ntdll = ctypes.WinDLL('ntdll')
ntdll.NtSuspendProcess.argtypes = [wintypes.HANDLE]

if len(sys.argv) < 2:
    print("Usage: python suspend.py <PID>")
    sys.exit(1)

pid = int(sys.argv[1])

handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, pid)
if handle:
    ntdll.NtSuspendProcess(handle)
    print(f"Process {pid} suspended.")
    ctypes.windll.kernel32.CloseHandle(handle)
else:
    print(f"Could not open process {pid} (Access Denied or invalid PID)")