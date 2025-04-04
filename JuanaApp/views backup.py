from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
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
            
    except Exception as e:
        return f"❌ Error: {str(e)}"
    
    return "⚠️ Comando no reconocido"