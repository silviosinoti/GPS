import PySimpleGUI as sg
import telnetlib
from datetime import datetime

# 🎨 Tema
sg.theme('DarkBlue3')

# Configurações
USER = "configuration"
PASSWORD = "cond3e89"
PORT = 23

DISPOSITIVOS = {
    "WPP": "10.113.72.36",
    "WBT": "10.113.60.36",
    "WLI": "10.113.52.36",
    "WAN": "10.113.36.36",
    "WSC": "10.113.28.36",
    "WSA": "10.113.20.36",
    "WCO": "10.113.12.36",
    "WPA": "10.113.240.36",
}

MESES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
         "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def enviar_data(ip, data_str):
    try:
        tn = telnetlib.Telnet(ip, PORT, timeout=5)

        tn.read_until(b"login: ")
        tn.write(USER.encode() + b"\n")

        tn.read_until(b"Password: ")
        tn.write(PASSWORD.encode() + b"\n")

        tn.read_until(b">")

        comando = f"DATE {data_str}\n"
        tn.write(comando.encode())

        resposta = tn.read_until(b">", timeout=5).decode('ascii', errors='ignore')
        tn.close()

        return f"✅ {ip} atualizado com sucesso!\n{resposta}"

    except Exception as e:
        return f"❌ Erro no {ip}: {e}"


def montar_data(values):
    return f"{values['ANO']}-{values['MES']}-{int(values['DIA']):02d} " \
           f"{int(values['HORA']):02d}:{int(values['MIN']):02d}:{int(values['SEG']):02d}"


# Layout
layout = [

    [sg.Text("Selecionar Retificadora:"),
     sg.Combo(list(DISPOSITIVOS.keys()), key="EQUIP", size=(10,1))],

    [sg.Text("Ano:"), sg.Combo(list(range(2023, 2031)), key="ANO", size=(6,1)),
     sg.Text("Mês:"), sg.Combo(MESES, key="MES", size=(6,1)),
     sg.Text("Dia:"), sg.Combo(list(range(1, 32)), key="DIA", size=(4,1))],

    [sg.Text("Hora:"), sg.Combo(list(range(0,24)), key="HORA", size=(4,1)),
     sg.Text("Min:"), sg.Combo(list(range(0,60)), key="MIN", size=(4,1)),
     sg.Text("Seg:"), sg.Combo(list(range(0,60)), key="SEG", size=(4,1))],

    [
        sg.Button("Atualizar Data"),
        sg.Button("Usar Hora Atual"),
        sg.Button("Sair", button_color=('white','red'))
    ],

    [sg.Multiline(size=(70,10), key="OUTPUT")]
]

window = sg.Window("Atualizador de Data GPS Retificadoras", layout)

# Loop principal
while True:
    event, values = window.read()

    if event is None or event == "Sair":
        break

    # ✅ Preencher automaticamente com hora atual
    if event == "Usar Hora Atual":
        now = datetime.now()
        window["ANO"].update(now.year)
        window["MES"].update(now.strftime("%b"))
        window["DIA"].update(now.day)
        window["HORA"].update(now.hour)
        window["MIN"].update(now.minute)
        window["SEG"].update(now.second)

    # ✅ Atualizar data
    if event == "Atualizar Data":
        try:
            nome = values["EQUIP"]

            if not nome:
                window["OUTPUT"].update("⚠️ Selecione uma retificadora.")
                continue

            ip = DISPOSITIVOS[nome]
            data_str = montar_data(values)

            resultado = enviar_data(ip, data_str)

            # ✅ comportamento antigo (substitui texto)
            window["OUTPUT"].update(resultado)

        except Exception as e:
            window["OUTPUT"].update(f"Erro: {e}")

window.close()
