"""Role and company knowledge for the resume checker.

The weights are intentionally transparent so the first MVP can explain why it
gave a score instead of behaving like a black box.
"""

ROLE_PROFILES = {
    "gpu_software": {
        "label": "GPU Software Engineer",
        "must_have": {
            "c++": 5,
            "cuda": 7,
            "parallel programming": 4,
            "profiling": 4,
            "performance": 4,
            "python": 2,
            "linux": 3,
        },
        "strong_signals": {
            "triton": 5,
            "tensor cores": 4,
            "shared memory": 4,
            "nsight": 4,
            "rocm": 4,
            "hip": 4,
            "opencl": 3,
            "simd": 3,
            "memory coalescing": 4,
            "kernel optimization": 5,
        },
        "project_ideas": [
            "CUDA matrix multiplication optimizer with naive, tiled, and shared-memory kernels plus benchmarks.",
            "Triton softmax or layer-norm kernel benchmarked against PyTorch.",
            "CUDA-to-HIP port of a small kernel library with AMD ROCm notes.",
        ],
    },
    "systems_software": {
        "label": "Systems Software Engineer",
        "must_have": {
            "c++": 5,
            "c": 4,
            "linux": 6,
            "operating systems": 5,
            "multithreading": 4,
            "memory management": 4,
            "debugging": 3,
        },
        "strong_signals": {
            "kernel": 5,
            "device driver": 5,
            "gdb": 3,
            "perf": 4,
            "ipc": 3,
            "concurrency": 4,
            "lock-free": 4,
            "networking": 3,
            "distributed systems": 4,
        },
        "project_ideas": [
            "Linux process and memory profiler using /proc, perf, or eBPF-style tracing.",
            "High-performance C++ thread pool with latency and throughput benchmarks.",
            "Minimal userspace driver simulation for a PCIe-like device queue.",
        ],
    },
    "compiler": {
        "label": "Compiler Engineer",
        "must_have": {
            "c++": 6,
            "compiler": 6,
            "llvm": 7,
            "data structures": 3,
            "algorithms": 3,
            "linux": 2,
        },
        "strong_signals": {
            "mlir": 6,
            "ir": 4,
            "optimization pass": 5,
            "code generation": 5,
            "static analysis": 4,
            "parser": 3,
            "jit": 4,
            "graph compiler": 5,
        },
        "project_ideas": [
            "LLVM optimization pass that removes redundant operations and reports before/after IR.",
            "Toy compiler with lexer, parser, IR, optimization, and code generation notes.",
            "MLIR or graph-compiler experiment for a tiny tensor expression language.",
        ],
    },
    "ai_performance": {
        "label": "AI/ML Performance Engineer",
        "must_have": {
            "python": 4,
            "pytorch": 6,
            "cuda": 6,
            "performance": 5,
            "profiling": 4,
            "c++": 3,
            "machine learning": 3,
        },
        "strong_signals": {
            "triton": 6,
            "tensorrt": 5,
            "onnx": 3,
            "quantization": 4,
            "inference": 5,
            "vllm": 4,
            "llm": 3,
            "batching": 3,
            "latency": 4,
            "throughput": 4,
        },
        "project_ideas": [
            "Inference benchmark comparing PyTorch eager, torch.compile, ONNX Runtime, and TensorRT if available.",
            "Custom Triton kernel for layer norm, softmax, or matmul with latency charts.",
            "C++ or Python batching server for model inference with p50/p95 latency metrics.",
        ],
    },
    "firmware": {
        "label": "Embedded/Firmware Software Engineer",
        "must_have": {
            "c": 6,
            "c++": 4,
            "embedded": 6,
            "linux": 3,
            "rtos": 4,
            "debugging": 3,
            "microcontroller": 3,
        },
        "strong_signals": {
            "device driver": 5,
            "uart": 3,
            "spi": 3,
            "i2c": 3,
            "can": 3,
            "arm": 4,
            "risc-v": 4,
            "bootloader": 5,
            "interrupt": 4,
        },
        "project_ideas": [
            "RTOS-based sensor pipeline with interrupt-driven IO and timing measurements.",
            "Bootloader or firmware update simulator with CRC validation.",
            "Linux character device driver with userspace test program.",
        ],
    },
    "graphics": {
        "label": "Graphics Software Engineer",
        "must_have": {
            "c++": 5,
            "graphics": 6,
            "opengl": 4,
            "vulkan": 5,
            "linear algebra": 3,
            "performance": 3,
        },
        "strong_signals": {
            "directx": 4,
            "shader": 5,
            "rendering": 4,
            "gpu": 4,
            "ray tracing": 4,
            "hlsl": 4,
            "glsl": 4,
            "profiling": 3,
        },
        "project_ideas": [
            "Vulkan renderer with profiling notes, frame-time charts, and shader pipeline explanation.",
            "GPU particle simulation using compute shaders.",
            "Mini graphics debugger or shader hot-reload tool.",
        ],
    },
    "ai_infra": {
        "label": "AI Infrastructure Engineer",
        "must_have": {
            "python": 4,
            "c++": 3,
            "distributed systems": 5,
            "kubernetes": 4,
            "linux": 4,
            "performance": 4,
            "cloud": 3,
        },
        "strong_signals": {
            "cuda": 4,
            "gpu": 4,
            "inference": 4,
            "pytorch": 3,
            "networking": 4,
            "observability": 3,
            "grpc": 3,
            "ray": 3,
            "slurm": 4,
        },
        "project_ideas": [
            "GPU-aware inference service with batching, queues, and p95 latency tracking.",
            "Distributed training or inference monitor with node/GPU utilization dashboard.",
            "C++/Python microservice benchmark focused on throughput, latency, and backpressure.",
        ],
    },
}

COMPANY_PROFILES = {
    "nvidia": {
        "label": "NVIDIA",
        "keywords": {
            "cuda": 7,
            "gpu": 5,
            "c++": 5,
            "linux": 4,
            "tensorrt": 5,
            "triton": 5,
            "nsight": 4,
            "parallel programming": 4,
            "deep learning": 3,
            "systems software": 4,
            "compiler": 4,
        },
        "stats": {
            "interview_rounds": "5 to 7 rounds",
            "acceptance_rate": "~0.3% (Highly Selective)",
            "focus_areas": ["Systems Engineering", "Memory Management", "Concurrency", "Hardware-Software Co-design"],
            "culture_values": ["Speed and Execution", "Innovation", "Flat Hierarchy", "One Team"],
        }
    },
    "amd": {
        "label": "AMD",
        "keywords": {
            "rocm": 7,
            "hip": 6,
            "gpu": 5,
            "c++": 5,
            "linux": 4,
            "llvm": 5,
            "compiler": 4,
            "opencl": 3,
            "performance": 4,
            "pytorch": 3,
        },
        "stats": {
            "interview_rounds": "3 to 5 rounds",
            "acceptance_rate": "~2-5% (Selective)",
            "focus_areas": ["C/C++ Fundamentals", "Linux Kernel", "Driver Development", "Practical Problem Solving"],
            "culture_values": ["Execution Focus", "Technical Depth", "Cross-team Collaboration"],
        }
    },
    "qualcomm": {
        "label": "Qualcomm",
        "keywords": {
            "c++": 5,
            "c": 4,
            "embedded": 5,
            "android": 4,
            "linux": 4,
            "drivers": 5,
            "dsp": 4,
            "computer vision": 3,
            "performance": 3,
            "multimedia": 3,
        },
        "stats": {
            "interview_rounds": "4 to 6 rounds",
            "acceptance_rate": "~4-6%",
            "focus_areas": ["Embedded C/C++", "RTOS", "Networking/DSP", "Android Frameworks"],
            "culture_values": ["Engineering Excellence", "Research Driven", "Work-Life Balance"],
        }
    },
    "intel": {
        "label": "Intel",
        "keywords": {
            "c++": 5,
            "linux": 4,
            "compiler": 5,
            "oneapi": 5,
            "opencl": 3,
            "drivers": 4,
            "performance": 4,
            "firmware": 4,
            "systems software": 4,
        },
        "stats": {
            "interview_rounds": "4 to 5 rounds",
            "acceptance_rate": "~5-8%",
            "focus_areas": ["Computer Architecture", "Compilers", "Silicon Validation", "Low-level Optimization"],
            "culture_values": ["Process Driven", "Deep Expertise", "Massive Scale"],
        }
    },
    "arm": {
        "label": "Arm",
        "keywords": {
            "c++": 5,
            "c": 4,
            "arm": 7,
            "compiler": 4,
            "embedded": 4,
            "architecture": 5,
            "linux": 3,
            "performance": 3,
        },
        "stats": {
            "interview_rounds": "4 to 5 rounds",
            "acceptance_rate": "~3-5%",
            "focus_areas": ["ISA", "Assembly/C", "OS Internals", "Microarchitecture"],
            "culture_values": ["Innovation", "IP Design Focus", "Global Collaboration"],
        }
    },
    "broadcom": {
        "label": "Broadcom",
        "keywords": {
            "c": 5,
            "c++": 4,
            "networking": 6,
            "linux": 4,
            "drivers": 5,
            "firmware": 5,
            "embedded": 4,
            "pcie": 4,
        },
        "stats": {
            "interview_rounds": "4 to 6 rounds",
            "acceptance_rate": "~4-7%",
            "focus_areas": ["Networking Protocols", "Linux Kernel", "High-speed IO", "Embedded Systems"],
            "culture_values": ["Execution Driven", "Acquisition Synergies", "High Profitability"],
        }
    },
    "apple": {
        "label": "Apple",
        "keywords": {
            "c++": 5,
            "c": 4,
            "objective-c": 3,
            "swift": 3,
            "metal": 4,
            "linux": 3,
            "kernel": 4,
            "embedded": 4,
            "performance": 4,
        },
        "stats": {
            "interview_rounds": "5 to 6 rounds",
            "acceptance_rate": "~2-4% (Highly Selective)",
            "focus_areas": ["Systems Design", "Performance Optimization", "Device Drivers", "Domain Depth"],
            "culture_values": ["Secrecy", "Attention to Detail", "Product Excellence"],
        }
    },
    "tesla": {
        "label": "Tesla",
        "keywords": {
            "c++": 6,
            "c": 4,
            "python": 3,
            "linux": 4,
            "cuda": 4,
            "embedded": 4,
            "robotics": 4,
            "real-time": 5,
            "rtos": 4,
        },
        "stats": {
            "interview_rounds": "4 to 7 rounds",
            "acceptance_rate": "~1-3% (Highly Selective)",
            "focus_areas": ["C++ Performance", "Real-Time Systems", "First-Principles Thinking", "Hard Engineering"],
            "culture_values": ["Hardcore Engineering", "Speed", "First Principles"],
        }
    },
    "meta_rl": {
        "label": "Meta Reality Labs",
        "keywords": {
            "c++": 6,
            "graphics": 5,
            "computer vision": 5,
            "opengl": 4,
            "vulkan": 4,
            "simd": 4,
            "android": 3,
            "performance": 5,
        },
        "stats": {
            "interview_rounds": "5 to 6 rounds",
            "acceptance_rate": "~3-5%",
            "focus_areas": ["C++ Systems", "Computer Vision/Graphics", "Math/Linear Algebra", "Performance"],
            "culture_values": ["Move Fast", "Focus on Impact", "Openness"],
        }
    },
    "cruise": {
        "label": "Cruise",
        "keywords": {
            "c++": 6,
            "python": 4,
            "linux": 4,
            "ros": 4,
            "robotics": 5,
            "cuda": 3,
            "embedded": 4,
            "performance": 4,
        },
        "stats": {
            "interview_rounds": "4 to 6 rounds",
            "acceptance_rate": "~3-6%",
            "focus_areas": ["Modern C++", "Robotics/AV", "System Architecture", "Performance"],
            "culture_values": ["Safety First", "Ownership", "Collaboration"],
        }
    },
    "synopsys": {
        "label": "Synopsys",
        "keywords": {
            "c++": 5,
            "compiler": 5,
            "eda": 6,
            "algorithms": 4,
            "data structures": 4,
            "static analysis": 4,
            "linux": 3,
        },
        "stats": {
            "interview_rounds": "3 to 4 rounds",
            "acceptance_rate": "~6-9%",
            "focus_areas": ["Complex Algorithms", "Data Structures", "C++ Templates", "Graph Theory"],
            "culture_values": ["Academic Approach", "Stability", "Continuous Learning"],
        }
    },
    "cadence": {
        "label": "Cadence",
        "keywords": {
            "c++": 5,
            "eda": 6,
            "algorithms": 4,
            "data structures": 4,
            "simulation": 4,
            "linux": 3,
            "compiler": 3,
        },
        "stats": {
            "interview_rounds": "3 to 4 rounds",
            "acceptance_rate": "~6-9%",
            "focus_areas": ["Simulation Engines", "C++ Performance", "Mathematical Modeling", "Algorithms"],
            "culture_values": ["Innovation", "Domain Expertise", "Team Collaboration"],
        }
    },
    "general": {
        "label": "Hardware Companies",
        "keywords": {
            "c++": 5,
            "linux": 4,
            "performance": 4,
            "systems software": 4,
            "gpu": 4,
            "compiler": 3,
            "embedded": 3,
            "python": 3,
        },
        "stats": {
            "interview_rounds": "Varies (3-6 rounds)",
            "acceptance_rate": "Varies by company",
            "focus_areas": ["C/C++", "OS Fundamentals", "Problem Solving", "Systems Architecture"],
            "culture_values": ["Technical Rigor", "Hardware-Software Co-design"],
        }
    },
}

CORE_FOUNDATION = {
    "data structures": 4,
    "algorithms": 4,
    "leetcode": 2,
    "problem solving": 2,
    "oop": 2,
    "dbms": 1,
    "computer networks": 2,
    "operating systems": 4,
}

IMPACT_TERMS = [
    "improved",
    "reduced",
    "increased",
    "optimized",
    "accelerated",
    "benchmarked",
    "profiled",
    "decreased",
    "saved",
    "scaled",
    "latency",
    "throughput",
    "speedup",
    "%",
    "x faster",
    "ms",
    "gb/s",
    "qps",
]

ATS_SECTIONS = [
    "education",
    "skills",
    "projects",
    "experience",
    "work experience",
    "internship",
    "achievements",
]
