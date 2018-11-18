from colorama import Fore, Back, Style

def useRed(content):
    return f"{Fore.RED}{content}{Style.RESET_ALL}"

def useGreen(content):
    return f"{Fore.GREEN}{content}{Style.RESET_ALL}"

def useBlue(content):
    return f"{Fore.BLUE}{content}{Style.RESET_ALL}"

def useCyan(content):
    return f"{Fore.CYAN}{content}{Style.RESET_ALL}"

def useYellow(content):
    return f"{Fore.YELLOW}{content}{Style.RESET_ALL}"