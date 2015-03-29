# pylint: disable=redefined-builtin
def human_size(size, format='.2f', max_value=1000):
    for unit in ['b', 'Kb', 'Mb', 'Gb', 'Tb', 'Pb']:
        if abs(size) < max_value:
            break
        size /= 1024.
    format_str = "{{:{}}} {{}}".format(format)
    # pylint: disable=undefined-loop-variable
    return format_str.format(size, unit)
