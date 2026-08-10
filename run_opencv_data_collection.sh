#!/usr/bin/env bash
set -eu

cd "$(dirname "$0")"

track_id="${1:-}"
mode="${2:-drive}"
if [ -z "$track_id" ]; then
  echo "usage: $0 <track_id> [drive|manual]"
  echo "example: $0 layout_a_run1 drive"
  exit 2
fi
case "$track_id" in
  *[!A-Za-z0-9_-]*)
    echo "track_id may contain only letters, numbers, underscores, and hyphens"
    exit 2
    ;;
esac

timestamp="$(date +%Y%m%d_%H%M%S)"
recording="data/recordings/${track_id}_${timestamp}.avi"

drive_args=""
case "$mode" in
  drive)
    echo "Clear the track, keep the power switch within reach, and watch the VNC preview."
    printf "Type COLLECT to drive at 10%% PWM for at most 15 seconds: "
    read -r confirmation
    if [ "$confirmation" != "COLLECT" ]; then
      echo "cancelled; motors were not started"
      exit 1
    fi
    drive_args="--drive"
    ;;
  manual)
    echo "Motor output is disabled. Move the car by hand through varied lane positions."
    ;;
  *)
    echo "mode must be drive or manual"
    exit 2
    ;;
esac

# shellcheck disable=SC2086
python3 jd_3_lane_follower_opencv.py \
  $drive_args \
  --speed 10 \
  --max-seconds 15 \
  --warmup-frames 30 \
  --require-two-lanes \
  --lost-lane-limit 1 \
  --watchdog-timeout 1.0 \
  --record-video "$recording"

echo "saved raw recording: $recording"
echo "Keep this AVI. Labels will be generated on the GPU PC with the strict quality gate."
