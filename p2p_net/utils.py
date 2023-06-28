import socket
import requests
import config

def get_current_hostname() -> str:
    '''현재 서버의 hostname(ex: naver, deeplearnig, daum 등) 리턴'''
    return socket.gethostname()

def get_internal_ip() -> str:
    '''현재 서버의 IP 주소 리턴'''
    host_name = socket.gethostname()
    ip_addr = socket.gethostbyname(host_name)
    return ip_addr

def get_external_ip() -> str:
    return requests.get(config.IP_CHECK_SERVICE_PROVIDER).text.strip()

if __name__=='__main__':
    print('utils.py')
    print(f'IP: {get_internal_ip()}')
    print(f'Hostname: {get_current_hostname()}')
    print(f'Ext IP: {get_external_ip()}')