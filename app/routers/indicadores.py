"""
Router para Indicadores de Calidad
Endpoints para calcular y obtener indicadores CLMC y TEAEM
"""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.indicadores_service import IndicadoresService

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/indicadores-calidad", response_class=HTMLResponse)
async def indicadores_page(request: Request):
    """Página principal de indicadores"""
    return templates.TemplateResponse(
        "indicadores_calidad.html",
        {"request": request}
    )


@router.get("/api/indicadores/clmc")
async def get_clmc(dias: int = 30, db: Session = Depends(get_db)):
    """
    Obtiene el indicador CLMC calculado
    Query params:
    - dias: período de cálculo (default: 30)
    """
    try:
        resultado = IndicadoresService.calcular_clmc(db, dias)
        return JSONResponse(content=resultado)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/api/indicadores/teaem")
async def get_teaem(dias: int = 30, db: Session = Depends(get_db)):
    """
    Obtiene el indicador TEAEM calculado
    Query params:
    - dias: período de cálculo (default: 30)
    """
    try:
        resultado = IndicadoresService.calcular_teaem(db, dias)
        return JSONResponse(content=resultado)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/api/indicadores/por-correcto")
async def get_por_correcto(dias: int = 30, db: Session = Depends(get_db)):
    """
    Obtiene el análisis de cumplimiento por cada uno de los 10 correctos
    Query params:
    - dias: período de análisis (default: 30)
    """
    try:
        resultado = IndicadoresService.analisis_por_correcto(db, dias)
        return JSONResponse(content=resultado)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/api/indicadores/tendencia")
async def get_tendencia(semanas: int = 4, db: Session = Depends(get_db)):
    """
    Obtiene la tendencia semanal de los indicadores
    Query params:
    - semanas: número de semanas a analizar (default: 4)
    """
    try:
        resultado = IndicadoresService.tendencia_semanal(db, semanas)
        return JSONResponse(content=resultado)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/api/indicadores/resumen")
async def get_resumen(dias: int = 30, db: Session = Depends(get_db)):
    """
    Obtiene un resumen completo de todos los indicadores
    """
    try:
        clmc = IndicadoresService.calcular_clmc(db, dias)
        teaem = IndicadoresService.calcular_teaem(db, dias)
        por_correcto = IndicadoresService.analisis_por_correcto(db, dias)
        tendencia = IndicadoresService.tendencia_semanal(db, 4)
        
        return JSONResponse(content={
            "clmc": clmc,
            "teaem": teaem,
            "por_correcto": por_correcto,
            "tendencia": tendencia
        })
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
