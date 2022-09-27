import io
from contextlib import contextmanager
from enum import Enum, auto
from itertools import groupby, islice

import numpy as np

U1 = 255
U2 = 65535


class PnmProblem(Enum):
    FILE_OPEN = auto()
    UNKNOWN_TAG = auto()
    FORMAT_ERROR = auto()
    DATA_ERROR = auto()


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
    reader = io.BufferedReader(file)
    tag = reader.read(2)
    if tag in [b"P5", b"P6"]:
        plain = False
    elif tag in [b"P2", b"P3"]:
        plain = True
    else:
        raise PnmError(PnmProblem.UNKNOWN_TAG, tag)

    data = iter(lambda: reader.read(1), b"")
    fields = (b"".join(group).decode("ascii") for is_space, group in groupby(data, key=bytes.isspace) if not is_space)

    try:
        width, height, max_val = map(int, islice(fields, 0, 3))
    except ValueError as e:
        raise PnmError(PnmProblem.FORMAT_ERROR, "header") from e

    if tag in [b"P2", b"P5"]:
        shape = (height, width)
    else:
        shape = (height, width, 3)

    if max_val <= U1:
        dtype = np.dtype("u1")
    elif max_val <= U2:
        dtype = np.dtype(">u2")
    else:
        raise PnmError(PnmProblem.FORMAT_ERROR, "max_val")

    try:
        if plain:
            image_data = np.fromiter(map(int, fields), dtype)
        else:
            image_data = np.frombuffer(reader.read(), dtype)
    except ValueError as e:
        raise PnmError(PnmProblem.FORMAT_ERROR, "image") from e

    try:
        image = image_data.reshape(shape)
    except ValueError as e:
        raise PnmError(PnmProblem.FORMAT_ERROR, "image data length") from e

    return image, max_val


def write_pnm(image, max_val, file):
    if image.ndim == 2:
        tag = "P5"
    elif image.ndim == 3:
        tag = "P6"
        if image.shape[2] != 3:
            raise PnmError(PnmProblem.DATA_ERROR, "shape")
    else:
        raise PnmError(PnmProblem.DATA_ERROR, "shape")

    height, width = image.shape[:2]

    try:
        if max_val <= U1:
            dtype = np.dtype("u1")
        elif max_val <= U2:
            dtype = np.dtype(">u2")
        else:
            raise PnmError(PnmProblem.DATA_ERROR, "max_val")
        image = image.astype(dtype, casting="same_kind", copy=False)
    except TypeError as e:
        raise PnmError(PnmProblem.DATA_ERROR, "dtype") from e

    header = f"{tag} {width} {height} {max_val}\n".encode("ascii")
    file.write(header)
    file.write(image.tobytes())
