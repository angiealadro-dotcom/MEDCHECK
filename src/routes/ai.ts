import { Hono } from 'hono';
import { authMiddleware } from '../middleware/auth';
import type { Env } from '../index';

// Nota: Estos endpoints son stubs (plantillas). No realizan integración real todavía.
// Para activarlos: establecer AI_ENABLED = "true" y configurar secretos (GEMINI_API_KEY, DRUG_DB_API_KEY).
// Todos retornan estructuras predecibles para facilitar el frontend.

const aiRouter = new Hono<{ Bindings: Env }>();

function aiDisabled(c: any) {
  return c.json({ error: 'AI module disabled', enabled: false }, 503);
}

// 1. Verificación visual de medicamento (imagen vs nombre esperado)
aiRouter.post('/verify-medication', authMiddleware, async (c) => {
  if (c.env.AI_ENABLED !== 'true') return aiDisabled(c);
  try {
    const body = await c.req.json();
    const { image_base64, expected_name } = body;
    if (!image_base64 || !expected_name) {
      return c.json({ error: 'image_base64 y expected_name son requeridos' }, 400);
    }
    // TODO: Llamar a Gemini Vision
    return c.json({
      match: false,
      confidence: 0,
      expected_name,
      detected_text: [],
      suggestions: ['Configurar Gemini para respuesta real'],
      stub: true,
    });
  } catch (err) {
    console.error('verify-medication stub error', err);
    return c.json({ error: 'Error interno' }, 500);
  }
});

// 2. OCR de etiqueta (lote, fecha vencimiento)
aiRouter.post('/extract-label', authMiddleware, async (c) => {
  if (c.env.AI_ENABLED !== 'true') return aiDisabled(c);
  try {
    const body = await c.req.json();
    const { image_base64 } = body;
    if (!image_base64) return c.json({ error: 'image_base64 requerido' }, 400);
    // TODO: Llamar a Gemini OCR
    return c.json({
      lot_number: null,
      expiration_date_iso: null,
      raw_text: [],
      confidence: 0,
      stub: true,
    });
  } catch (err) {
    return c.json({ error: 'Error interno' }, 500);
  }
});

// 3. Interacciones farmacológicas (lista de medicamentos)
aiRouter.post('/check-interactions', authMiddleware, async (c) => {
  if (c.env.AI_ENABLED !== 'true') return aiDisabled(c);
  try {
    const body = await c.req.json();
    const { medications } = body;
    if (!Array.isArray(medications) || medications.length < 2) {
      return c.json({ error: 'Al menos dos medicamentos son requeridos' }, 400);
    }
    // TODO: Llamar API externa de interacciones
    return c.json({
      interactions: [],
      severe_alerts: 0,
      notes: 'Integrar servicio de interacciones (Lexicomp/First Databank).',
      stub: true,
    });
  } catch (err) {
    return c.json({ error: 'Error interno' }, 500);
  }
});

// 4. Validación de dosis (paciente vs medicamento)
aiRouter.post('/validate-dose', authMiddleware, async (c) => {
  if (c.env.AI_ENABLED !== 'true') return aiDisabled(c);
  try {
    const body = await c.req.json();
    const { age_years, weight_kg, medication_name, prescribed_dose_mg } = body;
    if (!medication_name || prescribed_dose_mg == null) {
      return c.json({ error: 'medication_name y prescribed_dose_mg requeridos' }, 400);
    }
    // TODO: Usar modelo + base de datos de dosis estándar
    return c.json({
      medication_name,
      prescribed_dose_mg,
      recommended_range_mg: null,
      risk_level: 'unknown',
      message: 'Configurar lógica de dosis y límites. Stub.',
      stub: true,
    });
  } catch (err) {
    return c.json({ error: 'Error interno' }, 500);
  }
});

// 5. Asistente contextual (chat)
aiRouter.post('/assistant', authMiddleware, async (c) => {
  if (c.env.AI_ENABLED !== 'true') return aiDisabled(c);
  try {
    const body = await c.req.json();
    const { prompt, context } = body;
    if (!prompt) return c.json({ error: 'prompt requerido' }, 400);
    // TODO: Llamar a Gemini para respuesta generativa
    return c.json({
      reply: 'Este es un stub. Configure Gemini para respuestas reales.',
      prompt,
      context_used: context || null,
      stub: true,
    });
  } catch (err) {
    return c.json({ error: 'Error interno' }, 500);
  }
});

export default aiRouter;
