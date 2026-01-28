import os
from ase.build import bulk
from quacc import change_settings
from pathlib import Path


def test_autodiscover_bulk_slabs_paths():
    atoms = bulk("Cu")
    with change_settings({"AUTODISCOVER_DIR": True}):

        # Make sure we import the `@flow` inside the context manager after
        # changing settings!
        from quacc.recipes.emt.slabs import bulk_to_slabs_flow

        bulk_to_slabs_flow(atoms)

        results_dir = os.environ["QUACC_RESULTS_DIR"]
        for i in range(4):
            assert Path(f"{results_dir}/bulk_to_slabs_flow/bulk_to_slabs_subflow/relax_job-{i}").exists()
            assert Path(f"{results_dir}/bulk_to_slabs_flow/bulk_to_slabs_subflow/static_job-{i}").exists()