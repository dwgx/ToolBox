import logging
import os
import platform
import re
import shutil
import socket
import subprocess
import threading
import time

logger = logging.getLogger('SystemCore')

DNS_INFO = {
    "8.8.8.8": ("Google DNS", "全球"),
    "8.8.4.4": ("Google DNS", "全球"),
    "1.1.1.1": ("Cloudflare DNS", "全球"),
    "1.0.0.1": ("Cloudflare DNS", "全球"),
    "9.9.9.9": ("Quad9 DNS", "全球"),
    "149.112.112.112": ("Quad9 DNS", "全球"),
    "208.67.222.222": ("OpenDNS", "全球"),
    "208.67.220.220": ("OpenDNS", "全球"),
    "8.26.56.26": ("Comodo Secure DNS", "全球"),
    "8.20.247.20": ("Comodo Secure DNS", "全球"),
    "4.2.2.2": ("Level3 DNS", "全球"),
    "4.2.2.1": ("Level3 DNS", "全球"),
    "208.67.222.123": ("OpenDNS Family Shield", "全球"),
    "208.67.220.123": ("OpenDNS Family Shield", "全球"),
    "114.114.114.114": ("中国电信 DNS", "中国"),
    "223.5.5.5": ("阿里云 DNS", "中国"),
    "223.6.6.6": ("阿里云 DNS", "中国"),
    "180.76.76.76": ("百度 DNS", "中国"),
    "119.29.29.29": ("DNSPod DNS", "中国"),
    "182.254.116.116": ("腾讯 DNS", "中国"),
    "119.28.28.28": ("腾讯 DNS", "中国"),
    "140.207.198.241": ("中国移动 DNS", "中国"),
    "210.140.92.20": ("NTT Communications", "日本"),
}

def is_admin():
    try:
        if os.name == 'nt':
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        else:
            return os.geteuid() == 0
    except:
        return False

def execute_command(command):
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
        logger.info(output.strip())
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"命令执行失败: {e.output.strip()}")
        return False
    except Exception as e:
        logger.error(f"命令执行出现异常: {str(e)}")
        return False

def repair_network():
    logger.info("正在修复网络问题...")
    success = True
    if execute_command("netsh int ip reset"):
        logger.info("已成功重置 IP 协议栈。")
    else:
        logger.error("重置 IP 协议栈失败。请以管理员身份运行本程序。")
        success = False
    if execute_command("netsh winsock reset"):
        logger.info("已成功重置 Winsock。")
    else:
        logger.error("重置 Winsock 失败。请以管理员身份运行本程序。")
        success = False
    if success:
        logger.info("网络修复操作已完成。")
    return success

def reset_dns():
    logger.info("正在重置 DNS...")
    if execute_command("ipconfig /flushdns"):
        logger.info("已成功刷新 DNS 缓存。")
        return True
    else:
        logger.error("刷新 DNS 缓存失败。")
        return False

def release_and_renew_ip():
    logger.info("正在释放并刷新 IP 地址...")
    success = True
    if execute_command("ipconfig /release"):
        logger.info("已成功释放 IP 地址。")
    else:
        logger.error("释放 IP 地址失败。请以管理员身份运行本程序。")
        success = False
    if execute_command("ipconfig /renew"):
        logger.info("已成功刷新 IP 地址。")
    else:
        logger.error("刷新 IP 地址失败。请以管理员身份运行本程序。")
        success = False
    if success:
        logger.info("IP 地址释放并刷新操作已完成。")
    return success

def reset_proxy():
    logger.info("正在关闭所有代理设置...")
    commands = [
        'reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyEnable /f',
        'reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyServer /f',
        'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0 /f',
        "netsh winhttp reset proxy"
    ]
    success = True
    for cmd in commands:
        if not execute_command(cmd):
            success = False
    if success:
        logger.info("已成功关闭所有代理设置。")
    else:
        logger.error("关闭代理设置失败。请以管理员身份运行本程序。")
    return success

def reset_winsock():
    logger.info("正在重置 Winsock...")
    if execute_command("netsh winsock reset"):
        logger.info("已成功重置 Winsock。")
        return True
    else:
        logger.error("重置 Winsock 失败。请以管理员身份运行本程序。")
        return False

def check_hosts_file():
    logger.info("正在检测 HOSTS 文件...")
    hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
    try:
        with open(hosts_path, 'r', encoding='utf-8') as f:
            content = f.read()
            suspicious_entries = []
            for line in content.splitlines():
                if line.strip() and not line.startswith('#'):
                    if 'localhost' not in line and '::1' not in line:
                        suspicious_entries.append(line)
            if suspicious_entries:
                logger.warning("检测到可疑的 HOSTS 条目：")
                for entry in suspicious_entries:
                    logger.warning(entry)
                return suspicious_entries
            else:
                logger.info("HOSTS 文件未发现异常。")
                return []
    except Exception as e:
        logger.error(f"读取 HOSTS 文件失败: {str(e)}")
        return None

def cleanup_temp_files():
    logger.info("正在清理临时文件...")
    temp_path = os.environ.get('TEMP', None)
    if temp_path and os.path.exists(temp_path):
        try:
            file_count = 0
            for root, dirs, files in os.walk(temp_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                        file_count += 1
                    except Exception as e:
                        logger.error(f"无法删除文件 {file_path}: {str(e)}")
                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    try:
                        shutil.rmtree(dir_path)
                        file_count += 1
                    except Exception as e:
                        logger.error(f"无法删除文件夹 {dir_path}: {str(e)}")
            logger.info(f"临时文件清理完成，删除了 {file_count} 个文件和文件夹。")
            return file_count
        except Exception as e:
            logger.error(f"清理临时文件失败: {str(e)}")
            return None
    else:
        logger.error("无法找到临时文件夹路径。")
        return None

def get_current_dns():
    try:
        if platform.system() == "Windows":
            command = "ipconfig /all"
            output = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT)
            dns_servers = re.findall(r"DNS Servers[ .]*?:\s*([^\n]+)", output)
            if dns_servers:
                dns_list = dns_servers[0].split()
                current_dns = dns_list[0]
                current_secondary_dns = dns_list[1] if len(dns_list) > 1 else "未设置"
            else:
                current_dns = "未设置"
                current_secondary_dns = "未设置"
        else:
            with open('/etc/resolv.conf', 'r') as f:
                dns_servers = [line.split()[1] for line in f if line.startswith('nameserver')]
            current_dns = dns_servers[0] if dns_servers else "未设置"
            current_secondary_dns = dns_servers[1] if len(dns_servers) > 1 else "未设置"
        logger.info(f"当前 DNS 设置: {current_dns}")
        logger.info(f"当前次 DNS 设置: {current_secondary_dns}")
        return current_dns, current_secondary_dns
    except Exception as e:
        logger.error(f"获取当前 DNS 设置失败: {str(e)}")
        return None, None

def scan_fastest_dns(dns_list):
    logger.info("正在扫描最快的 DNS 服务器...")
    fastest_dns = None
    fastest_time = float('inf')
    results = []

    def ping_dns(dns):
        try:
            start_time = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect((dns, 53))
            end_time = time.time()
            response_time = end_time - start_time
            sock.close()
            return dns, response_time
        except Exception:
            return dns, float('inf')

    threads = []
    results_lock = threading.Lock()
    for dns in dns_list:
        thread = threading.Thread(target=lambda d=dns: add_ping_result(ping_dns(d), results, results_lock))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    for dns, response_time in results:
        provider, region = DNS_INFO.get(dns, ("未知", "未知"))
        if response_time < fastest_time:
            fastest_time = response_time
            fastest_dns = dns
    return results, fastest_dns

def add_ping_result(result, results, lock):
    with lock:
        results.append(result)

def get_active_interface():
    try:
        command = "netsh interface show interface"
        output = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT)
        for line in output.splitlines():
            if "已连接" in line or "Connected" in line:
                match = re.search(r"(已连接|Connected)\s+(专用|Dedicated)\s+([^\s]+)", line)
                if match:
                    interface_name = match.group(3)
                    return interface_name
                else:
                    parts = line.strip().split()
                    if len(parts) >= 4:
                        interface_name = parts[-1]
                        return interface_name
        return None
    except subprocess.CalledProcessError as e:
        logger.error(f"获取活动网络接口失败: {e.output}")
        return None
    except Exception as e:
        logger.error(f"获取活动网络接口出现异常: {str(e)}")
        return None

def set_dns(primary_dns, secondary_dns):
    try:
        if platform.system() == "Windows":
            interface_name = get_active_interface()
            if not interface_name:
                logger.error("未找到活动的网络接口。")
                return False
            primary_command = f'netsh interface ip set dns name="{interface_name}" static {primary_dns} primary'
            if execute_command(primary_command):
                logger.info(f"已将主 DNS 设置为: {primary_dns}")
            else:
                logger.error(f"设置主 DNS 失败: {primary_dns}")
                return False
            if secondary_dns:
                secondary_command = f'netsh interface ip add dns name="{interface_name}" addr={secondary_dns} index=2'
                if execute_command(secondary_command):
                    logger.info(f"已将次 DNS 设置为: {secondary_dns}")
                else:
                    logger.error(f"设置次 DNS 失败: {secondary_dns}")
                    return False
            return True
        else:
            with open('/etc/resolv.conf', 'w') as f:
                f.write(f"nameserver {primary_dns}\n")
                if secondary_dns:
                    f.write(f"nameserver {secondary_dns}\n")
            logger.info(f"已将 DNS 设置为: {primary_dns} 和 次 DNS: {secondary_dns}")
            return True
    except Exception as e:
        logger.error(f"设置 DNS 失败: {str(e)}")
        return False


