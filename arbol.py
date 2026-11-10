from pathlib import Path

# Carpetas y archivos a ignorar
ignorar = {'.semaforos314', '__pycache__', '.git', '.vscode', '.venv'}

def generar_arbol(ruta, prefijo=""):
    # Filtramos los elementos ignorados y ordenamos
    elementos = sorted([e for e in ruta.iterdir() if e.name not in ignorar])
    
    for i, elemento in enumerate(elementos):
        # Determinamos si es el último para dibujar las líneas correctamente
        conector = "└── " if i == len(elementos) - 1 else "├── "
        print(prefijo + conector + elemento.name)
        
        if elemento.is_dir():
            # Recursión para carpetas
            nuevo_prefijo = prefijo + ("    " if i == len(elementos) - 1 else "│   ")
            generar_arbol(elemento, nuevo_prefijo)

print(".")
generar_arbol(Path("."))