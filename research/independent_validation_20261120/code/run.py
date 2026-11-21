#!/usr/bin/env python3
"""Run the continuation without changing upstream hypotheses or upstream generated outputs."""
import os,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
SCRIPTS=['validate.py','maxT.py','semantic_sensitivity.py','nested_prediction.py','audit_reported.py','decoy_recount.py','annotate_signs.py','prepare_blinded.py','check_outputs.py']
def main():
    env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',VECLIB_MAXIMUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1');start=time.monotonic()
    for script in SCRIPTS:
        print('Running '+script,flush=True);subprocess.run([sys.executable,str(HERE/script)],check=True,env=env)
    print('Continuation complete in %.1f seconds'%(time.monotonic()-start))
if __name__=='__main__':main()
