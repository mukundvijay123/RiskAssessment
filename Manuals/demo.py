from sqlalchemy import create_engine, text
from collections import defaultdict
import json

# Supabase credentials
DB_USER = "postgres.oucktnjljscewmgoukzd"
DB_PASSWORD = "Ey-cat$2025"
DB_HOST = "aws-0-ap-south-1.pooler.supabase.com"
DB_PORT = 6543
DB_NAME = "postgres"

# Full SQLAlchemy connection URL (with SSL)
DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    f"?sslmode=require"
)

# Create engine with connection pool
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
connection = engine.connect()

# Replace with your actual UUID
org_id = "48510da2-30a0-4bba-9ea5-ed07c11cb347"

# Raw SQL query

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


result = connection.execute(query, {"org_id": org_id}).mappings()

# Build nested JSON
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

connection.close()

# Output
print(json.dumps(json_data, indent=2))
