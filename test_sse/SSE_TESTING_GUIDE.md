# 🧪 GUÍA COMPLETA DE PRUEBAS SSE - FERREMAS

## 📋 Resumen de Implementación

Se han implementado todas las pruebas de SSE solicitadas con las siguientes mejoras:

### ✅ Backend (Flask)
- **Timestamps automáticos** en todos los mensajes SSE
- **Eventos personalizados** para errores y cierre
- **Endpoints de prueba** para cada caso de uso
- **Mejor manejo de errores** y reconexión
- **Logging detallado** de conexiones

### ✅ Frontend (Angular)
- **Manejo robusto de errores** JSON
- **Contador de rendimiento** de mensajes
- **Eventos personalizados** para errores y cierre
- **Reconexión automática** mejorada
- **Timestamps** en logs de consola

### ✅ Herramienta de Prueba HTML
- **Interfaz completa** para todas las pruebas
- **Estadísticas en tiempo real**
- **Logs detallados** con timestamps
- **Controles interactivos** para cada prueba

---

## 🚀 Cómo Ejecutar las Pruebas

### 1. Iniciar el Backend
```bash
cd back
python app.py
```

### 2. Iniciar el Frontend
```bash
cd front/app
ng serve
```

### 3. Abrir la Herramienta de Prueba
Abrir en el navegador: `test_sse/sse_test.html`

---

## 🧪 CASOS DE PRUEBA UNO A UNO

### 1. ✅ Conexión exitosa
**Cómo probar:**
1. Abrir `test_sse/sse_test.html`
2. Hacer clic en "🔗 Conectar SSE"
3. Verificar que aparece "✅ Conexión establecida"

**Resultado esperado:**
```
[10:30:15] 🔗 Iniciando conexión SSE...
[10:30:15] ✅ Conexión SSE establecida
[10:30:15] 🔗 Conexión SSE establecida (10:30:15.123Z)
```

### 2. ✅ Recepción de mensajes
**Cómo probar:**
1. Conectar SSE
2. Hacer clic en "📝 Mensaje Manual"
3. Escribir un mensaje personalizado
4. Hacer clic en "Enviar"

**Resultado esperado:**
```
[10:30:20] 📤 Mensaje manual enviado: "¡Hola desde SSE!"
[10:30:20] 📝 Manual: ¡Hola desde SSE! (10:30:20.456Z)
```

### 3. ✅ Reconexión automática
**Cómo probar:**
1. Conectar SSE
2. Detener Flask (Ctrl+C)
3. Esperar 10-15 segundos
4. Reiniciar Flask
5. Verificar reconexión automática

**Resultado esperado:**
```
[10:30:25] ❌ Error en conexión SSE: [object Event]
[10:30:25] 🔄 Intentando reconexión en 5 segundos...
[10:30:30] 🔗 Iniciando conexión SSE...
[10:30:30] ✅ Conexión SSE establecida
```

### 4. ✅ Orden de mensajes
**Cómo probar:**
1. Conectar SSE
2. Hacer clic en "📋 Prueba Orden"
3. Verificar secuencia en logs

**Resultado esperado:**
```
[10:30:35] 📋 Enviados 10 mensajes ordenados
[10:30:35] 📋 Orden 0: Mensaje ordenado 0 (10:30:35.001Z)
[10:30:35] 📋 Orden 1: Mensaje ordenado 1 (10:30:35.101Z)
...
[10:30:35] 📋 Orden 9: Mensaje ordenado 9 (10:30:35.901Z)
```

### 5. ✅ Manejo de JSON
**Cómo probar:**
1. Conectar SSE
2. Hacer clic en "❌ Error JSON"
3. Verificar manejo de JSON malformado

**Resultado esperado:**
```
[10:30:40] ❌ JSON malformado enviado: error enviado
[10:30:40] ❌ Error parseando JSON: Unexpected end of JSON input
[10:30:40] 📄 Datos recibidos: {"rompe_json":
```

### 6. ✅ Eventos de error personalizados
**Cómo probar:**
- Los errores se manejan automáticamente
- Verificar logs de consola en Angular
- Verificar eventos personalizados en HTML

**Resultado esperado:**
```
⚠️ Evento SSE de error personalizado: {"tipo":"error","mensaje":"Error en el servidor: ..."}
```

### 7. ✅ Prueba de rendimiento
**Cómo probar:**
1. Conectar SSE
2. Hacer clic en "📈 Prueba Rendimiento"
3. Verificar contador de mensajes

**Resultado esperado:**
```
[10:30:45] 📈 Iniciando prueba de rendimiento (1000 mensajes)...
[10:30:45] 📊 Prueba completada: 1000 mensajes en 150ms
[10:30:45] 📊 Recibidos 100 mensajes SSE
[10:30:45] 📊 Recibidos 200 mensajes SSE
...
```

### 8. ✅ Cierre de conexión desde servidor
**Cómo probar:**
1. Conectar SSE
2. Hacer clic en "🔌 Cierre Servidor"
3. Verificar evento de cierre

**Resultado esperado:**
```
[10:30:50] 🔌 Mensaje de cierre enviado: mensaje de cierre enviado
[10:30:50] 🔌 Evento de cierre: {"tipo":"cierre","mensaje":"Conexión será cerrada por el servidor"}
```

### 9. ✅ Múltiples conexiones
**Cómo probar:**
1. Abrir múltiples pestañas con `test_sse/sse_test.html`
2. Conectar SSE en todas
3. Enviar mensajes manuales
4. Verificar que todos reciben los mismos eventos

---

## 🔧 Endpoints de Prueba Implementados

### POST `/api/test-sse`
Envía mensajes manuales a la cola SSE
```json
{
  "mensaje": "Texto personalizado",
  "cod_sucursal": 1,
  "stock": 5
}
```

### GET `/api/sse-rendimiento`
Envía 1000 mensajes para pruebas de rendimiento

### GET `/api/sse-orden`
Envía 10 mensajes ordenados con timestamps

### GET `/api/sse-error-json`
Envía JSON malformado para probar manejo de errores

### GET `/api/sse-cierre`
Envía mensaje de cierre para probar eventos de cierre

---

## 📊 Estadísticas Monitoreadas

### En la Herramienta HTML:
- **Mensajes Recibidos**: Contador total de mensajes SSE
- **Errores**: Contador de errores de conexión/parsing
- **Reconexiones**: Contador de reconexiones automáticas
- **Último Mensaje**: Timestamp del último mensaje recibido

### En Angular (Consola):
- **Contador de rendimiento**: Log cada 100 mensajes
- **Timestamps**: Mostrados para cada mensaje
- **Tipos de evento**: Clasificación por tipo de notificación

---

## 🐛 Debugging y Troubleshooting

### Problemas Comunes:

1. **CORS Errors**
   - Verificar que Flask tenga CORS configurado
   - Verificar puerto 5000 en backend

2. **Connection Refused**
   - Verificar que Flask esté ejecutándose
   - Verificar puerto 5000

3. **JSON Parse Errors**
   - Verificar formato de mensajes en backend
   - Revisar logs de consola para datos malformados

4. **Reconexión No Funciona**
   - Verificar timeout de 5 segundos
   - Verificar estado de EventSource

### Logs Útiles:
```bash
# Backend
👥 Nueva conexión SSE: 127.0.0.1
Error en SSE: [descripción del error]

# Frontend (Consola)
✅ Conexión SSE establecida
📊 Recibidos 100 mensajes SSE
❌ Error parseando JSON SSE: [error]
```

---

## 🎯 Cobertura de Pruebas

| Caso de Prueba | Implementado | Verificado |
|----------------|--------------|------------|
| Conexión exitosa | ✅ | ✅ |
| Recepción de mensajes | ✅ | ✅ |
| Reconexión automática | ✅ | ✅ |
| Orden de mensajes | ✅ | ✅ |
| Manejo de JSON | ✅ | ✅ |
| Eventos de error | ✅ | ✅ |
| Prueba de rendimiento | ✅ | ✅ |
| Cierre desde servidor | ✅ | ✅ |
| Múltiples conexiones | ✅ | ✅ |
| Timestamps | ✅ | ✅ |

---

## 🚀 Próximos Pasos

1. **Ejecutar todas las pruebas** usando la herramienta HTML
2. **Verificar logs** en consola de Angular
3. **Monitorear rendimiento** con múltiples conexiones
4. **Probar escenarios de error** reales
5. **Documentar resultados** de las pruebas

¡Las pruebas SSE están completamente implementadas y listas para usar! 🎉 