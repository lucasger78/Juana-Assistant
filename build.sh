#!/usr/bin/env bash
apt-get update && apt-get install -y \
    portaudio19-dev \
    libasound2-dev \
    libjack-dev \
    libpulse-dev \
    libffi-dev  # Agrega dependencias adicionales necesarias para compilar PyAudio

pip install --upgrade pip setuptools wheel  # Asegura que pip está actualizado
pip install -r requirements.txt  # Luego instala las dependencias
