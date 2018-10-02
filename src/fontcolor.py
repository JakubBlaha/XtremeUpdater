def font_color(color: tuple) -> tuple:
    """
    Returns the best font color for given background color.
    
    Option `Color` is a 3 to 4 long tuple and represents [red, green, blue, alpha].
    """

    is_alpha = len(color) == 4
    if is_alpha:
        color = color[:-1]

    red, green, blue = color
    red *= 255
    green *= 255
    blue *= 255
    calculated = (
        0, 0, 0,
        1) if (red * 0.299 + green * 0.587 + blue * 0.114) > 186 else (1, 1, 1,
                                                                       1)

    return calculated if is_alpha else calculated[:-1]
