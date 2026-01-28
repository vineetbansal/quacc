from ase.build import bulk
from quacc import change_settings


def test_autodiscover_bulk_slabs_paths(tmp_path):
    atoms = bulk("Cu")
    with change_settings({"AUTODISCOVER_DIR": True, "RESULTS_DIR": tmp_path}):

        # Make sure we import the `@flow` inside the context manager after
        # changing settings!
        from quacc.recipes.emt.slabs import bulk_to_slabs_flow

        bulk_to_slabs_flow(atoms)

        for i in range(4):
            assert (tmp_path / f"bulk_to_slabs_flow/bulk_to_slabs_subflow/relax_job-{i}").exists()
            assert (tmp_path / f"bulk_to_slabs_flow/bulk_to_slabs_subflow/static_job-{i}").exists()