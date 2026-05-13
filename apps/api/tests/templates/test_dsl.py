from app.templates.dsl import Ontology, ReportSection, WorkflowStep, WorkshopTemplateDSL


def test_workflow_step_defaults():
    step = WorkflowStep(id=1, name="Test", agent_name="Agent")
    assert step.status == "pending"
    assert step.depends_on == []


def test_ontology_defaults():
    o = Ontology()
    assert o.concepts == []
    assert o.relationships == []


def test_report_section_validation():
    section = ReportSection(title="Findings", type="chart", source_steps=[1, 2])
    assert section.type == "chart"


def test_template_dependency_resolution():
    template = WorkshopTemplateDSL(
        id="t1",
        name="Test",
        description="Desc",
        workflow_steps=[
            WorkflowStep(id=1, name="S1", agent_name="A1"),
            WorkflowStep(id=2, name="S2", agent_name="A2", depends_on=[1]),
            WorkflowStep(id=3, name="S3", agent_name="A3", depends_on=[1, 2]),
        ],
        ontology=Ontology(),
        output_types=[],
        report_structure=[],
    )
    assert template.get_dependencies(2) == [1]
    assert template.get_dependents(1) == [2, 3]
    assert template.get_step(99) is None
