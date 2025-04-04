from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# from django.http import JsonResponse
# from comandos.ejecutor import ejecutar
from comandos.ejecutor import ejecutar_comando
from comandos.ejecutor import crear_carpeta
from comandos.ejecutor import crear_archivo
from bs4 import BeautifulSoup

import requests
import os
import subprocess
import time
import speech_recognition as sr
import webbrowser
import pyautogui
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
# from comandos.ejecutor import crear_archivo


# Configuración global
WHATSAPP_WAIT_TIME = 300  # Segundos máximos para cargar WhatsApp

def home(request):
    """Vista para la página principal"""
    return render(request, 'index.html')

@csrf_exempt
def escuchar(request):
    """Procesa comandos de voz"""
    if request.method == 'POST':
        try:
            # 1. Reconocimiento de voz
            r = sr.Recognizer()
            with sr.Microphone() as source:
                audio = r.listen(source, timeout=5)
            texto = r.recognize_google(audio, language="es-ES").lower()
            
            # 2. Ejecutar comando
            resultado = ejecutar_comando(texto)
            return JsonResponse({"status": resultado, "comando": texto})
            
        except sr.WaitTimeoutError:
            return JsonResponse({"error": "No se detectó voz"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Método no permitido"}, status=405)

def ejecutar_comando(accion: str) -> str:
    """Ejecuta todos los programas con manejo mejorado de WhatsApp"""
    accion = accion.lower()
    
    try:
        # WhatsApp con detección automática de contactos
        if "whatsapp" in accion:
            if "mensaje" in accion and ("a " in accion or "para " in accion):
                try:
                    # Extraer nombre y mensaje (ej: "mensaje a Romi: hola")
                    partes = accion.split("a") if "a " in accion else accion.split("para")
                    nombre_contacto = partes[-1].split(":")[0].strip()
                    mensaje = ":".join(partes[-1].split(":")[1:]).strip()
                    
                    # Configuración de Selenium
                    options = webdriver.ChromeOptions()
                    options.add_argument("user-data-dir=C:\\Path\\To\\Your\\Chrome\\Profile")  # ¡Importante!
                    driver = webdriver.Chrome(options=options)
                    
                    driver.get("https://web.whatsapp.com")
                    
                    try:
                        # Espera a que cargue la lista de chats
                        WebDriverWait(driver, WHATSAPP_WAIT_TIME).until(
                            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
                        )
                        
                        # Buscar contacto
                        search_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
                        search_box.click()
                        search_box.send_keys(nombre_contacto)
                        time.sleep(2)
                        
                        # Hacer clic en el contacto (versión resistente)
                        try:
                            driver.find_element(By.XPATH, f'//span[@title="{nombre_contacto}"]').click()
                        except:
                            # Intento alternativo de coincidencia parcial
                            driver.find_element(By.XPATH, '//span[contains(@title, "{}")]'.format(nombre_contacto)).click()
                        
                        # Enviar mensaje
                        input_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="1"]')
                        input_box.send_keys(mensaje)
                        pyautogui.press('enter')
                        
                        driver.quit()
                        return f"📤 Mensaje enviado a {nombre_contacto.capitalize()}"
                        
                    except TimeoutException:
                        driver.quit()
                        return "⚠️ WhatsApp no cargó a tiempo. ¿Estás conectado?"
                        
                except Exception as e:
                    return f"❌ Error WhatsApp: {str(e)}"
            
            # Solo abrir WhatsApp
            webbrowser.open("https://web.whatsapp.com")
            return "📱 WhatsApp Web abierto"
        
        # Comandos directos web
        elif "youtube" in accion:
            webbrowser.open("https://www.youtube.com")
            return "📺 YouTube abierto"

        elif "gmail" in accion or "correo" in accion:
            webbrowser.open("https://mail.google.com")
            return "📧 Gmail abierto"

        elif "wikipedia" in accion:
            webbrowser.open("https://www.wikipedia.org")
            return "🌐 Wikipedia abierta"

        elif "linkedin" in accion:
            webbrowser.open("https://www.linkedin.com")
            return "🔗 LinkedIn abierto"

        elif "noticias" in accion:
            webbrowser.open("https://www.google.com/search?q=noticias")
            return "📰 Noticias abiertas"

        elif "netflix" in accion:
            webbrowser.open("https://www.netflix.com")
            return "🍿 Netflix abierto (todo sea por la ciencia)"
        
        elif "flow" in accion:
            webbrowser.open("https://portal.app.flow.com.ar/inicio")
            return "🍿 Flow abierto"

        elif "disney" in accion:
            webbrowser.open("https://www.disneyplus.com/es-419/home")
            return "🍿 Disney + abierto"

        elif "max" in accion:
            webbrowser.open("https://play.max.com/")
            return "🍿 Max abierto"
        
        elif "facebook" in accion:
            webbrowser.open("https://www.facebook.com/")
            return "📘 Abriendo Facebook"

        elif "instagram" in accion:
            webbrowser.open("https://www.instagram.com/")
            return "📸 Abriendo Instagram"

        elif "pinterest" in accion:
            webbrowser.open("https://www.pinterest.com/")
            return "📌 Abriendo Pinterest"

        elif "x" in accion or "twitter" in accion:
            webbrowser.open("https://twitter.com/")  # X es el nuevo Twitter
            return "🐦 Abriendo X (Twitter)"

        elif "reddit" in accion:
            webbrowser.open("https://www.reddit.com/r/argentina/")
            return "👽 Abriendo Reddit Argentina"

        elif "buscar" in accion and "en google" in accion:
            query = accion.replace("buscar", "").replace("en google", "").strip()
            if query:
                webbrowser.open(f"https://www.google.com/search?q={query}")
                return f"🔎 Buscando '{query}' en Google"
            else:
                return "❓ ¿Qué querés buscar en Google?"

        elif "reproducir" in accion and "en youtube" in accion:
            video = accion.replace("reproducir", "").replace("en youtube", "").strip()
            if video:
                search_url = f"https://www.youtube.com/results?search_query={video}"
                webbrowser.open(search_url + "&sp=EgIQAQ%253D%253D")  # Filtra solo videos y abre el primero
                return f"▶️ Reproduciendo '{video}' en YouTube"
            else:
                return "🎵 ¿Qué querés reproducir en YouTube?"
        
        

        elif "crear evento" in accion or "evento en calendario" in accion:
            webbrowser.open("https://calendar.google.com/calendar/r/eventedit")
            return "📅 Página para crear evento en Google Calendar abierta"
           
        # Comandos existentes mejorados
        elif "chrome" in accion:
            os.system('start chrome --new-window')
            return "✅ Chrome abierto"
            
        elif "spotify" in accion:
            try:
                spotify_path = os.path.join(os.environ['APPDATA'], 'Spotify', 'Spotify.exe')
                subprocess.Popen([spotify_path], shell=True)
                time.sleep(2)
                procesos = subprocess.check_output('tasklist', shell=True).decode()
                return "🎵 Spotify abierto" if "Spotify.exe" in procesos else "⚠️ Spotify no se detectó"
            except:
                os.system('start spotify://')
                return "🌐 Spotify Web abierto"
            
        elif "calculadora" in accion:
            os.system('calc')
            return "🧮 Calculadora abierta"
            
        elif "bloc de notas" in accion:
            os.system('notepad')
            return "📝 Bloc de notas listo"
            
        elif "cerrar" in accion:
            programa = accion.split("cerrar")[-1].strip()
            if "chrome" in programa:
                os.system('taskkill /im chrome.exe /f')
                return "🛑 Chrome cerrado"
            elif "spotify" in programa:
                os.system('taskkill /im spotify.exe /f')
                return "🛑 Spotify cerrado"
            else:
                return "⚠️ Programa no reconocido para cerrar"
        
        
        elif "crear carpeta" in accion:
            nombre_carpeta = accion.replace("crear carpeta", "").strip()
            return crear_carpeta(nombre_carpeta)

        elif "crear archivo" in accion:
            nombre_archivo = accion.replace("crear archivo", "").strip()
            return crear_archivo(nombre_archivo)
        
        elif "youtube" in accion:
            webbrowser.open("https://www.youtube.com")
            return "📺 YouTube abierto"

        elif "gmail" in accion or "correo" in accion:
            webbrowser.open("https://mail.google.com")
            return "📧 Gmail abierto"

        elif "wikipedia" in accion:
            webbrowser.open("https://www.wikipedia.org")
            return "🌐 Wikipedia abierta"

        
    except Exception as e:
        return f"❌ Error: {str(e)}"
    
    return "⚠️ Comando no reconocido"



def ejecutar_accion(request, accion):
    resultado = ejecutar_comando(accion)
    return JsonResponse({"mensaje": resultado})

# from django.shortcuts import render
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# import os
# import time
# import webbrowser
# import speech_recognition as sr
# import pyautogui
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException
# from selenium.webdriver.chrome.options import Options

# # Configuración de Chrome
# WHATSAPP_WAIT_TIME = 10  # Tiempo máximo de espera para WhatsApp Web
# CHROME_PROFILE_PATH = "C:\\chrome_selenium"  # Ruta del perfil de usuario
# REMOTE_DEBUGGING_PORT = "9222"

# def home(request):
#     """Vista para la página principal"""
#     return render(request, 'index.html')

# @csrf_exempt
# def escuchar(request):
#     """Procesa comandos de voz"""
#     if request.method == 'POST':
#         try:
#             recognizer = sr.Recognizer()
#             with sr.Microphone() as source:
#                 audio = recognizer.listen(source, timeout=5)
#             texto = recognizer.recognize_google(audio, language="es-ES").lower()
            
#             resultado = ejecutar_comando(texto)
#             return JsonResponse({"status": resultado, "comando": texto})
#         except sr.WaitTimeoutError:
#             return JsonResponse({"error": "No se detectó voz"}, status=400)
#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=500)
#     return JsonResponse({"error": "Método no permitido"}, status=405)

# def ejecutar_comando(accion: str) -> str:
#     """Ejecuta comandos como abrir WhatsApp o enviar mensajes"""
#     accion = accion.lower()
    
#     try:
#         if "whatsapp" in accion:
#             if "mensaje" in accion and ("a " in accion or "para " in accion):
#                 return enviar_mensaje_whatsapp(accion)
            
#             webbrowser.open("https://web.whatsapp.com")
#             return "📱 WhatsApp Web abierto"
#     except Exception as e:
#         return f"❌ Error: {str(e)}"
    
#     return "⚠️ Comando no reconocido"

# def enviar_mensaje_whatsapp(accion: str) -> str:
#     """Envía un mensaje en WhatsApp Web usando la sesión activa"""
#     try:
#         # Extraer nombre y mensaje
#         partes = accion.replace("mensaje a", "mensaje para").split("para")
#         if len(partes) < 2:
#             return "⚠️ Formato incorrecto. Usa 'mensaje para [nombre]: [mensaje]'"
        
#         datos_contacto = partes[1].strip().split(":")
#         if len(datos_contacto) < 2:
#             return "⚠️ Falta el mensaje después de ':'"
        
#         nombre_contacto = datos_contacto[0].strip()
#         mensaje = datos_contacto[1].strip()
        
#         # Configurar Selenium
#         options = Options()
#         options.debugger_address = f"127.0.0.1:{REMOTE_DEBUGGING_PORT}"
#         driver = webdriver.Chrome(options=options)
#         driver.get("https://web.whatsapp.com")
        
#         # Esperar que WhatsApp cargue
#         try:
#             WebDriverWait(driver, WHATSAPP_WAIT_TIME).until(
#                 EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
#             )
#         except TimeoutException:
#             return "⚠️ WhatsApp no cargó a tiempo. Verifica la conexión."

#         # Buscar el contacto
#         search_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
#         search_box.click()
#         search_box.clear()
#         search_box.send_keys(nombre_contacto)
#         time.sleep(2)
        
#         try:
#             driver.find_element(By.XPATH, f'//span[@title="{nombre_contacto}"]').click()
#         except NoSuchElementException:
#             return f"⚠️ No se encontró el contacto: {nombre_contacto}"
        
#         # Enviar el mensaje
#         try:
#             input_box = WebDriverWait(driver, 5).until(
#                 EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="1"]'))
#             )
#             input_box.send_keys(mensaje)
#             pyautogui.press('enter')
#             return f"📤 Mensaje enviado a {nombre_contacto.capitalize()}"
#         except TimeoutException:
#             return "⚠️ No se pudo encontrar el campo de mensaje."
#     except Exception as e:
#         return f"❌ Error en WhatsApp: {str(e)}"
