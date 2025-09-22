from datetime import datetime, timedelta
from typing import Dict

SEQUENCE_DAYS = {
    1: 0,  # day 0
    2: 3,  # +3 days
    3: 7,  # +7 days
}

def render_subject(step: int, company_name: str) -> str:
    if step == 1:
        return f"Ideas para tus eventos corporativos – {company_name}"
    if step == 2:
        return f"Seguimiento rápido – {company_name}"
    return f"Cierro el loop – {company_name}"


def render_body(step: int, contact_name: str, company_name: str) -> str:
    if step == 1:
        return (
            f"Hola {contact_name or 'equipo'},\n\n"
            "Ayudo a empresas MICE a diseñar y ejecutar incentivos y eventos que generan pipeline y retención."
            "\n\nTengo 3 ideas rápidas adaptadas a {company_name}. Si tiene sentido, puedo compartir un deck breve y un calendario."
            "\n\n¿Te parece si coordinamos una llamada de 15 minutos esta semana?\n\nSaludos,\n"
        )
    if step == 2:
        return (
            f"Hola {contact_name or 'equipo'},\n\n"
            "Solo para mantener el hilo vivo. Podemos encargarnos de end-to-end (sourcing de venues, logística, agenda, patrocinios)."
            "\n\n¿Quieres que te envíe 2-3 casos relevantes y presupuesto estimado?\n\nSaludos,\n"
        )
    q = (datetime.now().month - 1) // 3 + 1
    return (
        f"Hola {contact_name or 'equipo'},\n\n"
        f"Cierro el loop por ahora. Si en Q{q} están evaluando proveedores para eventos/incentivos,"
        " me encantaría aplicar.\n\n¿Te dejo material para cuando lo necesites?\n\nGracias,\n"
    )


def schedule_dates(start_date: datetime) -> Dict[int, datetime]:
    return {step: start_date + timedelta(days=offset) for step, offset in SEQUENCE_DAYS.items()}
