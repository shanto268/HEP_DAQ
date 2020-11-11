import PySimpleGUI as sg

# Define the window's contents
layout = [[sg.Text("Path to .ftr file:")], [sg.Input(key='path')],
          [sg.Text(size=(40, 1), key='-OUTPUT-')],
          [sg.Button('Ok'), sg.Button('Quit')]]

# Create the window
window = sg.Window('Prototype 1B Data Analysis', layout)

# Display and interact with the Window using an Event Loop
while True:
    event, values = window.read()
    # See if user wants to quit or window was closed
    if event == sg.WINDOW_CLOSED or event == 'Quit':
        break
    # Output a message to the window
    window['-OUTPUT-'].update('Input File:' + values['path'])

# Finish up by removing from the screen
window.close()
