"""
Nova v2.7.0 - Desktop Shortcut Creator
Creates a robust .lnk shortcut on the user's Desktop.
Usage: python tools/create_shortcut.py
"""
import os
import subprocess
import sys

def create_shortcut():
    # 1. Detect paths
    nova_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target = os.path.join(nova_root, "start.bat")
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    shortcut_path = os.path.join(desktop, "Nova.lnk")
    
    # Icon: Use python.exe from venv as fallback
    icon_path = os.path.join(nova_root, "venv", "Scripts", "python.exe")
    if not os.path.exists(icon_path):
        icon_path = target  # Fallback to bat icon
    
    print(f"[Nova Shortcut Creator]")
    print(f"  Target:    {target}")
    print(f"  Shortcut:  {shortcut_path}")
    print(f"  WorkDir:   {nova_root}")
    print(f"  Icon:      {icon_path}")
    print()
    
    # 2. Verify target exists
    if not os.path.exists(target):
        print(f"[ERROR] No se encontró start.bat en: {target}")
        sys.exit(1)
    
    # 3. Create shortcut using PowerShell COM
    ps_script = f'''
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{target}"
$Shortcut.WorkingDirectory = "{nova_root}"
$Shortcut.IconLocation = "{icon_path},0"
$Shortcut.Description = "Nova v2.7.0 - True Artifacts"
$Shortcut.WindowStyle = 7
$Shortcut.Save()
'''
    
    try:
        result = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0 and os.path.exists(shortcut_path):
            print(f"[OK] Acceso directo creado exitosamente en el Escritorio!")
            print(f"     -> {shortcut_path}")
        else:
            print(f"[ERROR] Fallo al crear el acceso directo.")
            if result.stderr:
                print(f"  PowerShell error: {result.stderr.strip()}")
    except subprocess.TimeoutExpired:
        print("[ERROR] Timeout al ejecutar PowerShell.")
    except FileNotFoundError:
        print("[ERROR] PowerShell no encontrado. ¿Estás en Windows?")

if __name__ == "__main__":
    create_shortcut()
