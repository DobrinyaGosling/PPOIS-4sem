from src.model.department import VirtualDepartment
from src.model.entities import Material
from src.model.exceptions import ValidationError
from src.view.utils import new_id


def add_material(dept: VirtualDepartment, title: str, content: str) -> Material:
    title = title.strip()
    content = content.strip()
    if not title or not content:
        raise ValidationError("title and content are required")
    material = Material(material_id=new_id("mat"), title=title, content=content)
    dept.materials[material.material_id] = material
    return material


def list_materials(dept: VirtualDepartment) -> list[Material]:
    return list(dept.materials.values())

