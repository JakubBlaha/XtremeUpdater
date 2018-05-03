def fade(st, nd, steps=10):
    st = st.strip("#")
    nd = nd.strip("#")
    st_rgb = hex_to_rgb(st)
    nd_rgb = hex_to_rgb(nd)

    to_step = [nds - sts for sts, nds in zip(st_rgb, nd_rgb)]

    (rstep, gstep, bstep) = [to_step[i] // steps for i in (0, 1, 2)]

    color_steps = []
    for i in range(steps - 1):
        color_steps.append(
            rgb_to_hex((st_rgb[0]+i*rstep, st_rgb[1]+i*gstep, st_rgb[2]+i*bstep))
        )
    color_steps.append("#" + nd)

    return color_steps


def hex_to_rgb(h):
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]

def rgb_to_hex(rgb):
    if len(rgb) > 4:
        raise Exception('Invalid RGB or RGBA')

    if len(rgb) == 4:
        rgb = rgb[0:-1]

    _long_hex = lambda s: ('0' if len(s) == 1 else '') + s
    _hex = lambda i: _long_hex(format(i, 'x'))
    return f'#{_hex(rgb[0])}{_hex(rgb[1])}{_hex(rgb[2])}'

def long_hex(h):
    if len(h) == 3:
        return "".join([ch*2 for ch in h])
    return h
    
