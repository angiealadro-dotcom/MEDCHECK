import { sql } from 'drizzle-orm';
import { sqliteTable, text, integer } from 'drizzle-orm/sqlite-core';

// Organizations Table
export const organizations = sqliteTable('organizations', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  name: text('name').notNull(),
  slug: text('slug').notNull().unique(),
  contactEmail: text('contact_email').notNull(),
  contactPhone: text('contact_phone'),
  institutionType: text('institution_type'),
  country: text('country'),
  city: text('city'),
  address: text('address'),
  isActive: integer('is_active', { mode: 'boolean' }).default(true),
  plan: text('plan', { enum: ['free', 'pro', 'enterprise'] }).default('free'),
  maxUsers: integer('max_users').default(5),
  createdAt: text('created_at').default(sql`(datetime('now'))`),
  updatedAt: text('updated_at').default(sql`(datetime('now'))`),
  trialEndsAt: text('trial_ends_at'),
  logoUrl: text('logo_url'),
  primaryColor: text('primary_color').default('#0d6efd'),
});

// Users Table
export const users = sqliteTable('users', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  email: text('email').notNull().unique(),
  username: text('username').notNull().unique(),
  hashedPassword: text('hashed_password').notNull(),
  fullName: text('full_name'),
  isActive: integer('is_active', { mode: 'boolean' }).default(true),
  isAdmin: integer('is_admin', { mode: 'boolean' }).default(false),
  isSuperAdmin: integer('is_super_admin', { mode: 'boolean' }).default(false),
  organizationId: integer('organization_id').notNull().references(() => organizations.id),
  createdAt: text('created_at').default(sql`(datetime('now'))`),
});

// Checklist Entries Table
export const checklistEntries = sqliteTable('checklist_entries', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  fechaHora: text('fecha_hora').default(sql`(datetime('now'))`),
  area: text('area'),
  turno: text('turno'),
  protocoloEtapa: text('protocolo_etapa'),
  item: text('item'),
  cumple: integer('cumple', { mode: 'boolean' }),
  observaciones: text('observaciones'),
  usuario: text('usuario'),
  metadatos: text('metadatos'),
  // Los 10 Correctos
  pacienteCorrecto: integer('paciente_correcto', { mode: 'boolean' }).default(false),
  medicamentoCorrecto: integer('medicamento_correcto', { mode: 'boolean' }).default(false),
  dosisCorrecta: integer('dosis_correcta', { mode: 'boolean' }).default(false),
  viaCorrecta: integer('via_correcta', { mode: 'boolean' }).default(false),
  horaCorrecta: integer('hora_correcta', { mode: 'boolean' }).default(false),
  fechaVencimientoVerificada: integer('fecha_vencimiento_verificada', { mode: 'boolean' }).default(false),
  educacionPaciente: integer('educacion_paciente', { mode: 'boolean' }).default(false),
  registroCorrecto: integer('registro_correcto', { mode: 'boolean' }).default(false),
  alergiasVerificadas: integer('alergias_verificadas', { mode: 'boolean' }).default(false),
  responsabilidadPersonal: integer('responsabilidad_personal', { mode: 'boolean' }).default(false),
  // Multi-tenancy
  organizationId: integer('organization_id').notNull().references(() => organizations.id),
  createdAt: text('created_at').default(sql`(datetime('now'))`),
});

// Reminders Table
export const reminders = sqliteTable('reminders', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  userId: integer('user_id').notNull().references(() => users.id),
  title: text('title').notNull(),
  body: text('body'),
  scheduledAt: text('scheduled_at').notNull(),
  sentAt: text('sent_at'),
  active: integer('active', { mode: 'boolean' }).default(true),
  createdAt: text('created_at').default(sql`(datetime('now'))`),
  organizationId: integer('organization_id').notNull().references(() => organizations.id),
});

// WebPush Subscriptions Table
export const webpushSubscriptions = sqliteTable('webpush_subscriptions', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  userId: integer('user_id').notNull().references(() => users.id),
  endpoint: text('endpoint').notNull().unique(),
  p256dh: text('p256dh').notNull(),
  auth: text('auth').notNull(),
  createdAt: text('created_at').default(sql`(datetime('now'))`),
});

// Medication Errors Table
// Registra eventos de errores de medicación para análisis de calidad y tasa de errores
// Un error puede estar asociado a un checklist_entry (administración) o reportarse independiente
export const medicationErrors = sqliteTable('medication_errors', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  organizationId: integer('organization_id').notNull().references(() => organizations.id),
  reportedByUserId: integer('reported_by_user_id').notNull().references(() => users.id),
  checklistEntryId: integer('checklist_entry_id').references(() => checklistEntries.id),
  errorType: text('error_type').notNull(), // p.ej: 'dosis', 'paciente', 'medicamento', 'via', 'hora', 'alergia', 'otro'
  severity: text('severity', { enum: ['near_miss', 'minor', 'moderate', 'severe', 'sentinel'] }).notNull(),
  stage: text('stage', { enum: ['prescription', 'transcription', 'dispensing', 'administration', 'monitoring'] }).notNull(),
  description: text('description'),
  contributingFactors: text('contributing_factors'), // texto libre (fatiga, ambiente, comunicación, etc.)
  occurredAt: text('occurred_at').default(sql`(datetime('now'))`),
  detectedAt: text('detected_at').default(sql`(datetime('now'))`),
  resolved: integer('resolved', { mode: 'boolean' }).default(false),
  resolutionNotes: text('resolution_notes'),
  createdAt: text('created_at').default(sql`(datetime('now'))`),
});

// TypeScript Types
export type Organization = typeof organizations.$inferSelect;
export type User = typeof users.$inferSelect;
export type ChecklistEntry = typeof checklistEntries.$inferSelect;
export type Reminder = typeof reminders.$inferSelect;
export type WebPushSubscription = typeof webpushSubscriptions.$inferSelect;
export type MedicationError = typeof medicationErrors.$inferSelect;

export type NewOrganization = typeof organizations.$inferInsert;
export type NewUser = typeof users.$inferInsert;
export type NewChecklistEntry = typeof checklistEntries.$inferInsert;
export type NewReminder = typeof reminders.$inferInsert;
export type NewWebPushSubscription = typeof webpushSubscriptions.$inferInsert;
export type NewMedicationError = typeof medicationErrors.$inferInsert;
