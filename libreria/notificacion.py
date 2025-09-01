import sys
import os

def notificar_windows(titulo, mensaje):
    cmd = f'''
    powershell -Command " \
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null; \
    $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02); \
    $textNodes = $template.GetElementsByTagName('text'); \
    $textNodes.Item(0).AppendChild($template.CreateTextNode('{titulo}')) > $null; \
    $textNodes.Item(1).AppendChild($template.CreateTextNode('{mensaje}')) > $null; \
    $toast = [Windows.UI.Notifications.ToastNotification]::new($template); \
    $notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('Python'); \
    $notifier.Show($toast);"
    '''
    os.system(cmd)

def notificar_linux(titulo, mensaje):
    os.system(f'notify-send "{titulo}" "{mensaje}"')

def notificar_mac(titulo, mensaje):
    os.system(f'''osascript -e 'display notification "{mensaje}" with title "{titulo}"' ''')

def notificar(titulo, mensaje):
    if sys.platform.startswith("win"):
        notificar_windows(titulo, mensaje)
    elif sys.platform.startswith("linux"):
        notificar_linux(titulo, mensaje)
    elif sys.platform.startswith("darwin"):
        notificar_mac(titulo, mensaje)
    else:
        print(f"Notificación: {titulo} - {mensaje}")

if __name__ == "__main__":
    notificar("Prueba de Notificación", "Esta es una notificación de prueba.")