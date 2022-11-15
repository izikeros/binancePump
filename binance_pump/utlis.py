def clear_console_screen():
    print("\033")


def seconds_to_h_m_s(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return "%02d:%02d:%02d" % (hours, minutes, seconds)


def color_me(text, val):
    if val > 0:
        return f"[green]{text}[/green]"
    elif val < 0:
        return f"[red]{text}[/red]"
    else:
        return text
