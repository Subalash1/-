import socket
import subprocess
import platform

def get_local_ip():
    """获取本机局域网IP地址"""
    try:
        # 创建一个UDP套接字连接到远程地址来获取本地IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def get_network_info():
    """获取网络信息"""
    local_ip = get_local_ip()
    system = platform.system()
    
    print("=" * 50)
    print("🎮 中文猜词游戏 - 网络信息")
    print("=" * 50)
    print(f"本机系统: {system}")
    print(f"本机IP地址: {local_ip}")
    print()
    print("📱 分享方式:")
    print(f"1. 本地访问: http://localhost:5000")
    print(f"2. 局域网访问: http://{local_ip}:5000")
    print()
    print("📋 分享给朋友:")
    print(f"   让同一WiFi下的朋友访问: http://{local_ip}:5000")
    print()
    
    if system == "Windows":
        print("🔧 如果朋友无法访问，可能需要:")
        print("   1. 关闭Windows防火墙")
        print("   2. 或在防火墙中允许Python程序")
        print("   3. 确保在同一WiFi网络下")
    
    print("=" * 50)

if __name__ == "__main__":
    get_network_info()