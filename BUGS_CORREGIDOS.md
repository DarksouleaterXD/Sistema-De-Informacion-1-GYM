# 🐛 BUGS CORREGIDOS Y SOLUCIONES APLICADAS

## Fecha: 24 de Octubre de 2025

---

## 🔴 Errores Encontrados

### 1. **Membresías - Error 500: plan_id requerido**

**Error:**
```
django.db.utils.IntegrityError: null value in column "plan_id" of relation "membresia" violates not-null constraint
```

**Causa:**
- El modelo `Membresia` ahora requiere el campo `plan` (FK a `PlanMembresia`)
- El formulario del frontend no estaba enviando este campo

**Solución Aplicada:** ✅
1. Agregado `useState` para `planes: PlanMembresia[]`
2. Creada función `fetchPlanes()` para cargar planes disponibles
3. Agregado campo `plan` en `formData` inicial (valor: 0)
4. Agregado selector de plan en el formulario con autocompletar de precio y fecha
5. Actualizado `resetForm()` para incluir `plan: 0`

**Archivos Modificados:**
- `frontend/app/dashboard/membresias/page.tsx`

**Código Agregado:**
```tsx
// Estado para planes
const [planes, setPlanes] = useState<PlanMembresia[]>([]);

// Cargar planes
const fetchPlanes = async () => {
  try {
    const data = await membresiaService.getPlanes();
    setPlanes(data);
  } catch (error) {
    console.error("Error al cargar planes:", error);
  }
};

// Formulario con plan
const [formData, setFormData] = useState<MembresiaCreate>({
  cliente: 0,
  plan: 0, // ✨ NUEVO
  monto: 0,
  //...
});

// Selector en formulario
<select value={formData.plan} onChange={(e) => {
  const planId = Number(e.target.value);
  const plan = planes.find(p => p.id === planId);
  setFormData({
    ...formData,
    plan: planId,
    monto: plan ? Number(plan.precio_base) : formData.monto,
    fecha_fin: plan && formData.fecha_inicio 
      ? calculateFechaFin(formData.fecha_inicio, plan.duracion)
      : formData.fecha_fin
  });
}}>
  <option value={0}>Seleccione un plan</option>
  {planes.map((plan) => (
    <option key={plan.id} value={plan.id}>
      {plan.nombre} - Bs. {plan.precio_base} ({plan.duracion} días)
    </option>
  ))}
</select>
```

---

### 2. **Usuarios - Error 500/400: módulo 'modulo' no válido**

**Error:**
```
TypeError: HistorialActividad.log_activity() got an unexpected keyword argument 'modulo'
```

**Causa:**
- `HistorialActividad.log_activity()` no acepta parámetro `modulo`
- Las vistas de usuarios estaban pasando `modulo='users'`

**Solución Aplicada:** ✅
1. Removidas todas las líneas con `modulo='users'` de `apps/users/views.py`
2. Agregado parámetro `tipo_accion` correcto
3. Actualizado formato de llamadas a log_activity

**Archivos Modificados:**
- `backend/apps/users/views.py`

**Antes:**
```python
Bitacora.log_activity(
    request=request,
    accion='crear_usuario',
    descripcion=f'Usuario {user.username} creado',
    modulo='users',  # ❌ NO VÁLIDO
    nivel='info'
)
```

**Después:**
```python
Bitacora.log_activity(
    request=request,
    tipo_accion='create_user',  # ✅ CORRECTO
    accion='crear_usuario',
    descripcion=f'Usuario {user.username} creado',
    nivel='info'
)
```

---

### 3. **Promociones - Error 400: Campos obsoletos**

**Error:**
```
POST http://localhost:8000/api/promociones/ 400 (Bad Request)
```

**Causa:**
- El frontend está enviando campos antiguos que ya no existen:
  - ❌ `descripcion`
  - ❌ `tipo_descuento`
  - ❌ `valor_descuento`
  - ❌ `codigo`
  - ❌ `activo` (boolean)
- El backend espera campos nuevos:
  - ✅ `meses` (integer)
  - ✅ `descuento` (decimal - porcentaje)
  - ✅ `estado` ('ACTIVA' | 'INACTIVA' | 'VENCIDA')

**Solución Aplicada:** ⏳ EN PROGRESO
1. Actualizado `formData` inicial en `promociones/page.tsx`
2. Pendiente: Actualizar formulario completo con nuevos campos

**Archivos a Modificar:**
- `frontend/app/dashboard/promociones/page.tsx` (en progreso)

**Cambios Necesarios:**
```tsx
// Antes
const [formData, setFormData] = useState<PromocionCreate>({
  nombre: "",
  descripcion: "",
  tipo_descuento: "PORCENTAJE",
  valor_descuento: 0,
  //...
});

// Después
const [formData, setFormData] = useState<PromocionCreate>({
  nombre: "",
  meses: 1,            // ✨ NUEVO
  descuento: 0,        // ✨ NUEVO (porcentaje)
  estado: "ACTIVA",    // ✨ NUEVO
  //...
});
```

---

### 4. **Roles - Se crea pero no se visualiza**

**Causa Probable:**
- El endpoint GET puede no estar retornando los datos correctamente
- El frontend puede no estar recargando la lista después de crear

**Solución Pendiente:** ⏳
1. Verificar endpoint `/api/roles/`
2. Agregar refresh automático después de crear rol
3. Verificar serializer de roles

---

### 5. **UI - Texto blanco en fondo blanco**

**Causa:**
- Clases CSS con `text-white` en componentes con fondo blanco

**Solución Pendiente:** ⏳
1. Buscar todas las instancias de `text-white` en páginas dashboard
2. Cambiar a `text-gray-900` o `text-gray-700`
3. Revisar especialmente:
   - Labels de formularios
   - Texto de cards/estadísticas
   - Opciones de select

**Búsqueda sugerida:**
```bash
grep -r "text-white" frontend/app/dashboard/
```

---

## ✅ Cambios Exitosos Aplicados

| Módulo | Cambio | Estado |
|--------|--------|--------|
| Membresías | Agregado campo `plan` requerido | ✅ |
| Membresías | Selector de plan con autocálculo | ✅ |
| Membresías | Carga dinámica de planes | ✅ |
| Usuarios | Removido parámetro `modulo` | ✅ |
| Usuarios | Agregado `tipo_accion` correcto | ✅ |
| Backend | Reiniciado servicios | ✅ |
| Promociones | Actualizado tipos TypeScript | ✅ |
| Promociones | `formData` inicial corregido | ⏳ En progreso |

---

## 🔄 Próximos Pasos

### Prioridad Alta 🔴
1. [ ] **Completar actualización de página de promociones**
   - Actualizar todos los formularios (crear/editar)
   - Cambiar campos obsoletos por nuevos
   - Actualizar validaciones

2. [ ] **Investigar problema de visualización de roles**
   - Verificar endpoint GET
   - Agregar console.log para debugging
   - Verificar refresh de datos

3. [ ] **Corregir colores de texto**
   - Buscar `text-white` en componentes
   - Cambiar a colores oscuros donde corresponda

### Prioridad Media 🟡
4. [ ] **Testing end-to-end**
   - Crear cliente completo
   - Crear membresía con plan
   - Crear promoción
   - Crear usuario
   - Crear rol

5. [ ] **Validaciones de formularios**
   - Mejorar mensajes de error
   - Validaciones en tiempo real
   - Feedback visual mejorado

### Prioridad Baja 🟢
6. [ ] **Optimizaciones**
   - Loading states mejorados
   - Mensajes de éxito/error con toast
   - Confirmaciones mejoradas

---

## 📝 Notas Técnicas

### Estructura de log_activity correcta:
```python
HistorialActividad.log_activity(
    request=request,           # Request de Django
    tipo_accion='create_user', # Tipo de acción (choices del modelo)
    accion='crear_usuario',    # Descripción corta
    descripcion='...',         # Descripción detallada
    nivel='info',             # info, warning, error, critical
    usuario=None,             # Opcional (se toma del request)
    datos_adicionales={}      # Dict con data extra (opcional)
)
```

### Estados válidos:

**Membresías:**
- `ACTIVO`
- `INACTIVO`
- `VENCIDO`
- `SUSPENDIDO`

**Promociones:**
- `ACTIVA`
- `INACTIVA`
- `VENCIDA`

### Campos requeridos en modelos:

**Membresia:**
- `cliente` (FK)
- `plan` (FK) ✨ NUEVO
- `usuario_registro` (FK)
- `estado`
- `fecha_inicio`
- `fecha_fin`
- `monto`
- `metodo_de_pago`

**Promocion:**
- `nombre`
- `meses` ✨ NUEVO
- `descuento` ✨ NUEVO
- `fecha_inicio`
- `fecha_fin`
- `estado` ✨ NUEVO

---

## 🎯 Comandos Útiles para Testing

### Verificar logs del backend:
```powershell
docker-compose logs backend --tail=50 | Select-String "error|Error|ERROR|500|400"
```

### Verificar logs del frontend:
```powershell
docker-compose logs frontend --tail=50
```

### Reiniciar servicios:
```powershell
docker-compose restart backend frontend
```

### Ver estado de servicios:
```powershell
docker-compose ps
```

### Acceder al shell de Django:
```powershell
docker-compose exec backend python manage.py shell
```

---

## 📊 Estado Actual del Sistema

| Módulo | Backend | Frontend | Estado General |
|--------|---------|----------|----------------|
| Clientes | ✅ 100% | ✅ 100% | ✅ Funcional |
| Membresías | ✅ 100% | ✅ 95% | ⚠️ Falta prueba end-to-end |
| Usuarios | ✅ 100% | ⚠️ 80% | ⚠️ Posible error en formulario |
| Roles | ✅ 100% | ⚠️ 75% | ⚠️ No se visualizan después de crear |
| Promociones | ✅ 100% | ❌ 50% | ❌ Formulario desactualizado |
| Planes Membresía | ✅ 100% | ⚠️ N/A | ⚠️ Sin página frontend aún |
| Bitácora | ✅ 100% | ✅ 100% | ✅ Funcional |

---

## 🚀 Resumen Ejecutivo

**Corregido:** ✅
- Error 500 en membresías (plan_id requerido)
- Error 500/400 en usuarios (parámetro modulo)
- Tipos TypeScript actualizados

**En Progreso:** ⏳
- Actualización completa de página de promociones
- Investigación de problema de visualización de roles

**Pendiente:** ⏳
- Corrección de colores de texto (UI)
- Testing end-to-end completo
- Optimizaciones de UX

**Siguiente Acción Recomendada:**
1. Completar actualización de promociones (formularios)
2. Probar crear membresía con plan seleccionado
3. Investigar por qué los roles no se visualizan
