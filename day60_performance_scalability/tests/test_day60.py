import asyncio, unittest
from pathlib import Path
from day60_performance_scalability.src.batching import chunked
from day60_performance_scalability.src.cache import TTLCache
from day60_performance_scalability.src.pipeline import process_resumes
from day60_performance_scalability.src.benchmark import run_benchmark

class Day60Tests(unittest.TestCase):
    def test_batching(self): self.assertEqual(list(chunked([1,2,3,4,5],2)), [[1,2],[3,4],[5]])
    def test_invalid_batch(self):
        with self.assertRaises(ValueError): list(chunked([1],0))
    def test_cache_lru(self):
        c=TTLCache(2,30); c.set("a",1); c.set("b",2); c.get("a"); c.set("c",3)
        self.assertEqual(c.size,2); self.assertIsNone(c.get("b")); self.assertEqual(c.get("a"),1)
    def test_pipeline_and_cache(self):
        r=asyncio.run(process_resumes(["Python SQL","Excel","Python SQL"],2,2,0))
        self.assertEqual(r["processed"],3); self.assertGreaterEqual(r["cache_hits"],1)
    def test_benchmark_report(self):
        root=Path(__file__).resolve().parents[1]; r=run_benchmark(root)
        self.assertEqual(len(r["cases"]),4)
        self.assertTrue((root/"output/benchmark_report.md").exists())
        self.assertTrue(all(c["success_count"]==c["items"] for c in r["cases"]))
if __name__=="__main__": unittest.main()
