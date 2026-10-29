# NeuroLab Enterprise — prototipo funcional simulado

NeuroLab es una interfaz web responsive para demostrar el flujo de trabajo de una plataforma de redes neuronales: login, carga de CSV, creación de proyectos, diseño de arquitecturas, simulación de entrenamientos, métricas, modelos y exportación de reportes.

> **Importante:** esta entrega es un prototipo simulado para demostración académica. Los datos de entrenamiento, la pérdida, la precisión y el tiempo se generan en el navegador; no se ejecuta TensorFlow ni se entrena una red neuronal real. Los metadatos de la demo se guardan en `localStorage` del navegador. No cargar datos confidenciales.

## 1. Requisitos

- Windows 10/11, macOS o Linux.
- Node.js 20 o superior y npm.
- Conexión a internet la primera vez para instalar dependencias.

## 2. Ejecutar en Visual Studio Code

1. Extrae el ZIP.
2. Abre la carpeta `neurolab-enterprise` en Visual Studio Code.
3. Abre **Terminal → Nueva terminal**.
4. Ejecuta:

```powershell
cd apps/web
npm install
npm run dev
```

5. Abre la URL local que Vite muestre, normalmente `http://localhost:5173`.

También puedes ejecutar `INICIAR_NEUROLAB.bat` desde la carpeta principal; este archivo inicia solo el frontend de la simulación.

## 3. Login de demostración

- **Correo:** `admin@neurolab.local`
- **Contraseña:** `NeuroLab2026!`

Las credenciales son fijas y están implementadas para la demo, no para proteger una aplicación pública.

## 4. Flujo principal

1. **Datasets:** sube un archivo `.csv`. El navegador lee su encabezado y cuenta las filas para mostrar un resumen. El contenido del archivo no se envía a un servidor; solo se conserva el nombre y los metadatos resumidos en el estado local.
2. **Proyectos:** crea un proyecto después de seleccionar un dataset. Selecciona la familia `Feedforward`, `RNN`, `CNN` o `GAN`.
3. **Diseñador de redes:** elige el proyecto, añade o elimina capas ocultas, cambia el número de neuronas y la activación por capa. Entrada y salida son configurables; la salida comienza con una neurona.
4. **Parámetros:** elige `Sigmoid`, `ReLU`, `Tanh`, `Softmax` o `Linear`; optimizador `Adam`, `SGD` o `RMSprop`; pérdida `binary_crossentropy`, `categorical_crossentropy` o `mse`; y número de épocas.
5. **Entrenamientos:** inicia la simulación y observa época, pérdida, precisión, tiempo transcurrido y progreso. Puedes pausar, reanudar, desactivar y eliminar ejecuciones.
6. **Modelos creados:** al completar una simulación se registra un modelo, que puedes activar o desactivar.
7. **Reportes:** descarga un resumen `.txt` o el historial de entrenamientos en `.csv`.
8. **Tema:** el botón de luna/sol cambia entre modo claro y oscuro. La preferencia queda guardada en el navegador.

## 5. Arquitectura del proyecto

```text
neurolab-enterprise/
├── apps/
│   └── web/
│       ├── src/
│       │   ├── App.tsx       # Vistas, estado, flujo y simulación (comentado por secciones)
│       │   ├── styles.css    # Diseño profesional responsive y tema claro/oscuro
│       │   └── main.tsx      # Punto de entrada React
│       ├── vercel.json       # Configuración de despliegue frontend en Vercel
│       ├── package.json      # Dependencias y comandos npm
│       └── index.html        # Documento HTML base
├── services/api/             # Base de API FastAPI de la versión de arquitectura
├── infra/postgres/schema.sql # Propuesta de esquema PostgreSQL
├── docs/
│   ├── IMPLEMENTACION.md     # Guía general de implementación
│   └── Documento_Maestro_NeuroLab_Enterprise_Semana_11.pdf
└── INICIAR_NEUROLAB.bat      # Inicia la demo del frontend en Windows
```

La UI de esta entrega funciona sin levantar `services/api`. La API, el esquema PostgreSQL y el documento maestro se conservan como referencia para la siguiente etapa. Para convertirlo en una plataforma real, se debe conectar el frontend a FastAPI, autenticar usuarios de forma segura, persistir datos en PostgreSQL, almacenar archivos y ejecutar entrenamientos en workers aislados.

## 6. Despliegue en Vercel

1. Sube la carpeta del proyecto a un repositorio Git.
2. En Vercel selecciona **Add New → Project** e importa el repositorio.
3. En **Root Directory** selecciona `apps/web`.
4. Vercel detectará Vite. Comprueba estos valores:
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`
5. Pulsa **Deploy**. `apps/web/vercel.json` incluye el fallback de rutas a `index.html`.

Este despliegue publica únicamente la interfaz simulada. No publica ni despliega automáticamente el backend FastAPI.

## 7. Estructura del código por secciones

`src/App.tsx` contiene comentarios de cabecera y separa la lógica en bloques funcionales:

- **Tipos y configuración:** `ModuleKey`, `Dataset`, `Project`, `Layer` y `Job` describen los datos que utiliza la interfaz.
- **Persistencia de demo:** `loadState`, `useEffect` y `localStorage` conservan el estado local.
- **Login:** valida las credenciales de demostración y abre el espacio de trabajo.
- **Dataset:** `uploadDataset` inspecciona el CSV local y registra sus metadatos.
- **Proyectos:** `createProject` asocia un dataset con una familia de red.
- **Arquitectura:** `addLayer`, `removeLayer`, `updateLayer` y `saveArchitecture` permiten editar capas y parámetros.
- **Simulación:** `startTraining` crea una ejecución; el temporizador avanza las épocas y genera valores ilustrativos de pérdida y precisión.
- **Administración de trabajos:** `updateJobStatus`, `deleteJob` y `exportJobs` pausan, reanudan, desactivan, eliminan y exportan ejecuciones.
- **Vistas de UI:** `Dashboard`, `Datasets`, `Projects`, `Architecture`, `Training`, `Models`, `Evaluation`, `Reports`, `Fundamentals` y `Admin` renderizan cada módulo.
- **Diseño responsive:** `styles.css` define la paleta, tarjetas, tablas, navegación móvil, media queries y variables para ambos temas.

## 8. Límites conocidos

- El login es de demostración y no ofrece seguridad real.
- El estado queda en el navegador y no se comparte entre usuarios ni dispositivos.
- La lectura CSV de esta demo asume encabezados sencillos separados por comas; no es un parser CSV completo.
- Las métricas y la duración son simuladas; no deben interpretarse como resultados científicos.
- La vista previa de arquitectura es conceptual, no un grafo ejecutable de TensorFlow/Keras.
