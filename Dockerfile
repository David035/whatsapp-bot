# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo de requisitos primero para aprovechar el caché de capas de Docker.
COPY requirements.txt .

# Instala las dependencias principales.
# Esto asegura que Flask y Gunicorn estén instalados antes de intentar una reinstalación forzada de Vonage.
RUN pip install --no-cache-dir Flask==2.3.3 gunicorn

# --- PASO CLAVE PARA INTENTAR RESOLVER EL PROBLEMA DE VONAGE ---
# Desinstala cualquier versión existente de vonage (si la hay) y luego la reinstala
# forzosamente. Esto ayuda a limpiar cualquier posible corrupción o caché.
RUN pip uninstall -y vonage && pip install --no-cache-dir --force-reinstall vonage>=3.0.0

# Copia el resto de tu código de aplicación (main.py y otros archivos)
COPY . .

# Google Cloud Run inyecta la variable de entorno PORT.
# Tu aplicación debe escuchar en este puerto. Gunicorn lo recogerá automáticamente.
ENV PORT 8080

# Comando para ejecutar tu aplicación usando Gunicorn.
# 'main:main' significa: desde el archivo 'main.py', ejecuta el objeto Flask llamado 'main'.
# Asegúrate de que 'main' sea el nombre de tu archivo .py y 'main' sea el nombre de tu objeto Flask.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:main