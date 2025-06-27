# 🧪 PRUEBAS SSE - FERREMAS

## 📁 Ubicación de Pruebas

Todas las herramientas y documentación de pruebas SSE se encuentran organizadas en la carpeta:

```
test_sse/
├── README.md                    # Guía principal
├── SSE_README.md               # Guía rápida de uso
├── SSE_TESTING_GUIDE.md        # Guía completa de pruebas
├── sse_test.html               # Herramienta HTML interactiva
└── test_sse_automated.py       # Script de pruebas automatizadas
```

## 🚀 Ejecución Rápida (DESDE LA RAÍZ DEL PROYECTO)

### ⚡ Opción 1: Scripts Automáticos (Recomendado)

**Windows:**
```bash
# Hacer doble clic en el archivo o ejecutar:
ejecutar_pruebas_sse.bat
```

**Linux/Mac:**
```bash
# Dar permisos y ejecutar:
chmod +x ejecutar_pruebas_sse.sh
./ejecutar_pruebas_sse.sh
```

### ⚡ Opción 2: Comandos Manuales

**Script automatizado:**
```bash
# Desde la raíz del proyecto FERREMAS
python test_sse/test_sse_automated.py
```

**Herramienta HTML:**
```bash
# Abrir en navegador (ruta relativa desde la raíz):
test_sse/sse_test.html
```

### ⚡ Opción 3: Navegación Directa

1. **Ir a la carpeta de pruebas**: `cd test_sse`
2. **Ver documentación**: `README.md`
3. **Ejecutar script**: `python test_sse_automated.py`
4. **Abrir HTML**: `sse_test.html`

## 📋 Resumen de Pruebas Implementadas

| ✅ | Prueba | Estado | Herramienta |
|---|--------|--------|-------------|
| ✅ | Verificar datos existentes | Implementada | Script |
| ✅ | Conexión exitosa | Implementada | HTML + Script |
| ✅ | Recepción de mensajes | Implementada | HTML + Script |
| ✅ | Reconexión automática | Implementada | HTML + Angular |
| ✅ | Orden de mensajes | Implementada | HTML + Script |
| ✅ | Manejo de JSON | Implementada | HTML + Script |
| ✅ | Eventos de error | Implementada | HTML + Angular |
| ✅ | Prueba de rendimiento | Implementada | HTML + Script |
| ✅ | Cierre desde servidor | Implementada | HTML + Script |
| ✅ | Múltiples conexiones | Implementada | HTML + Script |
| ✅ | Timestamps | Implementada | HTML + Angular |

## 🛠️ Herramientas Disponibles

1. **Herramienta HTML Interactiva** (`test_sse/sse_test.html`)
   - Interfaz visual completa
   - Estadísticas en tiempo real
   - Controles para cada prueba

2. **Script Automatizado** (`test_sse/test_sse_automated.py`)
   - 9 pruebas automatizadas
   - Reporte detallado
   - Verificación de endpoints
   - Uso de códigos reales del sistema

3. **Componente Angular** (`front/app/src/app/stock/stock.component.ts`)
   - Integración con aplicación real
   - Manejo de errores robusto
   - Contador de rendimiento

## 🔧 Endpoints de Prueba

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/notificaciones` | GET | Conexión SSE principal |
| `/api/test-sse` | POST | Enviar mensaje manual |
| `/api/sse-orden` | GET | Prueba orden de mensajes |
| `/api/sse-rendimiento` | GET | Prueba de rendimiento |
| `/api/sse-error-json` | GET | Prueba JSON malformado |
| `/api/sse-cierre` | GET | Prueba cierre de conexión |
| `/api/actualizar-stock` | POST | Actualización de stock |

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

### Detalles de Prueba de Stock
- **Producto usado**: FER-002 (Pala)
- **Cantidad agregada**: 8 unidades
- **Sucursal**: 101 (Sucursal Central Principal)
- **Stock final**: 16 unidades

## ⚠️ Requisitos Previos

Antes de ejecutar las pruebas, asegúrate de:

1. **Backend ejecutándose:**
   ```bash
   cd back
   python app.py
   ```

2. **Frontend ejecutándose (opcional):**
   ```bash
   cd front/app
   ng serve
   ```

## 🎯 Flujo de Pruebas Recomendado

1. **Iniciar servicios** (Flask + Angular)
2. **Ejecutar script automatizado** para verificación básica
3. **Usar herramienta HTML** para pruebas interactivas
4. **Verificar Angular** para integración real
5. **Revisar logs** en consola del navegador

## ✅ Resultado Esperado

```
🎯 RESULTADO FINAL: 9/9 pruebas pasaron
🎉 ¡TODAS LAS PRUEBAS SSE PASARON EXITOSAMENTE!
```

## 🐛 Solución de Problemas

### Error: "No se puede encontrar el archivo"
- **Solución**: Asegúrate de estar en la raíz del proyecto FERREMAS
- **Verificar**: `dir` (Windows) o `ls` (Linux/Mac) debe mostrar la carpeta `test_sse`

### Error: "Módulo no encontrado"
- **Solución**: Instalar dependencias: `pip install requests`

### Error: "Connection refused"
- **Solución**: Verificar que Flask esté ejecutándose en puerto 5000

---

## 📞 Soporte

Para problemas o preguntas sobre las pruebas SSE:
1. Revisar `test_sse/README.md` para instrucciones detalladas
2. Verificar logs de consola
3. Comprobar configuración de CORS
4. Asegurar que Flask esté ejecutándose

---

📚 **Para información detallada, consulta la carpeta [test_sse/](test_sse/)** 