# MedCheck - Sistema de Verificación de Medicación

Sistema web para gestionar protocolos y listas de cotejo en la administración de medicamentos hospitalarios.

## Características

- ✅ Registro de verificaciones por etapa del protocolo
- 📊 Reportes de cumplimiento en tiempo real
- 🔍 Detección de anomalías y alertas
- 📱 Interfaz web responsive con PWA
- 🔐 Autenticación segura de usuarios
- ⚡ API REST con FastAPI
- 🗄️ Almacenamiento flexible (SQLite/PostgreSQL/Snowflake)
- 🔔 Notificaciones push y recordatorios
- 🎙️ Asistente de voz (ElevenLabs)

## Requisitos

- Python 3.8+
- pip (gestor de paquetes de Python)
- Cuenta de Snowflake (opcional, para producción)
- API Key de ElevenLabs (opcional, para asistente de voz)

## Instalación Rápida

1. **Clonar el repositorio:**
```bash
git clone https://github.com/angiealadro-dotcom/medcheck.git
cd medcheck
```

2. **Crear un entorno virtual:**
```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno (opcional):**
```bash
# Copiar el archivo de ejemplo
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# Editar .env con tus configuraciones personalizadas
```

5. **Inicializar la base de datos:**
```bash
python init_db.py
```

## Uso

### Método 1: Launcher Python (Recomendado)
```bash
python run_dev.py
```

Este script:
- ✅ Verifica dependencias
- ✅ Inicia el servidor con auto-reload
- ✅ Abre automáticamente el navegador
- ✅ Funciona en Windows, Linux y Mac

### Método 2: Comando directo
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8002
```

### Método 3: Script Windows
```cmd
.\start_local_server.cmd
```

## Acceso al Sistema

- **URL Principal:** http://127.0.0.1:8002
- **Documentación API:** http://127.0.0.1:8002/docs
- **Health Check:** http://127.0.0.1:8002/health

### Credenciales por Defecto

```
Usuario: admin
Contraseña: Admin123!
```

> ⚠️ **IMPORTANTE:** Cambia estas credenciales en producción

2. Acceder a la documentación de la API:
```
http://localhost:8000/docs
```

## Estructura del Proyecto

```
medcheck/
├── app/
│   ├── main.py           # Aplicación FastAPI
│   ├── routers/          # Endpoints de la API
│   ├── models/           # Modelos Pydantic
│   ├── db/              # Conexión a Snowflake
│   └── auth/            # Autenticación
├── static/              # Archivos estáticos
├── templates/           # Templates Jinja2
├── tests/              # Tests
├── requirements.txt    # Dependencias
└── .env.example       # Template de variables de entorno
```

## Endpoints Principales

- `POST /checklist/`: Crear nuevo registro de verificación
- `GET /checklist/`: Obtener registros con filtros
- `GET /reports/summary`: Resumen de cumplimiento
- `GET /reports/anomalies`: Detección de anomalías
- `POST /auth/token`: Login (obtener token JWT)

## Seguridad

- Autenticación JWT
- Validación de datos con Pydantic
- CORS configurado
- Variables de entorno para secrets

## Contribuir

1. Fork el repositorio
2. Crear rama (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

---

## 📊 EVIDENCIA 7: Diseño de Indicadores de Calidad en Salud

### 🎯 Objetivos

1. **Comprender** el papel de los indicadores de calidad como herramientas para medir y mejorar la atención en salud
2. **Aplicar** el pensamiento crítico para interpretar y utilizar indicadores en casos clínicos reales y simulados
3. **Proponer** mejoras basadas en los resultados de indicadores

### 🎓 Competencias Específicas

Este proyecto desarrolla las siguientes competencias profesionales en salud:

- ✅ **Distinguir** los distintos tipos de indicadores de calidad en salud
- ✅ **Conocer** las fuentes de información para la obtención y análisis de indicadores (expediente clínico, reportes, NOM, etc.)
- ✅ **Interpretar** adecuadamente datos e informes relacionados con indicadores clave
- ✅ **Relacionar** los resultados de indicadores con acciones de mejora continua
- ✅ **Evaluar** el cumplimiento de estándares de calidad mediante indicadores operacionales

---

## 💊 Los 10 Correctos para la Administración de Medicamentos

MedCheck está diseñado para verificar sistemáticamente los **10 Correctos** de administración segura de medicamentos:

### 1. 👤 Paciente Correcto
- Verificación de identidad con dos identificadores únicos
- Confirmación con brazalete y/o expediente clínico
- Preguntar al paciente su nombre completo

### 2. 💊 Medicamento Correcto
- Verificar nombre genérico y comercial
- Confirmar contra la orden médica
- Revisar etiquetado y presentación

### 3. 📏 Dosis Correcta
- Validar cantidad exacta prescrita
- Verificar unidades de medida
- Confirmar cálculos de dosificación

### 4. 🔀 Vía de Administración Correcta
- Confirmar ruta prescrita (oral, IV, IM, SC, etc.)
- Verificar idoneidad de la vía para el medicamento
- Asegurar preparación adecuada según vía

### 5. ⏰ Hora de Administración Correcta
- Respetar intervalos de dosificación
- Verificar horarios establecidos
- Documentar hora real de administración

### 6. 📅 Fecha de Vencimiento Correcta
- Verificar que el medicamento no esté caducado
- Revisar condiciones de almacenamiento
- Descartar medicamentos vencidos

### 7. 📚 Educación al Paciente
- Informar sobre el medicamento y su propósito
- Explicar efectos esperados y posibles reacciones
- Responder dudas y obtener consentimiento informado

### 8. 📝 Registro Correcto
- Documentar administración inmediatamente
- Registrar dosis, hora, vía y respuesta del paciente
- Mantener trazabilidad completa

### 9. ⚠️ Verificación de Alergias
- Indagar historial de alergias medicamentosas
- Verificar contraindicaciones
- Consultar interacciones medicamentosas

### 10. 🔐 Responsabilidad Personal
- Preparar, administrar y registrar personalmente
- No delegar sin supervisión adecuada
- Evitar acciones basadas únicamente en confianza

> **Nota:** MedCheck automatiza la verificación de estos 10 correctos mediante su checklist digital, reduciendo significativamente el riesgo de errores de medicación.

---

## 📋 Ficha Técnica: Indicador de Calidad de Procesos

### Indicador: Cumplimiento del Uso de la Lista de Cotejo Digital "MedCheck" (CLMC)

| **Atributo** | **Especificación** |
|-------------|-------------------|
| **Nombre del Indicador** | Cumplimiento del uso de la lista de cotejo digital "MedCheck" para la administración segura de medicamentos (CLMC) |
| **Tipo de Indicador** | **Proceso** - Agrupación de datos - Positivo |
| **Propósito** | Los errores de medicación representan una de las causas más frecuentes de eventos adversos hospitalarios, especialmente en pacientes con múltiples medicamentos y en unidades de alta demanda. Por ello, la medición del indicador se enfoca en evaluar el cumplimiento del uso del checklist digital MedCheck previo a cada administración de medicamentos. |

#### 📊 Método de Cálculo

```
                     Formatos MedCheck Completos
CLMC (%) = ──────────────────────────────────────── × 100
           Total de Administraciones de Medicamentos
```

| **Componente** | **Descripción** |
|---------------|-----------------|
| **Numerador** | Número de administraciones con checklist MedCheck completo (10 correctos verificados) |
| **Denominador** | Total de administraciones de medicamentos realizadas en el periodo |
| **Multiplicador** | × 100 |
| **Unidad de Medida** | Porcentaje (%) |

#### 👥 Población Objetivo

Todos los pacientes que reciban administración de medicamentos en las unidades participantes del sistema MedCheck.

#### 📈 Interpretación

**Mayor porcentaje = Mayor cumplimiento = Mejor calidad**

El indicador mide la adherencia del personal de salud al protocolo de verificación digital. Un porcentaje alto indica:
- Uso sistemático de la herramienta
- Cultura de seguridad del paciente
- Reducción de riesgo de errores de medicación
- Trazabilidad y documentación completa

#### 🎯 Metas y Umbrales

| **Rango** | **Clasificación** | **Acción Requerida** |
|-----------|------------------|---------------------|
| **90% - 100%** | ✅ Calidad Óptima | Mantener y reconocer buenas prácticas |
| **80% - 89%** | ⚠️ Zona de Alerta | Intervención inmediata y capacitación |
| **< 80%** | 🚨 Fuera de Control | Acciones correctivas urgentes |

**Meta Institucional:** ≥ 90% de cumplimiento mensual

**Fundamentación:** Basado en estándares internacionales de seguridad del paciente (WHO, Joint Commission, ISMP)

#### 📅 Frecuencia de Medición

- **Reporte Mensual**: Análisis de tendencias y cumplimiento de meta
- **Revisiones Semanales**: Monitoreo interno por servicio
- **Auditorías**: Evaluación trimestral de calidad de datos

#### 📁 Fuente de Datos

**Sistema MedCheck** - Lista de cotejo digital integrada que:
- Registra en tiempo real cada verificación
- Genera reportes automáticos
- Identifica campos incompletos o omitidos
- Permite trazabilidad por usuario, turno y servicio
- Almacena evidencia para auditorías

#### 👨‍⚕️ Responsables de Medición

| **Rol** | **Responsabilidad** |
|---------|-------------------|
| **Supervisor de Enfermería** | Monitoreo diario y retroalimentación al personal |
| **Departamento de Farmacovigilancia** | Análisis de datos y detección de patrones |
| **Comité de Calidad y Seguridad del Paciente** | Evaluación de resultados y propuesta de mejoras |
| **Administrador de Plataforma MedCheck** | Mantenimiento técnico y generación de reportes |

#### ⚠️ Factores que Influyen en el Desempeño

**Factores Facilitadores:**
- ✅ Capacitación adecuada del personal
- ✅ Disponibilidad de dispositivos electrónicos
- ✅ Conectividad estable
- ✅ Cultura organizacional de seguridad
- ✅ Apoyo de la dirección

**Factores Obstaculizadores:**
- ❌ Alta carga laboral del personal
- ❌ Escasez de dispositivos móviles
- ❌ Prescripciones ilegibles o incompletas
- ❌ Interrupciones frecuentes durante la administración
- ❌ Fallas tecnológicas o de conectividad
- ❌ Resistencia al cambio
- ❌ Falta de supervisión o auditoría

---

## 📋 Ficha Técnica: Indicador de Calidad de Resultados

### Indicador: Tasa de Eventos Adversos por Errores de Medicación (TEAEM)

| **Atributo** | **Especificación** |
|-------------|-------------------|
| **Nombre del Indicador** | Tasa de Eventos Adversos por Errores de Medicación detectados mediante MedCheck (TEAEM) |
| **Tipo de Indicador** | **Resultado** - Agrupación de datos - Negativo (menor es mejor) |
| **Propósito** | Medir la incidencia de eventos adversos relacionados con errores en la administración de medicamentos, identificando específicamente aquellos casos donde se documentó el incumplimiento de uno o más de los 10 correctos. Este indicador permite evaluar el impacto real del sistema MedCheck en la seguridad del paciente. |

#### 📊 Método de Cálculo

```
                     Eventos con Incumplimiento de ≥1 Correcto
TEAEM (%) = ─────────────────────────────────────────────────── × 100
            Total de Administraciones de Medicamentos
```

| **Componente** | **Descripción** |
|---------------|-----------------|
| **Numerador** | Número de eventos adversos de medicación donde se documenta incumplimiento de uno o más de los 10 correctos |
| **Denominador** | Total de administraciones de medicamentos realizadas en el periodo (población en riesgo) |
| **Multiplicador** | × 100 |
| **Unidad de Medida** | Porcentaje (%) o Tasa por 100 administraciones |

#### 👥 Población Objetivo

Todos los pacientes que recibieron administración de medicamentos y en quienes se utilizó el sistema MedCheck para la verificación.

#### 📈 Interpretación

**Menor porcentaje = Mejor resultado = Mayor seguridad**

Este indicador de resultado mide directamente:
- Efectividad del sistema de verificación
- Impacto en la reducción de errores
- Áreas de oportunidad específicas (cuál de los 10 correctos se incumple más)
- Consecuencias de no seguir el protocolo

#### 🎯 Metas y Umbrales

| **Rango** | **Clasificación** | **Acción Requerida** |
|-----------|------------------|---------------------|
| **0% - 2%** | ✅ Excelencia | Mantener estándares y difundir mejores prácticas |
| **2.1% - 5%** | ⚠️ Aceptable con Vigilancia | Análisis de causas y medidas preventivas |
| **> 5%** | 🚨 Inaceptable | Intervención inmediata, auditoría y plan de acción |

**Meta Institucional:** ≤ 2% de eventos adversos por error de medicación

**Fundamentación:** 
- WHO: Global Patient Safety Action Plan 2021-2030
- Joint Commission: National Patient Safety Goals
- ISMP: Medication Safety Best Practices

#### 📅 Frecuencia de Medición

- **Reporte Mensual**: Análisis de incidencias y tendencias
- **Revisiones Semanales**: Monitoreo de eventos centinela
- **Análisis Trimestral**: Evaluación de impacto de intervenciones

#### 📁 Fuente de Datos

**Fuentes Integradas:**
1. **Sistema MedCheck**: Registro de verificaciones y alertas de incumplimiento
2. **Reportes de Farmacovigilancia**: Eventos adversos notificados
3. **Expediente Clínico Electrónico**: Documentación de eventos
4. **Sistema de Notificación de Eventos Adversos**: COFEPRIS/institucional

#### 👨‍⚕️ Responsables de Medición

| **Rol** | **Responsabilidad** |
|---------|-------------------|
| **Departamento de Farmacovigilancia** | Investigación y clasificación de eventos adversos |
| **Comité de Calidad y Seguridad del Paciente** | Análisis de causa raíz y propuesta de mejoras |
| **Supervisor de Enfermería** | Notificación oportuna de eventos |
| **Administrador de Plataforma MedCheck** | Correlación de datos y generación de reportes |
| **Dirección Médica** | Toma de decisiones basada en evidencia |

#### ⚠️ Factores que Influyen en el Desempeño

**Factores de Riesgo:**
- ❌ No utilizar o completar parcialmente el checklist MedCheck
- ❌ Carga laboral excesiva
- ❌ Fatiga del personal
- ❌ Prescripciones ambiguas o ilegibles
- ❌ Medicamentos de alto riesgo mal identificados
- ❌ Interrupciones durante la preparación/administración
- ❌ Falta de capacitación continua
- ❌ Cultura punitiva vs. cultura de seguridad

**Factores Protectores:**
- ✅ Uso sistemático de MedCheck
- ✅ Doble verificación en medicamentos de alto riesgo
- ✅ Entorno laboral seguro y sin distracciones
- ✅ Cultura de notificación sin castigo
- ✅ Capacitación continua
- ✅ Supervisión y retroalimentación constructiva

---

## ⚖️ Matriz de Riesgos y Toma de Decisiones

### Análisis de Riesgos en la Administración de Medicamentos

| **Riesgo Identificado** | **Probabilidad** | **Impacto** | **Nivel de Riesgo** | **Estrategia de Mitigación** | **Responsable** |
|------------------------|-----------------|------------|-------------------|----------------------------|----------------|
| Error en identificación del paciente | Media | Alto | **ALTO** | Implementación de doble verificación con MedCheck | Enfermería |
| Medicamento incorrecto administrado | Baja | Muy Alto | **ALTO** | Escaneo de código de barras + verificación en MedCheck | Farmacia + Enfermería |
| Dosis incorrecta | Media | Alto | **ALTO** | Calculadora integrada y alertas automáticas en MedCheck | Enfermería |
| Vía de administración incorrecta | Baja | Alto | **MEDIO** | Checklist obligatorio antes de administración | Enfermería |
| Hora de administración fuera de ventana | Alta | Medio | **MEDIO** | Recordatorios automáticos y notificaciones push | Sistema MedCheck |
| Medicamento caducado | Baja | Medio | **MEDIO** | Verificación obligatoria de fecha de vencimiento | Farmacia + Enfermería |
| Falta de educación al paciente | Alta | Bajo | **MEDIO** | Campo obligatorio en checklist | Enfermería |
| Omisión de registro | Media | Medio | **MEDIO** | Registro digital automático con timestamp | Sistema MedCheck |
| No verificar alergias | Baja | Muy Alto | **ALTO** | Alerta automática al acceder al perfil del paciente | Sistema MedCheck |
| Delegación inadecuada | Baja | Alto | **MEDIO** | Firma digital personalizada por usuario | Sistema MedCheck |

### Niveles de Riesgo

- 🔴 **ALTO (15-25 puntos)**: Requiere acción inmediata y monitoreo continuo
- 🟡 **MEDIO (8-14 puntos)**: Requiere plan de acción y seguimiento regular
- 🟢 **BAJO (1-7 puntos)**: Mantener controles actuales

### Matriz de Decisiones según Resultados de Indicadores

| **Resultado CLMC** | **Resultado TEAEM** | **Decisión Estratégica** | **Acciones Inmediatas** |
|-------------------|-------------------|------------------------|----------------------|
| ≥90% | ≤2% | ✅ **Mantener y Mejorar** | Reconocimiento, difusión de mejores prácticas |
| ≥90% | 2.1-5% | ⚠️ **Investigar Discrepancia** | Auditoría de calidad de datos, análisis de eventos |
| 80-89% | ≤2% | ⚠️ **Reforzar Cumplimiento** | Capacitación, recordatorios, supervisión |
| 80-89% | 2.1-5% | 🚨 **Intervención Moderada** | Plan de mejora, auditoría semanal |
| <80% | >5% | 🚨 **Crisis - Acción Urgente** | Suspensión de procesos, reentrenamiento, auditoría externa |
| <80% | ≤2% | ⚠️ **Revisar Medición** | Validar fuentes de datos, posible subregistro |

---

## 📅 Diagrama de Gantt del Proyecto MedCheck

### Cronograma de Implementación y Mejora Continua

```
FASE                          MES 1  MES 2  MES 3  MES 4  MES 5  MES 6  MES 7  MES 8
──────────────────────────────────────────────────────────────────────────────────
1. PLANIFICACIÓN
   └─ Análisis de necesidades   ██████
   └─ Diseño de indicadores      ██████
   └─ Aprobación institucional         ████

2. DESARROLLO
   └─ Desarrollo de software            ████████████
   └─ Pruebas unitarias                      ████████
   └─ Integración BD                               ██████

3. CAPACITACIÓN
   └─ Material didáctico                     ████████
   └─ Capacitación piloto                          ██████
   └─ Capacitación masiva                                ██████

4. IMPLEMENTACIÓN
   └─ Piloto (Unidad 1)                                  ████████
   └─ Expansión (3 Unidades)                                   ██████████
   └─ Implementación completa                                        ████████

5. MONITOREO Y EVALUACIÓN
   └─ Recolección de datos                                     ████████████████
   └─ Análisis mensual                                         ████████████████
   └─ Ajustes y mejoras                                              ██████████

6. DOCUMENTACIÓN
   └─ Informe preliminar                                             ██████
   └─ Informe final                                                        ████
──────────────────────────────────────────────────────────────────────────────────
HITOS CLAVE:
   🎯 M1: Aprobación del proyecto
   🎯 M3: Prototipo funcional
   🎯 M5: Finalización de capacitación
   🎯 M6: Inicio de piloto
   🎯 M7: Implementación completa
   🎯 M8: Evaluación de resultados
```

### Actividades Detalladas por Fase

#### **Mes 1-2: Planificación**
- [x] Conformación del equipo multidisciplinario
- [x] Análisis de necesidades institucionales
- [x] Diseño de indicadores de proceso y resultado
- [x] Definición de los 10 correctos a verificar
- [x] Aprobación del Comité de Calidad

#### **Mes 2-4: Desarrollo**
- [x] Desarrollo de la aplicación web MedCheck
- [x] Creación de base de datos relacional
- [x] Implementación de checklist digital
- [x] Desarrollo de módulo de reportes
- [x] Integración con sistemas existentes
- [x] Pruebas de funcionalidad y seguridad

#### **Mes 3-5: Capacitación**
- [x] Elaboración de manuales de usuario
- [x] Creación de videos tutoriales
- [x] Capacitación al equipo piloto (20 usuarios)
- [ ] Capacitación masiva (200+ usuarios)
- [ ] Evaluación de competencias adquiridas

#### **Mes 5-7: Implementación**
- [ ] Fase piloto en Unidad de Cuidados Intensivos
- [ ] Análisis de retroalimentación y ajustes
- [ ] Expansión a Medicina Interna, Cirugía y Pediatría
- [ ] Implementación completa en hospital
- [ ] Soporte técnico 24/7

#### **Mes 6-8: Monitoreo y Evaluación**
- [ ] Medición semanal de indicadores
- [ ] Análisis mensual de cumplimiento
- [ ] Detección de áreas de oportunidad
- [ ] Implementación de acciones correctivas
- [ ] Evaluación de impacto en seguridad del paciente
- [ ] Informe final de resultados

---

## 📋 Lista de Cotejo para Construcción de Indicadores

### Verificación del Proceso Metodológico

| **Criterio** | **Estado** | **Evidencia** |
|-------------|-----------|---------------|
| ¿Se detecta claramente la necesidad o el objetivo de mejora del indicador? | ✅ **SÍ** | Reducción de errores de medicación y mejora de seguridad del paciente |
| ¿Se ha conformado el equipo multidisciplinario que diseña el indicador? | ✅ **SÍ** | Enfermería, Medicina, Farmacia, Calidad, Informática |
| ¿Se seleccionó un proceso o área específica a evaluar? | ✅ **SÍ** | Administración segura de medicamentos |
| ¿El indicador tiene un nombre claro y definido? | ✅ **SÍ** | CLMC y TEAEM claramente identificados |
| ¿Se definió operacionalmente el indicador (numerador, denominador, unidad de medida)? | ✅ **SÍ** | Fórmulas matemáticas especificadas |
| ¿Se identificó la fuente de información para el cálculo? | ✅ **SÍ** | Sistema MedCheck, Farmacovigilancia, ECE |
| ¿Se estableció la frecuencia de medición del indicador? | ✅ **SÍ** | Mensual con revisiones semanales |
| ¿Cumple con criterios de calidad (relevante, válido, confiable, factible, sensible al cambio)? | ✅ **SÍ** | Basado en estándares internacionales |
| ¿Se definieron metas o estándares de referencia? | ✅ **SÍ** | CLMC ≥90%, TEAEM ≤2% |
| ¿Se planificó quién, cómo y cuándo se recogerán los datos, incluyendo capacitación? | ✅ **SÍ** | Responsables definidos, capacitación programada |
| ¿Existen mecanismos definidos para el análisis de los datos? | ⏳ **En Proceso** | Dashboard en desarrollo, reportes automatizados |
| ¿Los resultados se comunican al equipo clínico o directivo? | 📋 **Planificado** | Reportes mensuales al Comité de Calidad |
| ¿Se han realizado ajustes al indicador según retroalimentación o cambios en el contexto? | 📋 **Planificado** | Revisión trimestral de pertinencia |
| ¿Se han tomado decisiones basadas en los datos obtenidos? | 📋 **Planificado** | Matriz de decisiones implementada |
| ¿Se han establecido mecanismos de seguimiento y control? | 📋 **Planificado** | Auditorías trimestrales y seguimiento semanal |

**Leyenda:**
- ✅ Completado
- ⏳ En Proceso
- 📋 Planificado

---

## 🔬 Metodología SMART para los Indicadores

### Indicador CLMC (Proceso)

| **Criterio SMART** | **Aplicación** |
|-------------------|---------------|
| **S** (Specific - Específico) | Mide el porcentaje de administraciones con checklist MedCheck completo |
| **M** (Measurable - Medible) | Numerador y denominador claramente definidos, fórmula matemática precisa |
| **A** (Achievable - Alcanzable) | Meta de 90% es ambiciosa pero alcanzable con capacitación adecuada |
| **R** (Relevant - Relevante) | Directamente relacionado con seguridad del paciente y calidad asistencial |
| **T** (Time-bound - Temporal) | Medición mensual con hito de implementación completa en 8 meses |

### Indicador TEAEM (Resultado)

| **Criterio SMART** | **Aplicación** |
|-------------------|---------------|
| **S** (Specific - Específico) | Mide eventos adversos por incumplimiento de correctos de medicación |
| **M** (Measurable - Medible) | Tasa calculada con datos de farmacovigilancia y sistema MedCheck |
| **A** (Achievable - Alcanzable) | Meta ≤2% alineada con estándares internacionales (WHO, Joint Commission) |
| **R** (Relevant - Relevante) | Impacto directo en seguridad, morbimortalidad y costos hospitalarios |
| **T** (Time-bound - Temporal) | Evaluación mensual con análisis de tendencias semestrales |

---

## 📞 Contacto y Soporte

Para más información sobre el proyecto MedCheck o colaboración:

- **Repositorio:** [github.com/angiealadro-dotcom/MEDCHECK](https://github.com/angiealadro-dotcom/MEDCHECK)
- **Documentación API:** http://127.0.0.1:8002/docs
- **Issues:** [GitHub Issues](https://github.com/angiealadro-dotcom/MEDCHECK/issues)

---

## 📄 Licencia

Este proyecto está desarrollado con fines académicos y de mejora de la calidad en salud.

---

## 🙏 Agradecimientos

- Equipo de Enfermería por su retroalimentación continua
- Departamento de Calidad y Seguridad del Paciente
- Comité de Farmacovigilancia
- Todos los profesionales de la salud comprometidos con la seguridad del paciente

---

**Última actualización:** Noviembre 2025  
**Versión:** 1.1.0  
**Estado:** ✅ En producción - Fase de implementación

## Siguientes Pasos

- [x] Implementar frontend con templates
- [x] Configurar base de datos
- [x] Diseñar indicadores de calidad
- [x] Implementar checklist de 10 correctos
- [ ] Añadir tests automatizados
- [ ] Configurar CI/CD
- [ ] Implementar análisis predictivo con ML
- [ ] Expandir a otras instituciones
