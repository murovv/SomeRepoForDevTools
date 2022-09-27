import io
import traceback

import PySimpleGUI as sg

from pnm import PnmError, PnmProblem, open_pnm_file, read_pnm, write_pnm


def handle_exception(exc):
    error_text = "Unknown error"
    if isinstance(exc, PnmError):
        if exc.problem == PnmProblem.FILE_OPEN:
            error_text = "Error opening file"
        elif exc.problem == PnmProblem.UNKNOWN_TAG:
            error_text = f"Unknown tag {exc.args[0]}"
        elif exc.problem == PnmProblem.FORMAT_ERROR:
            error_text = f"Invalid {exc.args[0]}"
        elif exc.problem == PnmProblem.DATA_ERROR:
            error_text = f"Invalid image ({exc.args[0]})"
    return traceback.format_exc(), error_text


sg.theme("DarkAmber")

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
    event, values = sg.Window(
        "Error",
        [
            [sg.Text(error_text)],
            [sg.Multiline(error, size=(sg.MESSAGE_BOX_LINE_WIDTH, sg.MAX_SCROLLED_TEXT_BOX_HEIGHT))],
            [sg.P(), sg.Exit(), sg.P()],
        ],
    ).read(close=True)
else:
    sg.Window("PNP", [[sg.Image(data=buffer.getvalue())], [sg.P(), sg.Exit(), sg.P()]]).read(close=True)
