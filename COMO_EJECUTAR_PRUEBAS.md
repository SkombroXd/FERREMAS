# 🚀 CÓMO EJECUTAR PRUEBAS SSE - FERREMAS

## ⚡ Ejecución Rápida (3 Opciones)

### 🎯 Opción 1: Script Automático (MÁS FÁCIL)

**Windows:**
```
Hacer doble clic en: ejecutar_pruebas_sse.bat
```

**Linux/Mac:**
```bash
./ejecutar_pruebas_sse.sh
```

### 🎯 Opción 2: Comando Directo

```bash
python test_sse/test_sse_automated.py
```

### 🎯 Opción 3: Herramienta HTML

```
Abrir en navegador: test_sse/sse_test.html
```

---

## ⚠️ IMPORTANTE: Antes de Ejecutar

1. **Iniciar Backend:**
   ```bash
   cd back
   python app.py
   ```

2. **Verificar que esté en puerto 5000:**
   ```
   http://localhost:5000
   ```

---

## 📍 Ubicación Correcta

**Asegúrate de estar en la raíz del proyecto:**
```
FERREMAS/
├── ejecutar_pruebas_sse.bat    ← Hacer doble clic aquí
├── test_sse/                   ← Carpeta con pruebas
└── back/                       ← Backend Flask
```

---

## ✅ Resultado Esperado

```
🎯 RESULTADO FINAL: 9/9 pruebas pasaron
🎉 ¡TODAS LAS PRUEBAS SSE PASARON EXITOSAMENTE!
```

### 📊 Datos del Sistema Verificados

**Sucursales:**
- 101: Sucursal Central Principal
- 102: Sucursal Sur
- 103: Sucursal Norte

**Productos:**
- FER-001: Plancha acero
- FER-002: Pala (usado en pruebas de stock)
- FER-003: Destornillador
- ... 13 productos total

### 📊 Detalles de Prueba de Stock
- **Producto**: FER-002 (Pala)
- **Cantidad**: +8 unidades
- **Sucursal**: 101 (Sucursal Central Principal)
- **Stock final**: 16 unidades

---

## 🐛 Si No Funciona

1. **Verificar ubicación**: `dir` debe mostrar carpeta `test_sse`
2. **Verificar Flask**: `http://localhost:5000` debe responder
3. **Instalar requests**: `pip install requests`

---

## 📞 Ayuda

- **Documentación completa**: `test_sse/README.md`
- **Guía detallada**: `test_sse/SSE_TESTING_GUIDE.md`
- **Problemas**: Revisar `PRUEBAS_SSE.md`

---

## 🎉 ¡Éxito Garantizado!

Todas las pruebas están verificadas y funcionando al 100%. El sistema SSE está completamente operativo con:

- ✅ 9 pruebas automatizadas
- ✅ Códigos reales del sistema (FER-001, sucursales 101, 102, 103)
- ✅ Herramienta HTML interactiva
- ✅ Integración con Angular
- ✅ Manejo robusto de errores 