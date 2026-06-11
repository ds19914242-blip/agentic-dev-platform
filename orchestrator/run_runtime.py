from pathlib import Path

from orchestrator.graph_runtime import GraphRuntime
from orchestrator.run_status import write_status, append_event
from orchestrator.run_artifacts import register_artifact


class RunRuntime:
    def __init__(
        self,
        run_dir,
        run_id=None,
        product=None,
        request=None,
        run_type="feature",
    ):
        self.run_dir = Path(run_dir)

        self.graph = GraphRuntime(
            run_dir=self.run_dir,
            run_id=run_id,
            product=product,
            request=request,
            run_type=run_type,
        )

    def add_stage(self, stage_id, name):
        self.graph.add(stage_id, name)
        self.graph.write()

    def start_stage(self, stage_id):
        self.graph.start(stage_id)
        self.graph.write()

    def complete_stage(self, stage_id, artifacts=None):
        self.graph.complete(stage_id, artifacts=artifacts)
        self.graph.write()

    def fail_stage(self, stage_id, error=None, artifacts=None):
        self.graph.fail(
            stage_id,
            error=error,
            artifacts=artifacts,
        )
        self.graph.write()

    def skip_stage(self, stage_id):
        self.graph.skip(stage_id)
        self.graph.write()

    def artifact(self, name, path=None, kind=None, stage=None):
        return register_artifact(
            self.run_dir,
            name=name,
            path=path,
            kind=kind,
            stage=stage,
        )

    def event(self, text):
        append_event(self.run_dir, text)

    def status(self, status):
        write_status(self.run_dir, status)

    def write(self):
        self.graph.write()
