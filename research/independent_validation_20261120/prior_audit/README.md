# IVC work-branch audit artifacts

Reviewed commit: 8259c47fdf4a076f04029254f97c83f04abb139e.

The analysis is in ivc-work-branch-analysis.md. No repository code was changed.

Run against a checkout containing the referenced committed data:

```sh
python3.11 ivc_audit.py --repo /path/to/ivc --output ivc-audit-results.json
python3 ivc_model_check.py --repo /path/to/ivc --output ivc-model-check.json
python3.11 ivc_frontier_check.py --repo /path/to/ivc --output ivc-frontier-check.json
```

The coverage/typology/divisor/syntax audit and whole-seal frontier check require only the standard library. The model check additionally requires NumPy. The model check extracts four scoring functions from the repository by AST and evaluates committed clusters; it does not refit cluster discovery or rerun the random-merge nulls.

The frontier check reconstructs the repository baseline with its site exclusions, reproduces 8/9 versus 12/48 transition hits, then exhaustively allocates 3 of 19 complete seals to one group. Its 0.077399 result is a whole-object sensitivity test; observational exchangeability and genre differences remain assumptions.

The supplied JSON files are outputs from the checks actually run. The audit file contains the complete list of 40 unseen faces incorrectly counted as fully covered by the master numeric-ID filter. Script syntax results were generated using Python 3.11.13.
