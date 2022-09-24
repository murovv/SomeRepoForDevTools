from contextlib import contextmanager
from enum import Enum, auto
from itertools import groupby, islice

import numpy as np

U1 = 255
U2 = 65535


class PnmProblem(Enum):
    FILE_OPEN = auto()
    UNKNOWN_TAG = auto()


class PnmError(Exception):
    def __init__(self, problem, *args):
        super().__init__(*args)
        self.problem = problem


@contextmanager
def open_pnm_file(*args, **kwargs):
    try:
        file = open(*args, **kwargs)
    except IOError as e:
        raise PnmError(PnmProblem.FILE_OPEN) from e
    try:
        yield file
    finally:
        file.close()


def read_pnm(file):
    data = iter(lambda: file.read(1), b"")
    fields = (b"".join(group).decode("ascii") for is_space, group in groupby(data, key=bytes.isspace) if not is_space)
    tag, *rest = islice(fields, 0, 4)
    width, height, max_val = map(int, rest)

    if max_val <= U1:
        dtype = np.dtype("u1")
    else:
        dtype = np.dtype(">u2")

    if tag in ["P5", "P6"]:
        image_data = np.frombuffer(file.read(), dtype)
    elif tag in ["P2", "P3"]:
        image_data = np.fromiter(map(int, fields), dtype)
    else:
        raise PnmError(PnmProblem.UNKNOWN_TAG, tag)

    if tag in ["P2", "P5"]:
        shape = (height, width)
    else:
        shape = (height, width, 3)
    image = image_data.reshape(shape)

    if max_val not in [U1, U2]:
        image = np.round(image.astype(float) * U2 / max_val).astype("u2")
    return image


def write_pnm(image, file):
    if image.ndim == 2:
        tag = "P5"
    else:
        tag = "P6"
    height, width = image.shape[:2]
    if image.itemsize == 1:
        max_val = U1
    else:
        image = image.newbyteorder(">")
        max_val = U2
    header = f"{tag} {width} {height} {max_val}\n".encode("ascii")

    file.write(header)
    file.write(image.tobytes())
