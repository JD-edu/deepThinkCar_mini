"""Fine-tune a degree-output steering model on held-out recording runs."""

import argparse
import json
import math
from pathlib import Path

import keras
import numpy as np

from jd_deep_learning import (
    augment_with_horizontal_flip,
    dataset_sha256,
    discover_dataset,
    load_images,
    sha256_file,
    source_run_key,
    split_dataset_by_run_indices,
    steering_region_counts,
)


def fine_tune_model(
    data_directory,
    output_directory,
    base_model_path,
    validation_run_prefixes,
    *,
    epochs=30,
    batch_size=32,
    learning_rate=1e-4,
    seed=20260810,
):
    if not validation_run_prefixes:
        raise ValueError("at least one validation run prefix is required")
    output_directory = Path(output_directory)
    if output_directory.exists() and any(output_directory.iterdir()):
        raise FileExistsError("output directory must be empty: %s" % output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)

    keras.utils.set_random_seed(seed)
    image_paths, angles = discover_dataset(data_directory)
    train_indices, validation_indices, _groups = split_dataset_by_run_indices(
        image_paths,
        validation_fraction=0.2,
        seed=seed,
        validation_run_prefixes=validation_run_prefixes,
    )
    train_paths = [image_paths[index] for index in train_indices]
    validation_paths = [image_paths[index] for index in validation_indices]
    train_angles = angles[train_indices]
    validation_angles = angles[validation_indices]
    for name, values in (("training", train_angles), ("validation", validation_angles)):
        if min(steering_region_counts(values).values()) < 5:
            raise RuntimeError("%s split lacks left/center/right coverage" % name)

    train_images = load_images(train_paths)
    validation_images = load_images(validation_paths)
    original_train_count = len(train_images)
    train_images, train_angles_augmented = augment_with_horizontal_flip(
        train_images, train_angles
    )

    model = keras.models.load_model(base_model_path, compile=False)
    if model.output_shape != (None, 1):
        raise RuntimeError("base model must output one steering angle")
    frozen_layers = []
    for layer in model.layers:
        if not isinstance(layer, keras.layers.Dense):
            layer.trainable = False
            frozen_layers.append(layer.name)
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss="mse",
        metrics=["mae"],
    )

    best_path = output_directory / "lane_navigation_best.keras"
    callbacks = [
        keras.callbacks.ModelCheckpoint(
            best_path, monitor="val_loss", save_best_only=True, verbose=1
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=3,
            min_lr=1e-6,
            verbose=1,
        ),
        keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=7, restore_best_weights=True, verbose=1
        ),
    ]
    history = model.fit(
        train_images,
        train_angles_augmented,
        validation_data=(validation_images, validation_angles),
        epochs=epochs,
        batch_size=batch_size,
        shuffle=True,
        callbacks=callbacks,
        verbose=2,
    )

    best_model = keras.models.load_model(best_path, compile=False)
    candidate_keras = output_directory / "lane_navigation_candidate.keras"
    candidate_h5 = output_directory / "lane_navigation_candidate.h5"
    best_model.save(candidate_keras)
    best_model.save(candidate_h5, include_optimizer=False)
    predictions = best_model.predict(validation_images, batch_size=64, verbose=0).reshape(-1)
    errors = predictions - validation_angles
    reloaded = keras.models.load_model(candidate_h5, compile=False)
    reloaded_predictions = reloaded.predict(
        validation_images, batch_size=64, verbose=0
    ).reshape(-1)

    summary = {
        "method": "fine-tune dense layers; freeze convolutional feature extractor",
        "base_model": str(Path(base_model_path).resolve()),
        "base_model_sha256": sha256_file(base_model_path),
        "dataset_id": Path(data_directory).name,
        "dataset_sha256": dataset_sha256(image_paths),
        "dataset_images": len(image_paths),
        "train_images_before_augmentation": original_train_count,
        "train_images_after_augmentation": len(train_images),
        "validation_images": len(validation_images),
        "train_source_runs": sorted({source_run_key(path) for path in train_paths}),
        "validation_source_runs": sorted(
            {source_run_key(path) for path in validation_paths}
        ),
        "validation_run_prefixes_requested": list(validation_run_prefixes),
        "train_steering_regions": steering_region_counts(train_angles),
        "validation_steering_regions": steering_region_counts(validation_angles),
        "frozen_layers": frozen_layers,
        "learning_rate": learning_rate,
        "seed": seed,
        "epochs_requested": epochs,
        "epochs_completed": len(history.history["loss"]),
        "validation_mae": float(np.mean(np.abs(errors))),
        "validation_rmse": float(math.sqrt(np.mean(errors ** 2))),
        "validation_bias": float(np.mean(errors)),
        "validation_max_absolute_error": float(np.max(np.abs(errors))),
        "prediction_min": float(predictions.min()),
        "prediction_max": float(predictions.max()),
        "export_max_abs_difference": float(
            np.max(np.abs(reloaded_predictions - predictions))
        ),
        "candidate_h5": candidate_h5.name,
        "candidate_h5_sha256": sha256_file(candidate_h5),
        "promotion_status": "candidate_requires_independent_track_evaluation",
    }
    with (output_directory / "history.json").open("w", encoding="utf-8") as handle:
        json.dump(history.history, handle, indent=2, sort_keys=True)
        handle.write("\n")
    with (output_directory / "training_summary.json").open(
        "w", encoding="utf-8"
    ) as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--base-model", type=Path, required=True)
    parser.add_argument("--validation-run-prefix", action="append", required=True)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--learning-rate", type=float, default=1e-4)
    parser.add_argument("--seed", type=int, default=20260810)
    args = parser.parse_args(argv)
    summary = fine_tune_model(
        args.data_dir,
        args.output_dir,
        args.base_model,
        args.validation_run_prefix,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        seed=args.seed,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
