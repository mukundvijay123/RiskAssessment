from fastapi import APIRouter, Depends,HTTPException,status,Query,Response
from sqlalchemy.orm import Session
from sqlalchemy import text
from .db import get_db 
from io import BytesIO
from reportlab.lib.pagesizes import A4 
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from .models import SubDeptRequest
from uuid import UUID
from textwrap import wrap

ManualsRouter = APIRouter(prefix="/api/bcm-manual")
@ManualsRouter.get("/bcm-structure")
def get_bcm_structure(org_id: str = Query(..., description="Organization UUID"), db: Session = Depends(get_db)):
    try:
        # Validate org_id format (optional UUID pattern check)
        if not org_id or len(org_id) != 36:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid org_id format")

        # SQL query
        query = text("""
        SELECT DISTINCT ON (sd.id, p.name)
          d.id AS department_id,
          d.name AS department_name,
          sd.id AS subdepartment_id,
          sd.name AS subdepartment_name,
          p.id AS process_id,
          p.name AS critical_function_name,
          bp.description,
          bp.spoc,
          mor.primary_spoc,
          mor.fallback_spoc,
          mor.it_applications,
          mor.vendor_name,
          rs.people_unavailability_strategy,
          rs.technology_data_unavailability_strategy,
          rs.site_unavailability_strategy,
          rs.third_party_vendors_unavailability_strategy
        FROM department d
        JOIN subdepartment sd ON sd.department_id = d.id
        JOIN process p ON p.subdepartment_id = sd.id
        JOIN bia_process_info bp ON bp.process_id = p.id
        LEFT JOIN recovery_strategies rs ON rs.process_id = bp.id
        LEFT JOIN minimum_operating_requirement mor ON mor.process_id = bp.id
        WHERE d.organization_id = :org_id
        ORDER BY sd.id, p.name, p.id;
        """)

        result = db.execute(query, {"org_id": org_id}).mappings()

        json_data = {"departments": []}
        dept_map = {}

        for row in result:
            dept_id = str(row["department_id"])
            sub_id = str(row["subdepartment_id"])
            proc_id = str(row["process_id"])

            # Department
            if dept_id not in dept_map:
                dept_obj = {
                    "id": dept_id,
                    "name": row["department_name"],
                    "sub_departments": []
                }
                dept_map[dept_id] = dept_obj
                json_data["departments"].append(dept_obj)

            # Subdepartment
            sub_map = {s["id"]: s for s in dept_map[dept_id]["sub_departments"]}
            if sub_id not in sub_map:
                sub_obj = {
                    "id": sub_id,
                    "name": row["subdepartment_name"],
                    "critical_functions": []
                }
                dept_map[dept_id]["sub_departments"].append(sub_obj)
            else:
                sub_obj = sub_map[sub_id]

            # Critical function
            critical_fn = {
                "name": row["critical_function_name"],
                "description": row["description"],
                "recovery_strategy": ", ".join(filter(None, [
                    row["people_unavailability_strategy"],
                    row["technology_data_unavailability_strategy"],
                    row["site_unavailability_strategy"],
                    row["third_party_vendors_unavailability_strategy"]
                ])) or None,
                "dependencies": list(filter(None, [
                    row["it_applications"],
                    row["vendor_name"]
                ])),
                "contacts": list(filter(None, [
                    {"name": row["spoc"], "role": "SPOC"} if row["spoc"] else None,
                    {"name": row["primary_spoc"], "role": "Primary SPOC"} if row["primary_spoc"] else None,
                    {"name": row["fallback_spoc"], "role": "Fallback SPOC"} if row["fallback_spoc"] else None,
                ]))
            }

            sub_obj["critical_functions"].append(critical_fn)

        if not json_data["departments"]:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No departments found for the given org_id")

        return json_data

    except HTTPException as e:
        raise e  # Let FastAPI handle known errors
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    

@ManualsRouter.get("/bcm-manual/pdf", response_class=Response)
def download_bcm_manual_pdf(
    org_id: str = Query(..., description="Organization UUID"),
    db: Session = Depends(get_db),
):
    query = text("""
    SELECT DISTINCT ON (sd.id, p.name)
      d.name AS department_name,
      sd.name AS subdepartment_name,
      p.name AS critical_function_name,
      bp.description,
      bp.spoc,
      mor.primary_spoc,
      mor.fallback_spoc,
      mor.it_applications,
      mor.vendor_name,
      rs.people_unavailability_strategy,
      rs.technology_data_unavailability_strategy,
      rs.site_unavailability_strategy,
      rs.third_party_vendors_unavailability_strategy
    FROM department d
    JOIN subdepartment sd ON sd.department_id = d.id
    JOIN process p ON p.subdepartment_id = sd.id
    JOIN bia_process_info bp ON bp.process_id = p.id
    LEFT JOIN recovery_strategies rs ON rs.process_id = bp.id
    LEFT JOIN minimum_operating_requirement mor ON mor.process_id = bp.id
    WHERE d.organization_id = :org_id
    ORDER BY sd.id, p.name, p.id;
    """)

    try:
        results = db.execute(query, {"org_id": org_id}).mappings().all()
        if not results:
            raise HTTPException(status_code=404, detail="No data found for this org ID")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    left_margin = inch * 0.75
    right_margin = inch * 0.75
    usable_width = width - left_margin - right_margin
    y = height - inch

    font_name = "Helvetica"
    font_size = 10
    line_height = 12

    def draw_wrapped_text(text, indent=0, font=font_name, size=font_size, lh=line_height):
        nonlocal y
        pdf.setFont(font, size)
        lines = wrap(text, width=int((usable_width - indent) / (size * 0.6)))
        for line in lines:
            if y < inch:
                pdf.showPage()
                y = height - inch
                pdf.setFont("Helvetica-Bold", 16)
                pdf.drawString(left_margin, y, "Business Continuity Manual")
                y -= 30
                pdf.setFont(font, size)
            pdf.drawString(left_margin + indent, y, line)
            y -= lh

    # Title
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(left_margin, y, "Business Continuity Manual")
    y -= 30
    pdf.setFont(font_name, font_size)

    current_dept = current_sub = ""

    for row in results:
        if row["department_name"] != current_dept:
            current_dept = row["department_name"]
            draw_wrapped_text(f"Department: {current_dept}", indent=0, font="Helvetica-Bold", size=12)

        if row["subdepartment_name"] != current_sub:
            current_sub = row["subdepartment_name"]
            draw_wrapped_text(f"Sub-department: {current_sub}", indent=20)

        draw_wrapped_text(f"Function: {row['critical_function_name']}", indent=40)

        if row["description"]:
            draw_wrapped_text(f"Description: {row['description']}", indent=60)

        strategies = list(filter(None, [
            row["people_unavailability_strategy"],
            row["technology_data_unavailability_strategy"],
            row["site_unavailability_strategy"],
            row["third_party_vendors_unavailability_strategy"]
        ]))
        if strategies:
            draw_wrapped_text("Recovery Strategy:", indent=60)
            for strategy in strategies:
                draw_wrapped_text(f"- {strategy}", indent=80)

        dependencies = list(filter(None, [row["it_applications"], row["vendor_name"]]))
        if dependencies:
            draw_wrapped_text("Dependencies:", indent=60)
            for dep in dependencies:
                draw_wrapped_text(f"- {dep}", indent=80)

        contacts = list(filter(None, [
            f"SPOC: {row['spoc']}" if row["spoc"] else None,
            f"Primary SPOC: {row['primary_spoc']}" if row["primary_spoc"] else None,
            f"Fallback SPOC: {row['fallback_spoc']}" if row["fallback_spoc"] else None,
        ]))
        if contacts:
            draw_wrapped_text("Contacts:", indent=60)
            for contact in contacts:
                draw_wrapped_text(f"- {contact}", indent=80)

        y -= 10

    pdf.save()
    buffer.seek(0)
    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=BCM_Manual.pdf"}
    )

@ManualsRouter.get("/subdept-pdf", response_class=Response)
def generate_subdept_pdf(
    org_id: UUID = Query(..., description="Organization ID"),
    subdept_id: UUID = Query(..., description="Sub-department ID"),
    db: Session = Depends(get_db)
):
    query = text("""
        SELECT DISTINCT ON (sd.id, p.name)
            d.name AS department_name,
            sd.name AS subdepartment_name,
            p.name AS critical_function_name,
            bp.description,
            bp.spoc,
            mor.primary_spoc,
            mor.fallback_spoc,
            mor.it_applications,
            mor.vendor_name,
            rs.people_unavailability_strategy,
            rs.technology_data_unavailability_strategy,
            rs.site_unavailability_strategy,
            rs.third_party_vendors_unavailability_strategy
        FROM department d
        JOIN subdepartment sd ON sd.department_id = d.id
        JOIN process p ON p.subdepartment_id = sd.id
        JOIN bia_process_info bp ON bp.process_id = p.id
        LEFT JOIN recovery_strategies rs ON rs.process_id = bp.id
        LEFT JOIN minimum_operating_requirement mor ON mor.process_id = bp.id
        WHERE d.organization_id = :org_id AND sd.id = :subdept_id
        ORDER BY sd.id, p.name, p.id;
    """)

    try:
        results = db.execute(query, {"org_id": str(org_id), "subdept_id": subdept_id}).mappings().all()
        if not results:
            raise HTTPException(status_code=404, detail="No data found for this sub-department in the organization.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    subdept_name = results[0]["subdepartment_name"]

    # PDF Setup
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    left_margin = inch * 0.75
    right_margin = inch * 0.75
    usable_width = width - left_margin - right_margin
    y = height - inch
    line_height = 14

    def wrap_text(text: str, font: str, size: int, max_width: float):
        """Wrap text into a list of lines."""
        pdf.setFont(font, size)
        words = text.split()
        lines = []
        line = ""
        for word in words:
            test_line = f"{line} {word}".strip()
            if pdf.stringWidth(test_line, font, size) <= max_width:
                line = test_line
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
        return lines

    def draw_wrapped(text: str, indent: float = 0, font: str = "Helvetica", size: int = 10):
        nonlocal y
        lines = wrap_text(text, font, size, usable_width - indent)
        for line in lines:
            if y < inch:
                pdf.showPage()
                y = height - inch
                pdf.setFont(font, size)
            pdf.drawString(left_margin + indent, y, line)
            y -= line_height

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(left_margin, y, f"BCM Plan for Sub-Department: {subdept_name}")
    y -= 2 * line_height

    for row in results:
        draw_wrapped(f"Function: {row['critical_function_name']}", font="Helvetica-Bold", size=12)

        if row["description"]:
            draw_wrapped(f"Description: {row['description']}", indent=20)

        strategies = list(filter(None, [
            row["people_unavailability_strategy"],
            row["technology_data_unavailability_strategy"],
            row["site_unavailability_strategy"],
            row["third_party_vendors_unavailability_strategy"]
        ]))
        if strategies:
            draw_wrapped("Recovery Strategies:", indent=20)
            for strategy in strategies:
                draw_wrapped(f"- {strategy}", indent=40)

        dependencies = list(filter(None, [row["it_applications"], row["vendor_name"]]))
        if dependencies:
            draw_wrapped("Dependencies:", indent=20)
            for dep in dependencies:
                draw_wrapped(f"- {dep}", indent=40)

        contacts = list(filter(None, [
            f"SPOC: {row['spoc']}" if row["spoc"] else None,
            f"Primary SPOC: {row['primary_spoc']}" if row["primary_spoc"] else None,
            f"Fallback SPOC: {row['fallback_spoc']}" if row["fallback_spoc"] else None
        ]))
        if contacts:
            draw_wrapped("Contacts:", indent=20)
            for contact in contacts:
                draw_wrapped(f"- {contact}", indent=40)

        y -= line_height

    pdf.save()
    buffer.seek(0)

    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={subdept_name}_BCM_Plan.pdf"
        }
    )