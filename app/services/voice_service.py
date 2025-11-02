"""
Servicio de texto-a-voz usando ElevenLabs API
"""
import os
from typing import Optional
import requests
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class VoiceSettings(BaseSettings):
    # Configuración de carga de variables de entorno para evitar errores por claves extra en .env
    model_config = ConfigDict(extra='ignore', env_file='.env')

    elevenlabs_api_key: Optional[str] = None
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"  # Rachel - voz profesional femenina

class VoiceService:
    """Servicio para generar audio desde texto usando ElevenLabs"""
    
    def __init__(self):
        self.settings = VoiceSettings()
        self.base_url = "https://api.elevenlabs.io/v1"
    
    def generate_report_speech(self, summary: dict) -> Optional[bytes]:
        """
        Genera audio narrando el resumen del reporte
        """
        if not self.settings.elevenlabs_api_key:
            return None
        
        # Construir texto narrativo del reporte
        texto = self._build_report_narrative(summary)
        
        # Llamar a ElevenLabs API
        url = f"{self.base_url}/text-to-speech/{self.settings.elevenlabs_voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.settings.elevenlabs_api_key
        }
        
        data = {
            "text": texto,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }
        
        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                return response.content
            else:
                print(f"Error ElevenLabs: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error generando voz: {e}")
            return None
    
    def _build_report_narrative(self, summary: dict) -> str:
        """
        Construye narrativa en español del reporte
        """
        cumplimiento = summary.get("porcentaje_cumplimiento", 0)
        total = summary.get("total_items", 0)
        cumplidos = summary.get("items_cumplidos", 0)
        
        # Saludo y resumen general
        if cumplimiento >= 90:
            tono = "Excelente trabajo."
        elif cumplimiento >= 70:
            tono = "Buen desempeño, pero hay áreas de mejora."
        else:
            tono = "Atención: se requiere acción inmediata."
        
        texto = f"{tono} "
        texto += f"El cumplimiento general es del {cumplimiento}%. "
        texto += f"Se completaron {cumplidos} de {total} verificaciones. "
        
        # Detalles por etapa
        etapas = summary.get("cumplimiento_por_etapa", {})
        if etapas:
            texto += "Revisemos por etapa. "
            
            for etapa, datos in etapas.items():
                perc = datos.get("porcentaje", 0)
                if perc < 70:
                    texto += f"En {etapa}, el cumplimiento es crítico: {perc}%. "
                elif perc < 85:
                    texto += f"En {etapa}, hay {perc}% de cumplimiento, podemos mejorar. "
                else:
                    texto += f"En {etapa}, vamos bien con {perc}%. "
        
        return texto

    def get_recommendations(self, summary: dict) -> list:
        """
        Genera recomendaciones basadas en los datos de cumplimiento
        """
        recomendaciones = []
        cumplimiento = summary.get("porcentaje_cumplimiento", 0)
        etapas = summary.get("cumplimiento_por_etapa", {})
        
        # Recomendaciones generales
        if cumplimiento < 70:
            recomendaciones.append({
                "tipo": "critico",
                "titulo": "Acción Inmediata Requerida",
                "descripcion": "El cumplimiento está por debajo del 70%. Se recomienda reunión urgente del equipo para identificar barreras y establecer plan de acción.",
                "icono": "fa-exclamation-triangle"
            })
        elif cumplimiento < 85:
            recomendaciones.append({
                "tipo": "advertencia",
                "titulo": "Mejora Continua Necesaria",
                "descripcion": "El cumplimiento puede mejorar. Considere sesiones de refuerzo y monitoreo más frecuente.",
                "icono": "fa-exclamation-circle"
            })
        else:
            recomendaciones.append({
                "tipo": "exito",
                "titulo": "Excelente Desempeño",
                "descripcion": "El equipo mantiene altos estándares. Continuar con las buenas prácticas y compartir experiencias exitosas.",
                "icono": "fa-check-circle"
            })
        
        # Recomendaciones por etapa
        for etapa, datos in etapas.items():
            perc = datos.get("porcentaje", 0)
            if perc < 70:
                recomendaciones.append({
                    "tipo": "critico",
                    "titulo": f"Reforzar: {etapa.capitalize()}",
                    "descripcion": f"La etapa de {etapa} tiene {perc}% de cumplimiento. Revisar protocolos, capacitar personal y aumentar supervisión.",
                    "icono": "fa-clipboard-list"
                })
            elif perc < 85:
                recomendaciones.append({
                    "tipo": "advertencia",
                    "titulo": f"Optimizar: {etapa.capitalize()}",
                    "descripcion": f"En {etapa} hay oportunidad de mejora ({perc}%). Considerar recordatorios visuales o checklist digitales.",
                    "icono": "fa-tasks"
                })
        
        # Recomendaciones específicas según patrones
        if etapas.get("prescripción", {}).get("porcentaje", 100) < 80:
            recomendaciones.append({
                "tipo": "info",
                "titulo": "Verificación de Prescripciones",
                "descripcion": "Implementar doble verificación en prescripciones. Revisar legibilidad de órdenes médicas y uso de sistema electrónico.",
                "icono": "fa-file-prescription"
            })
        
        if etapas.get("administración", {}).get("porcentaje", 100) < 80:
            recomendaciones.append({
                "tipo": "info",
                "titulo": "Protocolo de Administración",
                "descripcion": "Reforzar los 5 correctos: paciente, medicamento, dosis, vía, hora. Considerar pausas activas para reducir fatiga.",
                "icono": "fa-syringe"
            })
        
        return recomendaciones
