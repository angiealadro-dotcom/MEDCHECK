"""
Servicio para cálculo de Indicadores de Calidad
- CLMC: Cumplimiento del Uso de Lista de Cotejo MedCheck
- TEAEM: Tasa de Eventos Adversos por Errores de Medicación
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models.checklist_entry import ChecklistEntrySQL
from datetime import datetime, timedelta
from typing import Dict, List, Any


class IndicadoresService:
    
    @staticmethod
    def calcular_clmc(db: Session, dias: int = 30) -> Dict[str, Any]:
        """
        Calcula el indicador CLMC (Cumplimiento de Lista de Cotejo MedCheck)
        
        Fórmula: CLMC (%) = (Formatos MedCheck Completos / Total de Administraciones) × 100
        
        Un formato se considera completo si tiene TODOS los 10 correctos marcados como True
        """
        fecha_inicio = datetime.utcnow() - timedelta(days=dias)
        
        # Total de administraciones (entradas donde protocolo_etapa = 'administracion')
        total_administraciones = db.query(ChecklistEntrySQL).filter(
            and_(
                ChecklistEntrySQL.fecha_hora >= fecha_inicio,
                ChecklistEntrySQL.protocolo_etapa == 'administracion'
            )
        ).count()
        
        # Administraciones con checklist completo (todos los 10 correctos = True)
        formatos_completos = db.query(ChecklistEntrySQL).filter(
            and_(
                ChecklistEntrySQL.fecha_hora >= fecha_inicio,
                ChecklistEntrySQL.protocolo_etapa == 'administracion',
                ChecklistEntrySQL.paciente_correcto == True,
                ChecklistEntrySQL.medicamento_correcto == True,
                ChecklistEntrySQL.dosis_correcta == True,
                ChecklistEntrySQL.via_correcta == True,
                ChecklistEntrySQL.hora_correcta == True,
                ChecklistEntrySQL.fecha_vencimiento_verificada == True,
                ChecklistEntrySQL.educacion_paciente == True,
                ChecklistEntrySQL.registro_correcto == True,
                ChecklistEntrySQL.alergias_verificadas == True,
                ChecklistEntrySQL.responsabilidad_personal == True
            )
        ).count()
        
        # Calcular porcentaje
        clmc_porcentaje = (formatos_completos / total_administraciones * 100) if total_administraciones > 0 else 0
        
        # Determinar nivel de calidad
        if clmc_porcentaje >= 90:
            nivel = "Óptimo"
            color = "success"
        elif clmc_porcentaje >= 80:
            nivel = "Zona de Alerta"
            color = "warning"
        else:
            nivel = "Fuera de Control"
            color = "danger"
        
        return {
            "indicador": "CLMC",
            "nombre": "Cumplimiento del Uso de la Lista de Cotejo Digital MedCheck",
            "valor": round(clmc_porcentaje, 2),
            "numerador": formatos_completos,
            "denominador": total_administraciones,
            "meta": 90.0,
            "nivel": nivel,
            "color": color,
            "periodo_dias": dias
        }
    
    @staticmethod
    def calcular_teaem(db: Session, dias: int = 30) -> Dict[str, Any]:
        """
        Calcula el indicador TEAEM (Tasa de Eventos Adversos por Errores de Medicación)
        
        Fórmula: TEAEM (%) = (Eventos con Incumplimiento ≥1 Correcto / Total de Administraciones) × 100
        
        Un evento adverso se considera cuando AL MENOS UNO de los 10 correctos es False
        """
        fecha_inicio = datetime.utcnow() - timedelta(days=dias)
        
        # Total de administraciones
        total_administraciones = db.query(ChecklistEntrySQL).filter(
            and_(
                ChecklistEntrySQL.fecha_hora >= fecha_inicio,
                ChecklistEntrySQL.protocolo_etapa == 'administracion'
            )
        ).count()
        
        # Eventos adversos (al menos un correcto incumplido)
        eventos_adversos = db.query(ChecklistEntrySQL).filter(
            and_(
                ChecklistEntrySQL.fecha_hora >= fecha_inicio,
                ChecklistEntrySQL.protocolo_etapa == 'administracion',
                (
                    (ChecklistEntrySQL.paciente_correcto == False) |
                    (ChecklistEntrySQL.medicamento_correcto == False) |
                    (ChecklistEntrySQL.dosis_correcta == False) |
                    (ChecklistEntrySQL.via_correcta == False) |
                    (ChecklistEntrySQL.hora_correcta == False) |
                    (ChecklistEntrySQL.fecha_vencimiento_verificada == False) |
                    (ChecklistEntrySQL.educacion_paciente == False) |
                    (ChecklistEntrySQL.registro_correcto == False) |
                    (ChecklistEntrySQL.alergias_verificadas == False) |
                    (ChecklistEntrySQL.responsabilidad_personal == False)
                )
            )
        ).count()
        
        # Calcular porcentaje
        teaem_porcentaje = (eventos_adversos / total_administraciones * 100) if total_administraciones > 0 else 0
        
        # Determinar nivel de calidad (menor es mejor para este indicador)
        if teaem_porcentaje <= 2:
            nivel = "Excelencia"
            color = "success"
        elif teaem_porcentaje <= 5:
            nivel = "Aceptable con Vigilancia"
            color = "warning"
        else:
            nivel = "Inaceptable"
            color = "danger"
        
        return {
            "indicador": "TEAEM",
            "nombre": "Tasa de Eventos Adversos por Errores de Medicación",
            "valor": round(teaem_porcentaje, 2),
            "numerador": eventos_adversos,
            "denominador": total_administraciones,
            "meta": 2.0,
            "nivel": nivel,
            "color": color,
            "periodo_dias": dias
        }
    
    @staticmethod
    def analisis_por_correcto(db: Session, dias: int = 30) -> List[Dict[str, Any]]:
        """
        Analiza el cumplimiento de cada uno de los 10 correctos
        """
        fecha_inicio = datetime.utcnow() - timedelta(days=dias)
        
        total = db.query(ChecklistEntrySQL).filter(
            and_(
                ChecklistEntrySQL.fecha_hora >= fecha_inicio,
                ChecklistEntrySQL.protocolo_etapa == 'administracion'
            )
        ).count()
        
        if total == 0:
            return []
        
        correctos = [
            ("paciente_correcto", "Paciente Correcto"),
            ("medicamento_correcto", "Medicamento Correcto"),
            ("dosis_correcta", "Dosis Correcta"),
            ("via_correcta", "Vía Correcta"),
            ("hora_correcta", "Hora Correcta"),
            ("fecha_vencimiento_verificada", "Fecha de Vencimiento"),
            ("educacion_paciente", "Educación al Paciente"),
            ("registro_correcto", "Registro Correcto"),
            ("alergias_verificadas", "Verificación de Alergias"),
            ("responsabilidad_personal", "Responsabilidad Personal")
        ]
        
        resultados = []
        for campo, nombre in correctos:
            cumplidos = db.query(ChecklistEntrySQL).filter(
                and_(
                    ChecklistEntrySQL.fecha_hora >= fecha_inicio,
                    ChecklistEntrySQL.protocolo_etapa == 'administracion',
                    getattr(ChecklistEntrySQL, campo) == True
                )
            ).count()
            
            porcentaje = (cumplidos / total * 100)
            
            resultados.append({
                "nombre": nombre,
                "campo": campo,
                "cumplidos": cumplidos,
                "total": total,
                "porcentaje": round(porcentaje, 2)
            })
        
        return resultados
    
    @staticmethod
    def tendencia_semanal(db: Session, semanas: int = 4) -> Dict[str, List]:
        """
        Calcula la tendencia de los indicadores por semana
        """
        resultados = {
            "semanas": [],
            "clmc": [],
            "teaem": []
        }
        
        for i in range(semanas, 0, -1):
            dias_fin = (i - 1) * 7
            dias_inicio = i * 7
            
            fecha_fin = datetime.utcnow() - timedelta(days=dias_fin)
            fecha_inicio = datetime.utcnow() - timedelta(days=dias_inicio)
            
            # CLMC de la semana
            total_semana = db.query(ChecklistEntrySQL).filter(
                and_(
                    ChecklistEntrySQL.fecha_hora >= fecha_inicio,
                    ChecklistEntrySQL.fecha_hora < fecha_fin,
                    ChecklistEntrySQL.protocolo_etapa == 'administracion'
                )
            ).count()
            
            completos_semana = db.query(ChecklistEntrySQL).filter(
                and_(
                    ChecklistEntrySQL.fecha_hora >= fecha_inicio,
                    ChecklistEntrySQL.fecha_hora < fecha_fin,
                    ChecklistEntrySQL.protocolo_etapa == 'administracion',
                    ChecklistEntrySQL.paciente_correcto == True,
                    ChecklistEntrySQL.medicamento_correcto == True,
                    ChecklistEntrySQL.dosis_correcta == True,
                    ChecklistEntrySQL.via_correcta == True,
                    ChecklistEntrySQL.hora_correcta == True,
                    ChecklistEntrySQL.fecha_vencimiento_verificada == True,
                    ChecklistEntrySQL.educacion_paciente == True,
                    ChecklistEntrySQL.registro_correcto == True,
                    ChecklistEntrySQL.alergias_verificadas == True,
                    ChecklistEntrySQL.responsabilidad_personal == True
                )
            ).count()
            
            eventos_semana = db.query(ChecklistEntrySQL).filter(
                and_(
                    ChecklistEntrySQL.fecha_hora >= fecha_inicio,
                    ChecklistEntrySQL.fecha_hora < fecha_fin,
                    ChecklistEntrySQL.protocolo_etapa == 'administracion',
                    (
                        (ChecklistEntrySQL.paciente_correcto == False) |
                        (ChecklistEntrySQL.medicamento_correcto == False) |
                        (ChecklistEntrySQL.dosis_correcta == False) |
                        (ChecklistEntrySQL.via_correcta == False) |
                        (ChecklistEntrySQL.hora_correcta == False) |
                        (ChecklistEntrySQL.fecha_vencimiento_verificada == False) |
                        (ChecklistEntrySQL.educacion_paciente == False) |
                        (ChecklistEntrySQL.registro_correcto == False) |
                        (ChecklistEntrySQL.alergias_verificadas == False) |
                        (ChecklistEntrySQL.responsabilidad_personal == False)
                    )
                )
            ).count()
            
            clmc_valor = (completos_semana / total_semana * 100) if total_semana > 0 else 0
            teaem_valor = (eventos_semana / total_semana * 100) if total_semana > 0 else 0
            
            resultados["semanas"].append(f"Semana -{i}")
            resultados["clmc"].append(round(clmc_valor, 2))
            resultados["teaem"].append(round(teaem_valor, 2))
        
        return resultados
