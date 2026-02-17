from pprint import pprint
import jobflow as jf
from jobflow_remote import submit_flow

from mypackage import hypot


if __name__ == "__main__":
    workflow = hypot(3, 4)

    # Run locally
    # responses = jf.run_locally(workflow)
    # pprint(responses)

    # Run on slurm
    ids = submit_flow(workflow, worker="slurm")
    print(ids)
