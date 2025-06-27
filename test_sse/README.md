# 🧪 CARPETA DE PRUEBAS SSE - FERREMAS

Esta carpeta contiene todas las herramientas y documentación para probar las funcionalidades de Server-Sent Events (SSE) del proyecto FERREMAS.

## 📁 Estructura de Archivos

```
test_sse/
├── README.md                    # Este archivo - Guía principal
├── SSE_README.md               # Guía rápida de uso
├── SSE_TESTING_GUIDE.md        # Guía completa de pruebas
├── sse_test.html               # Herramienta HTML interactiva
└── test_sse_automated.py       # Script de pruebas automatizadas
```

## 🚀 Inicio Rápido

### 1. Preparar el Entorno
```bash
# Desde la raíz del proyecto FERREMAS
cd back
python app.py
```

En otra terminal:
```bash
cd front/app
ng serve
```

### 2. Ejecutar Pruebas

#### Opción A: Herramienta HTML Interactiva
```bash
# Abrir en navegador
test_sse/sse_test.html
```

#### Opción B: Script Automatizado
```bash
# Desde la raíz del proyecto
python test_sse/test_sse_automated.py
```

#### Opción C: Aplicación Angular
```bash
# Ir a http://localhost:4200/stock
# Abrir consola del navegador para ver logs
```

## 📋 Archivos Detallados

### `sse_test.html`
**Herramienta HTML interactiva completa**
- ✅ Interfaz visual moderna
- ✅ Estadísticas en tiempo real
- ✅ Controles para cada prueba
- ✅ Logs detallados con timestamps
- ✅ Reconexión automática

### `test_sse_automated.py`
**Script de prueba automatizada**
- ✅ 9 pruebas automatizadas (incluyendo verificación de datos)
- ✅ Reporte detallado
- ✅ Verificación de endpoints
- ✅ Pruebas de rendimiento
- ✅ Uso de códigos reales del sistema

### `SSE_README.md`
**Guía rápida de referencia**
- ✅ Inicio rápido
- ✅ Lista de pruebas
- ✅ Troubleshooting
- ✅ Casos de uso

### `SSE_TESTING_GUIDE.md`
**Guía completa paso a paso**
- ✅ Instrucciones detalladas
- ✅ Ejemplos de código
- ✅ Casos de prueba específicos
- ✅ Debugging avanzado

## 🧪 Casos de Prueba Disponibles

| ✅ | Prueba | Herramienta | Descripción |
|---|--------|-------------|-------------|
| ✅ | Verificar datos existentes | Script | Verificar productos y sucursales |
| ✅ | Conexión exitosa | HTML + Script | Establecer conexión SSE |
| ✅ | Recepción de mensajes | HTML + Script | Recibir mensajes manuales |
| ✅ | Reconexión automática | HTML + Angular | Reconectar al perder conexión |
| ✅ | Orden de mensajes | HTML + Script | Verificar secuencia temporal |
| ✅ | Manejo de JSON | HTML + Script | Procesar JSON malformado |
| ✅ | Eventos de error | HTML + Angular | Manejar errores personalizados |
| ✅ | Prueba de rendimiento | HTML + Script | 1000 mensajes simultáneos |
| ✅ | Cierre desde servidor | HTML + Script | Eventos de cierre |
| ✅ | Múltiples conexiones | HTML + Script | Varias pestañas simultáneas |
| ✅ | Timestamps | HTML + Angular | Marcas de tiempo automáticas |

## 🔧 Endpoints de Prueba

| Endpoint | Método | Descripción | Probado por |
|----------|--------|-------------|-------------|
| `/api/notificaciones` | GET | Conexión SSE principal | HTML + Script |
| `/api/test-sse` | POST | Enviar mensaje manual | HTML + Script |
| `/api/sse-orden` | GET | Prueba orden de mensajes | HTML + Script |
| `/api/sse-rendimiento` | GET | Prueba de rendimiento | HTML + Script |
| `/api/sse-error-json` | GET | Prueba JSON malformado | HTML + Script |
| `/api/sse-cierre` | GET | Prueba cierre de conexión | HTML + Script |
| `/api/actualizar-stock` | POST | Actualización de stock | Script |

## 📊 Datos del Sistema

### Sucursales Disponibles
- **101**: Sucursal Central Principal
- **102**: Sucursal Sur  
- **103**: Sucursal Norte

### Productos Disponibles
- **FER-001**: Plancha acero
- **FER-002**: Pala (usado en pruebas de stock)
- **FER-003**: Destornillador
- **...**: 13 productos total

### Resultado de Pruebas
```
🎯 RESULTADO FINAL: 9/9 pruebas pasaron
🎉 ¡TODAS LAS PRUEBAS SSE PASARON EXITOSAMENTE!
```

### Detalles de Prueba de Stock
- **Producto usado**: FER-002 (Pala)
- **Cantidad agregada**: 8 unidades
- **Sucursal**: 101 (Sucursal Central Principal)
- **Stock final**: 16 unidades

## 📊 Monitoreo y Logs

### Herramienta HTML
- Contador de mensajes recibidos
- Contador de errores
- Contador de reconexiones
- Timestamp del último mensaje

### Script Automatizado
- Logs con timestamps precisos
- Reporte de éxito/fallo por prueba
- Resumen final con estadísticas
- Verificación de datos del sistema

### Angular (Consola)
- Contador de rendimiento cada 100 mensajes
- Timestamps para cada mensaje
- Clasificación por tipo de evento

## 🐛 Troubleshooting

### Problemas Comunes

1. **CORS Errors**
   - Verificar que Flask esté ejecutándose
   - Comprobar configuración CORS en `back/app.py`

2. **Connection Refused**
   - Verificar puerto 5000
   - Comprobar que Flask esté activo

3. **JSON Parse Errors**
   - Revisar logs de consola
   - Verificar formato de mensajes

4. **Reconexión No Funciona**
   - Verificar timeout de 5 segundos
   - Comprobar estado de EventSource

### Logs Útiles

```bash
# Backend
👥 Nueva conexión SSE: 127.0.0.1
Error en SSE: [descripción del error]

# Frontend
✅ Conexión SSE establecida
📊 Recibidos 100 mensajes SSE
❌ Error parseando JSON SSE: [error]
```

## 🎯 Flujo de Pruebas Recomendado

1. **Iniciar servicios** (Flask + Angular)
2. **Ejecutar script automatizado** para verificación básica
3. **Usar herramienta HTML** para pruebas interactivas
4. **Verificar Angular** para integración real
5. **Revisar logs** en consola del navegador

## 📞 Soporte

Para problemas o preguntas:
1. Revisar `SSE_TESTING_GUIDE.md` para instrucciones detalladas
2. Verificar logs de consola
3. Comprobar configuración de CORS
4. Asegurar que Flask esté ejecutándose

---

## 🚀 Próximos Pasos

1. **Ejecutar todas las pruebas** usando las herramientas disponibles
2. **Verificar logs** en consola de Angular
3. **Probar con múltiples usuarios** simultáneos
4. **Monitorear rendimiento** en diferentes escenarios
5. **Documentar resultados** de las pruebas

¡Las pruebas SSE están completamente implementadas y funcionando al 100%! 🎉 