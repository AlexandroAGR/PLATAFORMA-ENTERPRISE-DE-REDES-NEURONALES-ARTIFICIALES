# NeuroLab Enterprise — guía de arquitectura y explicación del código

## Flujo de usuario

```text
LOGIN DE DEMOSTRACIÓN
        ↓
CARGAR DATASET CSV
        ↓
CREAR PROYECTO ASOCIADO A DATASET
        ↓
ELEGIR FAMILIA: Feedforward / RNN / CNN / GAN
        ↓
CONFIGURAR ENTRADA, CAPAS OCULTAS Y SALIDA
        ↓
ACTIVACIÓN + OPTIMIZADOR + FUNCIÓN DE PÉRDIDA + ÉPOCAS
        ↓
INICIAR SIMULACIÓN DE ENTRENAMIENTO
        ↓
MONITORIZAR ÉPOCA / PÉRDIDA / PRECISIÓN / TIEMPO
        ↓
REGISTRAR MODELO + EVALUAR + EXPORTAR CSV/REPORTE
```

## Estructura de datos

- `Dataset`: identifica un CSV y contiene nombre, cantidad de filas y columnas, tamaño y campos detectados.
- `Layer`: representa una capa editable con identificador, número de neuronas y función de activación.
- `Project`: vincula dataset, familia neuronal, capas y parámetros de entrenamiento.
- `Job`: representa una ejecución simulada y guarda estado, época, pérdida, precisión, tiempo y el historial que dibujan los gráficos.
- `ModuleKey`: limita la navegación a los módulos reconocidos por la interfaz.

## Lógica de los bloques principales

### Estado persistente
`loadState()` intenta leer el objeto de demostración desde `localStorage`. Si no existe o está dañado, devuelve el estado inicial con un dataset y un proyecto de ejemplo. Un `useEffect` vuelve a guardar el estado cuando cambia. Esto permite actualizar la página sin perder la demo en el mismo navegador.

### Carga de dataset
`uploadDataset()` toma el archivo del control de carga, verifica que tenga extensión `.csv`, lee el texto en el navegador y obtiene el encabezado y el número aproximado de filas. Solo registra metadatos; no envía el contenido a un servidor.

### Creación del proyecto
`createProject()` exige nombre y dataset. Crea un identificador, asocia el dataset, guarda la familia elegida y prepara una arquitectura inicial. En la versión real, este bloque se reemplazaría por `POST /api/v1/projects` y el servidor validaría la relación con el dataset.

### Diseñador de arquitectura
`addLayer()` añade una capa oculta. `removeLayer()` elimina la seleccionada. `updateLayer()` modifica sus neuronas o activación. `saveArchitecture()` guarda las capas y los hiperparámetros en el proyecto local. En producción, el endpoint de la API tendría que validar topología, dimensiones y compatibilidad de parámetros antes de aceptar la configuración.

### Simulación de entrenamiento
`startTraining()` crea un trabajo con estado `En ejecución`. Un intervalo actualiza la época, la pérdida, la precisión y el tiempo. Cuando la época actual alcanza el total configurado, cambia el estado a `Completado` y marca el modelo simulado como activo. No se ejecuta backpropagation ni un motor de ML.

### Estados

- `En ejecución`: el temporizador actualiza las métricas.
- `Pausado`: el temporizador deja de modificar esa ejecución y se puede reanudar.
- `Cancelado`: ejecución desactivada por el usuario.
- `Completado`: alcanzó todas las épocas; aparece en el registro de modelos.
- `Incompleto`: estado disponible en el filtro para una ampliación futura.

### Exportación CSV
`exportJobs()` construye una fila por entrenamiento, escapa comillas dobles y descarga un archivo `neurolab_entrenamientos.csv`. Se puede abrir con Excel o cualquier hoja de cálculo.

## Recomendaciones para explicar el proyecto

1. React divide la interfaz en componentes por módulo.
2. TypeScript define la estructura esperada de cada entidad y reduce errores de datos.
3. `useState` guarda la vista actual y el estado de los formularios.
4. `useEffect` persiste los cambios y ejecuta el reloj de la simulación.
5. `localStorage` se utiliza solo para que la demostración conserve su estado en un navegador.
6. Recharts representa curvas ilustrativas de pérdida y precisión.
7. Lucide React aporta iconos consistentes.
8. CSS usa variables para tema claro/oscuro y media queries para ajustar el diseño a móviles, tablets y escritorio.
9. Vercel despliega el frontend estático; FastAPI y PostgreSQL necesitarían despliegue separado para una solución real.
