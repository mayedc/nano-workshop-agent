import logging
from pathlib import Path

import yaml

from app.templates.dsl import WorkshopTemplateDSL

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).parents[3] / "templates" / "workshop"


class TemplateRegistry:
    _templates: dict[str, WorkshopTemplateDSL] = {}

    @classmethod
    def load_all(cls) -> list[WorkshopTemplateDSL]:
        cls._templates.clear()
        if not TEMPLATES_DIR.exists():
            logger.warning("Templates directory not found: %s", TEMPLATES_DIR)
            return []

        loaded: list[WorkshopTemplateDSL] = []
        for file_path in TEMPLATES_DIR.glob("*.yaml"):
            try:
                template = cls._load_file(file_path)
                cls._templates[template.id] = template
                loaded.append(template)
                logger.info("Loaded template: %s (%s)", template.id, template.name)
            except Exception as e:
                logger.error("Failed to load template %s: %s", file_path, e)

        return loaded

    @classmethod
    def _load_file(cls, path: Path) -> WorkshopTemplateDSL:
        with open(path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        if not raw:
            raise ValueError(f"Empty template file: {path}")
        return WorkshopTemplateDSL.model_validate(raw)

    @classmethod
    def get(cls, template_id: str) -> WorkshopTemplateDSL | None:
        return cls._templates.get(template_id)

    @classmethod
    def list_ids(cls) -> list[str]:
        return list(cls._templates.keys())

    @classmethod
    def all(cls) -> list[WorkshopTemplateDSL]:
        return list(cls._templates.values())


def load_and_validate_templates() -> list[WorkshopTemplateDSL]:
    return TemplateRegistry.load_all()
