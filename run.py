#!/usr/bin/env python3
"""
AI Orbit Ecosystem Data Ingestion Pipeline CLI Runner.
Main executable entrypoint for data extraction, entity resolution, relationship mapping, export, and web server.
"""

import sys
import os
import argparse
import logging
import json
import unittest
import http.server
import socketserver
import webbrowser

# Ensure src is in Python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from src.pipeline import DataIngestionPipeline
from src.validators.validator import DataValidator


def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers = []
    root_logger.addHandler(handler)


def run_tests():
    """Discovers and runs test suite in tests/"""
    print("\n========================================================")
    print("      RUNNING AI ORBIT PIPELINE UNIT TEST SUITE         ")
    print("========================================================\n")
    test_loader = unittest.TestLoader()
    test_dir = os.path.join(CURRENT_DIR, "tests")
    test_suite = test_loader.discover(test_dir, pattern="test_*.py")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    if result.wasSuccessful():
        print("\n[SUCCESS] All unit and integration tests passed.\n")
        return 0
    else:
        print("\n[FAILURE] Test suite encountered failures or errors.\n")
        return 1


def serve_web_app(port: int = 8080):
    """Starts a local HTTP server to host the interactive AI Orbit Web App"""
    web_dir = os.path.join(CURRENT_DIR, "web")
    os.chdir(web_dir)
    handler = http.server.SimpleHTTPRequestHandler
    
    print("\n" + "=" * 65)
    print("       AI ORBIT ECOSYSTEM INTERACTIVE WEB DASHBOARD       ")
    print("=" * 65)
    print(f"Serving web application at: http://localhost:{port}")
    print(f"Local Directory:            {web_dir}")
    print("Press Ctrl+C to stop the server.")
    print("=" * 65 + "\n")

    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Web server stopped.")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="AI Orbit Bulk Data Ingestion Pipeline & Web Explorer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 run.py --mode full
  python3 run.py --mode test
  python3 run.py --serve
  python3 run.py --serve --port 3000
  python3 run.py --sample 5
        """
    )

    parser.add_argument(
        "--mode",
        choices=["full", "validate", "test", "summary"],
        default="full",
        help="Execution mode: 'full' (ingest & export), 'validate' (check existing data), 'test' (run test suite), 'summary' (print stats)"
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Start local web server to host the AI Orbit interactive frontend"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to serve web application on (default: 8080)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=os.path.join(CURRENT_DIR, "data", "processed"),
        help="Directory to save processed JSON artifacts"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.88,
        help="Fuzzy matching similarity threshold for entity resolution (default: 0.88)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable detailed debug logging"
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=0,
        help="Display N sample records after pipeline completion"
    )

    args = parser.parse_args()
    setup_logging(args.verbose)

    if args.serve:
        return serve_web_app(args.port)

    if args.mode == "test":
        return run_tests()

    print("\n" + "=" * 65)
    print("       AI ORBIT ECOSYSTEM DATA INGESTION PIPELINE        ")
    print("=" * 65)
    print(f"Mode:             {args.mode.upper()}")
    print(f"Output Directory: {args.output_dir}")
    print(f"Fuzzy Threshold:  {args.threshold}")
    print("=" * 65 + "\n")

    pipeline = DataIngestionPipeline(
        output_dir=args.output_dir,
        fuzzy_threshold=args.threshold
    )

    if args.mode in ("full", "validate", "summary"):
        stats = pipeline.run()

        print("\n" + "=" * 65)
        print("                 PIPELINE EXECUTION SUMMARY               ")
        print("=" * 65)
        print(f"Status:                    {stats.validation_status}")
        print(f"Data Quality Score:        {stats.quality_score} / 100.0")
        print(f"Total Canonical Entities:  {stats.total_unique_entities} records (Target: 250-300)")
        print(f"Deduplicated / Merged:     {stats.deduplicated_count} duplicates resolved")
        print(f"Total Graph Relationships: {stats.total_relationships} edges")
        print(f"Relationship Density:      {stats.relationship_density} edges/node")
        print(f"Validation Errors:         {stats.validation_errors_count}")
        print(f"Validation Warnings:       {stats.validation_warnings_count}")
        print("-" * 65)
        print("Entities by Category Breakdown:")
        for cat, count in stats.entities_by_category.items():
            if count > 0:
                print(f"  - {cat:<20}: {count:>3} records")
        print("-" * 65)
        print("Top Relationship Predicates:")
        for rel_type, count in stats.relationships_by_type.items():
            if count > 0:
                print(f"  - {rel_type:<20}: {count:>3} edges")
        print("=" * 65 + "\n")

        if args.sample > 0:
            print(f"\n--- Displaying {args.sample} Sample Processed Entities ---")
            entities_file = os.path.join(args.output_dir, "entities.json")
            if os.path.exists(entities_file):
                with open(entities_file, "r", encoding="utf-8") as f:
                    samples = json.load(f)[:args.sample]
                    print(json.dumps(samples, indent=2))

        print(f"[SUCCESS] Artifacts exported successfully to: {args.output_dir}\n")
        print("Tip: Run 'python3 run.py --serve' to launch the interactive web dashboard!\n")
        return 0


if __name__ == "__main__":
    sys.exit(main())
