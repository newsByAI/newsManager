#!/bin/bash

# --- ⚙️ CONFIGURACIÓN ---
# Modifica estas variables con los datos de tu proyecto en Google Cloud.

# El ID de tu proyecto de GCP.
PROJECT_ID="enube-ai"

# La región de tu repositorio de Artifact Registry (ej. "us-central1").
REGION="us-central1"

# El nombre del repositorio que creaste en Artifact Registry.
REPOSITORY_NAME="news-repo"

# El nombre que quieres darle a la imagen de tu aplicación (ej. "backend-api", "frontend-app").
IMAGE_NAME="ai-backend"


# --- 📜 LÓGICA DEL SCRIPT ---

# Activa la salida de error para que el script se detenga si un comando falla.
set -e

cd "$(dirname "${BASH_SOURCE[0]}")"

echo "➡️ Iniciando el proceso de construcción y despliegue de la imagen..."

# 1. Validación de variables
if [[ -z "$PROJECT_ID" || -z "$REGION" || -z "$REPOSITORY_NAME" || -z "$IMAGE_NAME" ]]; then
  echo "❌ Error: Asegúrate de configurar las variables PROJECT_ID, REGION, REPOSITORY_NAME, y IMAGE_NAME en el script."
  exit 1
fi

# 2. Generación de tags
# Tag con la fecha y hora actual para tener un versionado único e inmutable.
TIMESTAMP_TAG=$(date +'%Y%m%d-%H%M%S')
# Tag 'latest' para apuntar siempre a la última versión subida.
LATEST_TAG="latest"

# 3. Construcción de la URL completa del repositorio de la imagen
IMAGE_URL_BASE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/${IMAGE_NAME}"
IMAGE_URL_TIMESTAMP="${IMAGE_URL_BASE}:${TIMESTAMP_TAG}"
IMAGE_URL_LATEST="${IMAGE_URL_BASE}:${LATEST_TAG}"

echo "   - URL base de la imagen: ${IMAGE_URL_BASE}"
echo "   - Tag de versión: ${TIMESTAMP_TAG}"

# 4. Autenticación de Docker con Artifact Registry
# Esto configura tu cliente Docker para que pueda conectarse a tu repositorio de GCP.
echo "🔑 Autenticando Docker con Google Artifact Registry..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet

# 5. Construcción de la imagen de Docker
# Se construye la imagen y se le aplica el tag del timestamp directamente.
echo "🚀 Construyendo la imagen de Docker..."
docker build -t "${IMAGE_URL_TIMESTAMP}" ..

# 6. Etiquetado de la imagen como 'latest'
# Se le añade un segundo tag ('latest') a la imagen que acabamos de construir.
echo "🏷️  Etiquetando la imagen construida como 'latest'..."
docker tag "${IMAGE_URL_TIMESTAMP}" "${IMAGE_URL_LATEST}"

# 7. Subida de las imágenes al repositorio
echo "⬆️  Subiendo la imagen con el tag '${TIMESTAMP_TAG}' al registro..."
docker push "${IMAGE_URL_TIMESTAMP}"

echo "⬆️  Actualizando el tag 'latest' en el registro..."
docker push "${IMAGE_URL_LATEST}"

echo ""
echo "✅ ¡Proceso completado con éxito!"
echo "-------------------------------------"
echo "Imagen subida con las siguientes etiquetas:"
echo "  - Versión única: ${IMAGE_URL_TIMESTAMP}"
echo "  - Última versión: ${IMAGE_URL_LATEST}"
echo "-------------------------------------"