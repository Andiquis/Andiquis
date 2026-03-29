#!/bin/bash

# Leer cada línea del archivo y ejecutar code --install-extension
while read extension; do
    echo "Instalando $extension..."
    code --install-extension "$extension"
done < vscode-extensions-clean.txt

echo "¡Todas las extensiones fueron instaladas!"
