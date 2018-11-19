from prompt_toolkit import HTML

def useRed(content):
    return HTML(f'<obj fg="ansired">{content}</obj>')

def useGreen(content):
    return HTML(f'<obj fg="ansigreen">{content}</obj>')

def useBlue(content):
    return HTML(f'<obj fg="ansiblue">{content}</obj>')

def useCyan(content):
    return HTML(f'<obj fg="ansicyan">{content}</obj>')

def useYellow(content):
    return HTML(f'<obj fg="ansiyellow">{content}</obj>')