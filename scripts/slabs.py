from pprint import pprint
from ase.build import bulk
import jobflow as jf
from jobflow_remote import submit_flow
from quacc.recipes.emt.slabs import bulk_to_slabs_flow


if __name__ == "__main__":

    atoms = bulk("Cu")
    workflow = bulk_to_slabs_flow(atoms, run_static=False)
  
    # run locally
    # results = jf.run_locally(workflow, ensure_success=True)
    # pprint(results)

    # Run on slurm
    ids = submit_flow(workflow, worker="slurm")
    print(ids)
