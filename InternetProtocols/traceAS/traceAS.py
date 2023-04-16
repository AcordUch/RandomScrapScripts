import subprocess
import argparse
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from re import compile as re_compile

IP_REG = re_compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b[^.]")
AS_REG = re_compile(r"[Oo]riginA?S?: *([\d\w]+?)\n")
COUNTRY_REG = re_compile(r"[Cc]ountry: *([\w]+?)\n")
PROVIDER_REG = re_compile(r"mnt-by: *([\w\d-]+?)\n")
ARG_PARSER = argparse.ArgumentParser()
destination = ""


class IpInfo:
    def __init__(self, ip: str, as_: str, country: str, provider: str):
        self.ip = ip
        self.as_ = as_
        self.country = country
        self.provider = provider


def main() -> None:
    process_key()
    trace_res = subprocess.run(['tracert', destination], stdout=subprocess.PIPE).stdout.decode("ISO-8859-1")
    print_info(IpInfo("IP", "AS", "Country", "Provider"))
    for ip in IP_REG.findall(trace_res)[1:]:
        print_info(get_ip_info(ip.strip("]")))


def download_page(url: str) -> str:
    try:
        with urlopen(url) as page:
            content = page.read().decode('utf-8', errors='ignore')
            return content
    except (URLError, HTTPError):
        return ""


def get_ip_info(ip: str) -> IpInfo:
    def try_get(reg) -> str:
        res = reg.search(page)
        if res:
            return reg.search(page).group(1)
        else:
            return "-"

    if is_grey_ip(ip):
        return IpInfo(ip, "Grey IP", "", "")

    page = download_page(f"https://www.nic.ru/whois/?searchWord={ip}")
    return IpInfo(
        ip,
        try_get(AS_REG),
        try_get(COUNTRY_REG),
        try_get(PROVIDER_REG)
    )


def is_grey_ip(ip: str) -> bool:
    return (ip.startswith("192.168.") or
            ip.startswith("10.") or
            ip.startswith("172.") and 15 < int(ip.split(".")[1]) < 32)


def process_key() -> None:
    def configure_arg_parser() -> None:
        ARG_PARSER.add_argument("-d", "--destination", dest="destination", required=True)

    global destination
    configure_arg_parser()
    args = ARG_PARSER.parse_args()
    destination = args.destination


def print_info(ip_info: IpInfo) -> None:
    print("{} {} {} {}".format(ip_info.ip, ip_info.as_, ip_info.country, ip_info.provider))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
    finally:
        input("\nДля выхода нажмите Enter...")
