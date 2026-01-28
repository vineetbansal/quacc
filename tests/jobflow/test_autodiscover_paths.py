import pytest
jf = pytest.importorskip("jobflow")

from pathlib import Path
from ase.build import bulk
from quacc import change_settings
from quacc.wflow_tools.context import flow_context


def test_autodiscover_bulk_slabs_paths(tmp_path):
    atoms = bulk("Cu")
    with change_settings({"AUTODISCOVER_DIR": True}):

        from quacc.recipes.emt.slabs import relax_job
        from quacc.atoms.slabs import make_slabs_from_bulk

        slabs = make_slabs_from_bulk(atoms)
        relax_jobs = [relax_job(slab) for slab in slabs]
        flow = jf.Flow(relax_jobs)

        context_name = str(tmp_path)
        with flow_context(context_name):
            jf.run_locally(flow, create_folders=False)

        for i in range(4):
            assert Path(f"{context_name}/relax_job-{i}").exists()
