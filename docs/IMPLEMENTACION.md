# Guía de implementación por fases

1. **Base de plataforma:** configurar React, API, autenticación, PostgreSQL y CRUD de proyectos.
2. **Arquitecturas:** validar familias, formas de entrada/salida, capas y parámetros en backend.
3. **Entrenamiento:** incorporar cola de trabajos y workers aislados con TensorFlow/Keras.
4. **Tiempo real y evaluación:** persistir estados y métricas; publicar eventos por SSE/WebSocket.
5. **Registro y reportes:** guardar versiones inmutables, comparar ejecuciones y exportar CSV/PDF.
6. **Endurecimiento:** pruebas de seguridad, límites de CPU/memoria, observabilidad, backups y CI/CD.

## Estados de entrenamiento recomendados
`QUEUED → PREPARING → RUNNING → COMPLETED | FAILED | CANCELLED`

## Criterio de MVP del documento
Usuario autenticado crea proyecto, configura una red Feedforward, selecciona dataset de prueba, inicia entrenamiento real TensorFlow/Keras, visualiza estado y métricas sin recargar, consulta resultados y conserva la versión del modelo con trazabilidad.
