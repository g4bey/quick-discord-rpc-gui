from pypresence import Presence
import PySimpleGUIQt as sg
from time import time
from urllib.parse import urlparse


# ---------------------------------------------------

client_id = ""

saved_payload = {
    'large_image': None,
    'small_image': None,
    'large_text': None,
    'small_text': None,
    'state': None,
    'details': None,
    'buttons': None,
    'start': None
}

keys = [
    'state',
    'details',
    'timestamp',
    'large_text',
    'small_text',
    'large_image',
    'small_image',
    'label_1',
    'url_1',
    'label_2',
    'url_2'
]

RPC = Presence(client_id=client_id)

RPC.connect()

last_update = 0

clear_requested = False


# ---------------------------------------------------


def is_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except BaseException:
        return False


def update_payload(values, keys, window):
    payload = {
        'large_image': values['large_image'] or None,
        'small_image': values['small_image'] or None,
        'large_text': values['large_text'] or None,
        'small_text': values['small_text'] or None,
        'state': values['state'] or None,
        'details': values['details'] or None,
        'buttons': [],
        'start': time() if values['start'] else None
    }

    if values['label_1'] and values['url_1']:
        if is_url(values['url_1']):
            payload['buttons'].append({
                'label': values['label_1'],
                'url': values['url_1']
            })
        else:
            sg.popup_non_blocking(
                'Please enter a valid URL! Exemple: https://onetrickwolfy.me',
                title='Invalid URL',
                auto_close_duration=10,
                auto_close=True,
                keep_on_top=True
            )

    if values['label_2'] and values['url_2']:
        if is_url(values['url_2']):
            payload['buttons'].append({
                'label': values['label_2'],
                'url': values['url_2']
            })
        else:
            sg.popup_non_blocking(
                'Please enter a valid URL! Exemple: https://onetrickwolfy.me',
                title='Invalid URL',
                auto_close_duration=10,
                auto_close=True,
                keep_on_top=True
            )

    if(not payload['buttons']):
        payload['buttons'] = None

    return payload


# ---------------------------------------------------


sg.theme('dark purple 3')

layout = [
    [
        sg.Frame(
            title='Misc',
            layout=[
                [
                    sg.Text("State"),
                    sg.In(size=(40, 1), key="state", do_not_clear=True)
                ],
                [
                    sg.Text("Details"),
                    sg.Multiline(
                        key="details", focus=True, size=(
                            40, 3), do_not_clear=True)
                ],
                [
                    sg.Text("Count Time"),
                    sg.Checkbox(key="start", text='count time from now')
                ]
            ]
        )
    ],
    [
        sg.Frame(
            title='Texts',
            layout=[
                [
                    sg.Text("Large Text"),
                    sg.Multiline(
                        key="large_text",
                        focus=True,
                        size=(40, 3),
                        do_not_clear=True
                    )
                ],
                [
                    sg.Text("Small Text"),
                    sg.In(
                        size=(40, 1),
                        key="small_text",
                        do_not_clear=True
                    )
                ]
            ]
        )
    ],
    [
        sg.Frame(
            title='Images',
            layout=[
                [
                    sg.Text("Large Image"),
                    sg.In(size=(40, 1), key="large_image", do_not_clear=True)
                ],
                [
                    sg.Text("Small Image"),
                    sg.In(size=(40, 1), key="small_image", do_not_clear=True),
                ]
            ]
        )
    ],
    [
        sg.Frame(title='Button 1',
                 layout=[
                     [
                         sg.Text("Label"),
                         sg.In(size=(20, 1), key="label_1", do_not_clear=True)
                     ],
                     [
                         sg.Text("URL"),
                         sg.In(size=(20, 1), key="url_1", do_not_clear=True)
                     ]
                 ]
                 ),
        sg.Frame(title='Button 2',
                 layout=[
                     [
                         sg.Text("Label"),
                         sg.In(size=(20, 1), key="label_2", do_not_clear=True)
                     ],
                     [
                         sg.Text("URL"),
                         sg.In(size=(20, 1), key="url_2", do_not_clear=True)
                     ]
                 ]
                 )
    ],
    [
        sg.Button('Update', size=(25, 1.5)),
        sg.Button('Clear', size=(25, 1.5)),
        sg.Button('Open Template', key='open_template', size=(25, 1.5)),
        sg.Button('Save Template', key='save_template', size=(25, 1.5))
    ]
]

window = sg.Window(
    title="Rich Presence GUI",
    layout=layout,
    size=(800, 1200),
    grab_anywhere=False,
    font=('Helvetica', 12),
    no_titlebar=False,
    alpha_channel=1,
    keep_on_top=False,
    element_padding=(2, 3),
    resizable=False
)


# ---------------------------------------------------


while True:
    event, values = window.read(timeout=100)

    if event == 'Clear' or clear_requested:
        for key, value in saved_payload.items():
            if key == 'buttons':
                if not value:
                    window['url_1']('')
                    window['label_1']('')
                    window['url_2']('')
                    window['label_2']('')
                else:
                    if len(value) == 1:
                        window['url_1'](value[0]['url'])
                        window['label_1'](value[0]['label'])
                    elif len(value) == 2:
                        window['url_1'](value[1]['url'])
                        window['label_1'](value[1]['label'])
            elif key == 'start' and value:
                window[key](True)
            else:
                window[key](value or '')

            clear_requested = False

    if event == 'Update':
        saved_payload = update_payload(values, keys, window)
        RPC.update(**saved_payload)
        clear_requested = True

    if event == 'save_template':
        filename = sg.PopupGetFile(
            'Save Settings', 
            save_as = True, 
            no_window = True, 
            file_types=(
                ("Pickle", "*.pickle"),)
            )
        window.SaveToDisk(filename)
        window.save_to_disk(filename)

    if event == 'open_template':
        filename = sg.PopupGetFile(
            'Save Settings', 
            save_as = False, 
            no_window = True, 
            file_types = (
                ("Pickle", "*.pickle"),)
            )
        window.LoadFromDisk(filename)

    if event == 'Exit' or event == sg.WIN_CLOSED:
        break

    if (time() - last_update) > 15:
        RPC.update(**saved_payload)
        last_update = time()

window.close()
