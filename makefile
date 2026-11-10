PYTHON = python
SRC_DIR = src
DATA_DB = data/semaforos.db
DATA_PROCESS = data/process

.PHONY: help setup db analyze check-pk clean all

help:
	@echo "Comandos disponibles:"
	@echo "  make setup    - Instala las dependencias del proyecto"
	@echo "  make db       - Carga el CSV original a la base de datos SQLite"
	@echo "  make analyze  - Ejecuta el analisis y genera los graficos"
	@echo "  make check-pk - Ejecuta el script para verificar la Primary Key"
	@echo "  make clean    - Elimina los archivos generados (db, txt, png)"
	@echo "  make all      - Ejecuta setup, db y analyze en secuencia"

setup:
	@echo "Instalando dependencias..."
	$(PYTHON) -m pip install -r requirements.txt

db:
	@echo "Cargando datos a SQLite..."
	$(PYTHON) $(SRC_DIR)/cargar_datos.py

analyze:
	@echo "Ejecutando analisis y generando graficos..."
	$(PYTHON) $(SRC_DIR)/analisis_semaforos.py

check-pk:
	@echo "Verificando Primary Key..."
	$(PYTHON) comprobacion_pk.py

clean:
	@echo "Limpiando archivos generados..."
	rm -f $(DATA_DB)
	rm -f $(DATA_PROCESS)/*.png
	rm -f $(DATA_PROCESS)/*.txt

all: setup db analyze