import io
import traceback

import PySimpleGUI as sg

from pnm import open_pnm_file, read_pnm, write_pnm
from pnm.exceptions import *


def handle_exception(exc):
    if isinstance(exc, FileOpenError):
        error_text = "Error opening file"
    elif isinstance(exc, UnknownTagError):
        error_text = f"Unknown tag {exc.tag}"
    elif isinstance(exc, FormatError):
        error_text = f"Invalid {exc.file_part}"
    elif isinstance(exc, DataError):
        error_text = f"Invalid image ({exc.problem})"
    elif isinstance(exc, PnmError):
        error_text = "PNM error"
    else:
        error_text = "Unknown error"
    return traceback.format_exc(), error_text


sg.theme("DarkGray15")

event, values = sg.Window(
    "Open PNP", [[sg.Text("Filename")], [sg.Input(k="filename"), sg.FileBrowse()], [sg.OK(), sg.Cancel()]]
).read(close=True)
if event != "OK":
    exit()
filename = values["filename"]
error, error_text = None, None
buffer = io.BytesIO()
try:
    with open_pnm_file(filename, "rb") as file:
        image, max_val = read_pnm(file)
    write_pnm(image, max_val, buffer)
except Exception as exc:
    error, error_text = handle_exception(exc)
    sg.Window(
        "Error",
        [
            [sg.Text(error_text)],
            [sg.Multiline(error, size=(sg.MESSAGE_BOX_LINE_WIDTH, sg.MAX_SCROLLED_TEXT_BOX_HEIGHT))],
            [sg.P(), sg.Exit(), sg.P()],
        ],
    ).read(close=True)
else:
    sg.Window("PNP", [[sg.Image(data=buffer.getvalue())], [sg.P(), sg.Exit(), sg.P()]]).read(close=True)
