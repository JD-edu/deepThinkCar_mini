# Legacy sample model warning

`lane_navigation_final.h5` in this directory is an old course sample artifact.
It is kept only to preserve the upstream repository history and must not be
copied to the Raspberry Pi as the result of a new training run.

The current training script requires a new `--output-dir` and writes
`lane_navigation_candidate.h5`. Promote a candidate to
`models/lane_navigation_final.h5` only after an untouched driving video has
been used to compare it with the current deployed model.

`lane_navigation_best_normalized_do_not_deploy.keras` is an internal training
checkpoint whose output is normalized, not degrees. The runtime loader must
never receive that checkpoint.
