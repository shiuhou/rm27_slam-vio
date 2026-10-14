"""VIO-only entry point; legacy SLAM launchers live on legacy/slam."""
import argparse
from pathlib import Path
from .common import require, read_json


def run(config, *, _fixture_token=None):
    require(config.get('backend') == 'OpenVINS', 'BACKEND_UNSUPPORTED',
            'main supports OpenVINS VIO only; legacy SLAM is archived on legacy/slam')
    from .openvins_runtime import run as run_vio
    return run_vio(config)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    args = parser.parse_args()
    result = run(read_json(args.config))
    print(result['status'] + ': ' + result.get('failure_reason', 'offline process completed; not a stage PASS'))
    return 0 if result['status'] == 'EXECUTION_COMPLETED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
