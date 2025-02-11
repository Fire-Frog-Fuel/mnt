from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Define custom colors
ORANGE = '\033[38;2;255;165;0m'  # RGB for orange
YELLOW = Fore.YELLOW
GREEN = Fore.GREEN
BRIGHT_RED = '\033[38;2;255;0;0m'  # Vivid red (not pinkish)

def style_print(info_text,color,text: object, end_: str | None = "\n"):
    print(f"{color}[{info_text}]{Style.RESET_ALL} {text}",end=end_)

def WARNING(text: object, end_: str | None = "\n"):
    print(f"{ORANGE}[WARNING]{Style.RESET_ALL} {text}",end=end_)
    
def ERROR(text: object, end_: str | None = "\n"):
    print(f"{BRIGHT_RED}[ERROR]{Style.RESET_ALL} {text}",end=end_)

def INFO(text: object, end_: str | None = "\n"):
    print(f"{GREEN}[INFO]{Style.RESET_ALL} {text}",end=end_)