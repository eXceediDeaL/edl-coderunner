from prompt_toolkit import HTML


def useRed(content: str)->HTML:
    return HTML(f'<obj fg="ansired">{content}</obj>')


def useGreen(content: str)->HTML:
    return HTML(f'<obj fg="ansigreen">{content}</obj>')


def useBlue(content: str)->HTML:
    return HTML(f'<obj fg="ansiblue">{content}</obj>')


def useCyan(content: str)->HTML:
    return HTML(f'<obj fg="ansicyan">{content}</obj>')


def useYellow(content: str)->HTML:
    return HTML(f'<obj fg="ansiyellow">{content}</obj>')
