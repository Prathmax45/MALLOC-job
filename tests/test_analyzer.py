import unittest

from app.resume_agent.analyzer import analyze_base_resume, generate_target_stats
from app.resume_agent.pdf_reader import clean_resume_text


class AnalyzerTests(unittest.TestCase):
    def test_gpu_resume_scores_and_reports(self):
        resume = """
        Education
        Skills: C++, Python, Linux, CUDA, PyTorch, Operating Systems, Data Structures, Algorithms
        Projects
        Built a GPU CUDA matrix multiplication optimizer using shared memory and profiling with Nsight.
        Improved runtime by 3x and reduced latency by 40% after benchmarking memory coalescing.
        Experience
        Implemented multithreaded C++ services and debugged performance issues with gdb.
        """

        result = analyze_base_resume(resume)
        stats = generate_target_stats(resume, "gpu_software", "nvidia")

        self.assertGreaterEqual(result.score, 70)
        self.assertTrue(result.best_fit_roles)
        self.assertTrue(result.company_fit)
        self.assertTrue(stats.highest_probability_path)
        self.assertIn("cuda", result.detected_signals)

    def test_empty_resume_reveals_low_readiness(self):
        resume = "Education\nB.Tech Computer Science\nSkills: HTML CSS JavaScript\n"

        result = analyze_base_resume(resume)
        stats = generate_target_stats(resume, "systems_software", "amd")

        self.assertLess(result.score, 55)
        self.assertTrue(stats.missing_skills)
        self.assertTrue(stats.priority_actions)

    def test_pdf_text_cleanup_preserves_resume_sections(self):
        raw = "Skills: P y t h o n C++ CUDA\n\nProjects: Built GPU optimizer"
        cleaned = clean_resume_text(raw)

        self.assertIn("Python", cleaned)
        self.assertIn("Skills", cleaned)
        self.assertIn("Projects", cleaned)


if __name__ == "__main__":
    unittest.main()
