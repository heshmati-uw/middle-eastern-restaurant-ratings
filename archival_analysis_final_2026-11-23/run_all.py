"""Run the consolidated analysis.

  python run_all.py                       exhibits, figures and RESULTS.md from the frozen tables (no raw data needed)
  python run_all.py --from-raw <project root> [--rscript <path to Rscript>] [--workers N]
                                          also rebuilds the sample, county assignment, review extract and frozen tables from raw files
"""
import sys, subprocess, pathlib, argparse

HERE = pathlib.Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument("--from-raw")
ap.add_argument("--rscript", default="Rscript")
ap.add_argument("--workers", default="16")
a = ap.parse_args()


def run(*cmd):
    print(">>", " ".join(str(c) for c in cmd), flush=True)
    subprocess.run([str(c) for c in cmd], cwd=HERE, check=True)


if a.from_raw:
    run(sys.executable, "01_build_sample.py", a.from_raw)
    run(a.rscript, "02_geocode_counties.R", a.from_raw, ".")
    run(sys.executable, "03_extract_reviews.py", a.from_raw, a.workers)
    run(sys.executable, "04_build_frozen.py")
for s in ["05_label_choice.py", "06_levels.py", "07_events.py", "08_figures.py", "10_positioning_over_time.py", "11_story_figures.py", "13_star_breakdown.py",
          "09_results_summary.py"]:
    run(sys.executable, s)
if a.from_raw:
    # descriptives that need the raw files: review text, reviewer activity, business names, county boundaries
    run(sys.executable, "12_scan_text_and_reviewers.py", a.from_raw, a.workers)
    run(sys.executable, "14_labels_and_pairs.py", a.from_raw)
    run(a.rscript, "15_map.R", a.from_raw, ".")
    run(sys.executable, "16_text_and_reviewers.py")
    run(sys.executable, "17_identity_lens.py")
    run(sys.executable, "18_scan_reviewer_leniency.py", a.from_raw, a.workers)
    run(sys.executable, "19_star_breakdown_leniency.py")
    run(sys.executable, "21_each_group_over_time.py")
    run(sys.executable, "22_scan_authentic_reviews.py", a.from_raw, a.workers)
    run(sys.executable, "23_authentic_mentions.py")
    run(sys.executable, "20_results_summary_html.py")
