import io
import traceback

import PySimpleGUI as sg

from pnm import PnmError, PnmProblem, open_pnm_file, read_pnm, write_pnm

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
except PnmError as e:
    error = traceback.format_exc()
    if e.problem == PnmProblem.FILE_OPEN:
        error_text = "Error opening file"
    elif e.problem == PnmProblem.UNKNOWN_TAG:
        error_text = f"Unknown tag {e.args[0]}"
    elif e.problem == PnmProblem.FORMAT_ERROR:
        error_text = f"Invalid {e.args[0]}"
    elif e.problem == PnmProblem.DATA_ERROR:
        error_text = "Invalid image"
except Exception as e:
    error = traceback.format_exc()
if error:
    if not error_text:
        error_text = "Unknown error"
    event, values = sg.Window(
        "Error",
        [
            [sg.Text(error_text)],
            [sg.Multiline(error, size=(sg.MESSAGE_BOX_LINE_WIDTH, sg.MAX_SCROLLED_TEXT_BOX_HEIGHT))],
            [sg.Exit()],
        ],
    ).read(close=True)
    if event == "stack":
        with open("trace", "w") as file:
            file.write(str(error))
else:
    sg.Window("PNP", [[sg.Image(data=buffer.getvalue())], [sg.Push(), sg.Exit(), sg.Push()]]).read(close=True)
