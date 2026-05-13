import pytest

from app.templates.dsl import Ontology, WorkflowStep, WorkshopTemplateDSL
from app.templates.loader import TemplateRegistry, load_and_validate_templates


def test_load_all_templates():
    templates = load_and_validate_templates()
    assert len(templates) >= 3
    ids = [t.id for t in templates]
    assert "ehmi_design_workshop" in ids
    assert "ux_research_workshop" in ids
    assert "policy_stakeholder_workshop" in ids


def test_get_template():
    load_and_validate_templates()
    t = TemplateRegistry.get("ehmi_design_workshop")
    assert t is not None
    assert t.name == "eHMI Design Workshop"
    assert len(t.input_roles) > 0
    assert len(t.analysis_modules) > 0


def test_template_workflow_steps():
    load_and_validate_templates()
    t = TemplateRegistry.get("ux_research_workshop")
    assert t is not None
    assert len(t.workflow_steps) > 0
    step = t.workflow_steps[0]
    assert step.id == 1
    assert step.name
    assert step.agent_name


def test_template_ontology():
    load_and_validate_templates()
    t = TemplateRegistry.get("policy_stakeholder_workshop")
    assert t is not None
    assert len(t.ontology.concepts) > 0
    assert len(t.ontology.participant_groups) > 0


def test_dsl_model_validation():
    data = {
        "id": "test_workshop",
        "name": "Test Workshop",
        "description": "A test",
        "input_roles": ["role1"],
        "analysis_modules": ["module1"],
        "workflow_steps": [
            {"id": 1, "name": "Step 1", "agent_name": "Agent1", "depends_on": []},
            {"id": 2, "name": "Step 2", "agent_name": "Agent2", "depends_on": [1]},
        ],
        "ontology": {
            "concepts": ["concept1"],
            "participant_groups": ["group1"],
        },
        "output_types": ["report"],
        "report_structure": [
            {"title": "Summary", "type": "text", "source_steps": [1]},
        ],
    }
    template = WorkshopTemplateDSL.model_validate(data)
    assert template.id == "test_workshop"
    assert len(template.workflow_steps) == 2


def test_dsl_invalid_step_dependency():
    data = {
        "id": "bad",
        "name": "Bad",
        "description": "Bad workshop",
        "workflow_steps": [
            {"id": 1, "name": "Step 1", "agent_name": "Agent1", "depends_on": [99]},
        ],
        "ontology": {},
        "output_types": [],
        "report_structure": [],
    }
    with pytest.raises(ValueError):
        WorkshopTemplateDSL.model_validate(data)


def test_dsl_invalid_step_status():
    with pytest.raises(ValueError):
        WorkflowStep(id=1, name="Step", agent_name="Agent", status="invalid")


def test_dsl_invalid_report_type():
    with pytest.raises(ValueError):
        from app.templates.dsl import ReportSection
        ReportSection(title="Bad", type="invalid", source_steps=[])
