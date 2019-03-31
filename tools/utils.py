from random import randint


def generate_name(parts=4, partsize=4):
    part_pattern = "%d" * partsize

    generated_parts = []
    for i in range(0, parts):
        part = ""
        for j in range(0, partsize):
            part += str(randint(0, 9))
        generated_parts.append(part)

    return "-".join(generated_parts)


