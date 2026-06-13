"""
sys_manager.py
Módulo de auditoría del sistema. Compatible Windows y Linux sin librerías propietarias.
"""

import platform
import subprocess


class SysManager:
    """Detecta el SO y ejecuta comandos de auditoría multiplataforma."""

    def __init__(self):
        self.os_name = platform.system()

    def is_windows(self) -> bool:
        return self.os_name == "Windows"

    def _run(self, cmd: list, timeout: int = 20) -> str:
        """Ejecuta un comando y devuelve su salida como string."""
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True,
                timeout=timeout, encoding="utf-8",
                errors="replace", shell=self.is_windows(),
            )
            return (result.stdout or result.stderr or "Sin salida").strip()
        except subprocess.TimeoutExpired:
            return f"[TIMEOUT] El comando tardó más de {timeout}s."
        except FileNotFoundError:
            return f"[ERROR] Comando no encontrado: {' '.join(cmd)}"
        except Exception as e:
            return f"[ERROR] {e}"

    def get_os_info(self) -> dict:
        return {
            "OS":           self.os_name,
            "Release":      platform.release(),
            "Version":      platform.version(),
            "Hostname":     platform.node(),
            "Architecture": platform.architecture()[0],
            "Python":       platform.python_version(),
        }

    def get_processes(self) -> str:
        if self.is_windows():
            return self._run(["tasklist"], timeout=20)
        return self._run(["ps", "aux"], timeout=20)

    def get_network(self) -> str:
        if self.is_windows():
            return self._run(["netstat", "-ano"], timeout=15)
        return self._run(["netstat", "-tuln"], timeout=15)

    def get_disk_usage(self) -> str:
        if self.is_windows():
            cmd = ("Get-WmiObject Win32_LogicalDisk | "
                   "Select-Object Caption, FreeSpace, Size | Format-Table -AutoSize")
            return self._run(["powershell", "-Command", cmd], timeout=15)
        return self._run(["df", "-h"], timeout=10)

    def disk_usage(self) -> str:
        return self.get_disk_usage()

    def get_cpu_info(self) -> str:
        if self.is_windows():
            cmd = ("Get-WmiObject Win32_Processor | "
                   "Select-Object CurrentClockSpeed, Name, NumberOfCores | Format-Table -AutoSize")
            return self._run(["powershell", "-Command", cmd], timeout=15)
        return self._run(["lscpu"], timeout=10)

    def get_memory_info(self) -> str:
        if self.is_windows():
            cmd = ("Get-WmiObject Win32_OperatingSystem | "
                   "Select-Object FreePhysicalMemory, TotalVisibleMemorySize | Format-Table -AutoSize")
            return self._run(["powershell", "-Command", cmd], timeout=15)
        return self._run(["free", "-h"], timeout=10)

    def memory_info(self) -> str:
        return self.get_memory_info()

    def get_users(self) -> str:
        if self.is_windows():
            return self._run(["net", "user"], timeout=10)
        return self._run(["cut", "-d:", "-f1", "/etc/passwd"], timeout=10)

    def get_services(self) -> str:
        if self.is_windows():
            return self._run(["sc", "query", "type=", "all"], timeout=30)
        return self._run(["systemctl", "list-units", "--type=service",
                          "--no-pager", "--all"], timeout=20)

    def get_system_logs(self) -> str:
        if self.is_windows():
            cmd = ("Get-EventLog -LogName System -Newest 20 "
                   "-EntryType Error,Warning | "
                   "Select-Object TimeGenerated, EntryType, Message | Format-List")
            return self._run(["powershell", "-Command", cmd], timeout=30)
        return self._run(["journalctl", "-n", "50", "--no-pager", "-p", "err"], timeout=20)

    def get_full_diagnostics(self) -> dict:
        """Ejecuta todos los módulos y devuelve un diccionario completo."""
        return {
            "os_info":      self.get_os_info(),
            "procesos":     self.get_processes(),
            "red":          self.get_network(),
            "disco":        self.get_disk_usage(),
            "cpu":          self.get_cpu_info(),
            "memoria":      self.get_memory_info(),
            "usuarios":     self.get_users(),
            "servicios":    self.get_services(),
            "logs_sistema": self.get_system_logs(),
        }