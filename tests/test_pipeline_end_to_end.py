"""Integration test for End-to-End Pipeline Execution."""

import unittest
import os
import json
from src.pipeline import DataIngestionPipeline


class TestPipelineEndToEnd(unittest.TestCase):
    def test_full_pipeline_run(self):
        output_dir = "/tmp/ai_orbit_test_output"
        pipeline = DataIngestionPipeline(output_dir=output_dir)
        stats = pipeline.run()

        # Assert target record scope (250-300 records)
        self.assertGreaterEqual(stats.total_unique_entities, 250)
        self.assertLessEqual(stats.total_unique_entities, 300)

        # Assert relationship count and validation
        self.assertGreaterEqual(stats.total_relationships, 250)
        self.assertEqual(stats.validation_status, "PASS")
        self.assertEqual(stats.validation_errors_count, 0)
        self.assertEqual(stats.quality_score, 100.0)

        # Verify exported files exist and are non-empty
        entities_path = os.path.join(output_dir, "entities.json")
        relationships_path = os.path.join(output_dir, "relationships.json")
        recently_added_path = os.path.join(output_dir, "recently_added.json")

        self.assertTrue(os.path.exists(entities_path))
        self.assertTrue(os.path.exists(relationships_path))
        self.assertTrue(os.path.exists(recently_added_path))

        with open(entities_path) as f:
            data = json.load(f)
            self.assertEqual(len(data), stats.total_unique_entities)

        with open(relationships_path) as f:
            rels = json.load(f)
            self.assertEqual(len(rels), stats.total_relationships)


if __name__ == "__main__":
    unittest.main()
