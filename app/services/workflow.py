"""Workflow lifecycle service."""

from uuid import UUID

from app.db.models import Workflow, WorkflowStatus
from app.db.postgres import SessionLocal


async def create_workflow() -> UUID:
    """Create a new workflow row in PENDING status."""
    async with SessionLocal() as session:
        workflow = Workflow(status=WorkflowStatus.PENDING)
        session.add(workflow)
        await session.commit()
        return workflow.id


async def set_workflow_status(workflow_id: UUID, status: WorkflowStatus) -> None:
    """Update a workflow's lifecycle status."""
    async with SessionLocal() as session:
        workflow = await session.get(Workflow, workflow_id)
        if workflow is None:
            raise ValueError(f"Workflow {workflow_id} not found")
        workflow.status = status
        await session.commit()


async def get_workflow(workflow_id: UUID) -> Workflow | None:
    """Fetch a workflow by id."""
    async with SessionLocal() as session:
        return await session.get(Workflow, workflow_id)
