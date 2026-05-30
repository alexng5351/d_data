import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent if SCRIPT_DIR.name == 'scripts' else SCRIPT_DIR
WORKSPACE = BASE_DIR
PUBLIC_DIR = BASE_DIR / 'public'
COVERS_DATA_DIR = PUBLIC_DIR / 'data' / 'covers'
TEMP_DIR = BASE_DIR / 'temp' / 'covers'
CONFIG_PATH = Path(os.getenv('PINTEREST_SCENE_CONFIG', BASE_DIR / 'pinterest_scene_config.json'))
COLLECT_SCRIPT = Path(os.getenv('PINTEREST_COLLECT_SCRIPT', SCRIPT_DIR / 'pinterest_collect_verify.py'))
ROOT_OUTPUT_DIR = Path(os.getenv('AICOVER_SCENE_OUTPUT_DIR', TEMP_DIR / 'scene_candidates'))
COVER_JSON = Path(os.getenv('AICOVER_COVERS_JSON', COVERS_DATA_DIR / 'covers_candidates.json'))
SUMMARY_JSON = Path(os.getenv('AICOVER_SUMMARY_JSON', TEMP_DIR / 'pinterest_verify_summary.json'))
COVERAGE_REPORT = Path(os.getenv('AICOVER_COVERAGE_REPORT', TEMP_DIR / 'coverage_report.json'))


def load_scene_config(config_path: Path = CONFIG_PATH):
    with open(config_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError('pinterest_scene_config.json must be a list of scene config objects')
    required = {'scene', 'scene_cn', 'queries', 'target_accept_count'}
    for item in data:
        missing = required - set(item.keys())
        if missing:
            raise ValueError(f"Scene config missing fields {sorted(missing)}: {item}")
    return data


def find_scene(configs, scene_key: str):
    for scene in configs:
        if scene['scene'] == scene_key or scene['scene_cn'] == scene_key:
            return [scene]
    available = ', '.join(item['scene'] for item in configs)
    raise ValueError(f"Unknown scene '{scene_key}'. Available scenes: {available}")


def read_json_if_exists(path: Path, default):
    if not path.exists():
        return default
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def run_collect_for_scene(scene_cfg):
    scene = scene_cfg['scene']
    scene_dir = ROOT_OUTPUT_DIR / scene
    image_dir = scene_dir / 'images'
    scene_dir.mkdir(parents=True, exist_ok=True)
    image_dir.mkdir(parents=True, exist_ok=True)

    query = ' | '.join(scene_cfg.get('queries', []))
    target_accept_count = int(scene_cfg.get('target_accept_count', 4))
    cmd = [
        'python3',
        str(COLLECT_SCRIPT),
        '--scene',
        scene,
        '--query',
        query,
        '--scene-cn',
        scene_cfg['scene_cn'],
        '--target-accept-count',
        str(target_accept_count),
        '--max-inputs',
        str(max(target_accept_count * 4, 40)),
    ]
    proc = subprocess.run(cmd, cwd=str(WORKSPACE), capture_output=True, text=True)

    accepted = read_json_if_exists(COVER_JSON, [])
    summary = read_json_if_exists(SUMMARY_JSON, {})

    copied_candidates = []
    for idx, candidate in enumerate(accepted, start=1):
        candidate_copy = json.loads(json.dumps(candidate, ensure_ascii=False))
        src = Path(candidate_copy.get('image', {}).get('url', ''))
        if src.exists():
            dst = image_dir / src.name
            shutil.copyfile(src, dst)
            candidate_copy['image']['url'] = str(dst)
        elif src:
            candidate_copy.setdefault('risk_notes', []).append(f'image_source_missing:{src}')
        candidate_copy.setdefault('scene', scene)
        candidate_copy.setdefault('scene_cn', scene_cfg['scene_cn'])
        copied_candidates.append(candidate_copy)

    candidates_path = scene_dir / 'candidates.json'
    with open(candidates_path, 'w', encoding='utf-8') as f:
        json.dump(copied_candidates, f, ensure_ascii=False, indent=2)

    summary_path = scene_dir / 'summary.json'
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    accepted_count = len(copied_candidates)
    total_count = len(summary.get('checked', [])) if isinstance(summary, dict) else accepted_count
    target = int(scene_cfg.get('target_accept_count', 4))
    return {
        'scene': scene,
        'scene_cn': scene_cfg['scene_cn'],
        'queries': scene_cfg.get('queries', []),
        'target_accept_count': target,
        'accepted': accepted_count,
        'total': total_count,
        'passed': accepted_count >= target,
        'candidates_json': str(candidates_path),
        'images_dir': str(image_dir),
        'summary_json': str(summary_path),
        'subprocess_returncode': proc.returncode,
        'subprocess_stdout_preview': (proc.stdout or '')[-2000:],
        'subprocess_stderr_preview': (proc.stderr or '')[-2000:],
    }


def parse_args():
    parser = argparse.ArgumentParser(description='Batch collect Pinterest candidates by scene config.')
    parser.add_argument('--scene', default='', help='Run one scene only. Accepts scene or scene_cn from pinterest_scene_config.json.')
    parser.add_argument('--config', default=str(CONFIG_PATH), help='Path to pinterest_scene_config.json')
    return parser.parse_args()


def main():
    args = parse_args()
    configs = load_scene_config(Path(args.config))
    selected = find_scene(configs, args.scene) if args.scene else configs
    ROOT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    COVERAGE_REPORT.parent.mkdir(parents=True, exist_ok=True)

    results = []
    for scene_cfg in selected:
        print(f"[batch] Running scene: {scene_cfg['scene']} / {scene_cfg['scene_cn']}")
        result = run_collect_for_scene(scene_cfg)
        results.append(result)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    report = {
        'config': str(Path(args.config).resolve()),
        'scene_count': len(results),
        'all_passed': all(item['passed'] for item in results),
        'scenes': results,
    }
    with open(COVERAGE_REPORT, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()