import json
import os

knowledge_dir = r"d:\flow zint ai hackthons\omniflow-backend\knowledge"
os.makedirs(knowledge_dir, exist_ok=True)

# 1. Update/merge brands.json
brands_path = os.path.join(knowledge_dir, "brands.json")
existing_brands = []
if os.path.exists(brands_path):
    try:
        with open(brands_path, "r", encoding="utf-8") as f:
            existing_brands = json.load(f)
    except Exception:
        pass

brand_updates = [
    {
        "name": "Apple",
        "category": "Premium Ecosystem",
        "positioning": "Premium ecosystem, AI-integrated chips",
        "popular_series": ["MacBook Pro Series", "MacBook Air Series", "iPhone 17 Series"]
    },
    {
        "name": "Samsung",
        "category": "Mobile & Electronics",
        "positioning": "Display tech, foldables, Galaxy AI integration",
        "popular_series": ["Galaxy S26 Series", "Galaxy Z Fold Series"]
    },
    {
        "name": "Lenovo",
        "category": "Computers",
        "positioning": "Business laptops, ThinkPad, enterprise AI scaling",
        "popular_series": ["ThinkPad Series", "Yoga Series", "Legion Series"]
    },
    {
        "name": "ASUS",
        "category": "Computers",
        "positioning": "Gaming, ROG, creator laptops and graphics integration",
        "popular_series": ["ROG Series", "Zenbook Series", "Zephyrus Series"]
    }
]

# Merge logic for brands: key by "name"
brands_map = {b["name"].lower(): b for b in existing_brands if "name" in b}
for b in brand_updates:
    brands_map[b["name"].lower()] = b

with open(brands_path, "w", encoding="utf-8") as f:
    json.dump(list(brands_map.values()), f, indent=2)


# 2. Update/merge mobiles.json
mobiles_path = os.path.join(knowledge_dir, "mobiles.json")
existing_mobiles = []
if os.path.exists(mobiles_path):
    try:
        with open(mobiles_path, "r", encoding="utf-8") as f:
            existing_mobiles = json.load(f)
    except Exception:
        pass

mobile_updates = [
    {
        "brand": "Apple",
        "model": "iPhone 17 Pro",
        "category": "Premium Smartphone",
        "price": "$1,299",
        "specs": "Apple A19 Pro chip, 8GB RAM, Apple Intelligence, 2026 release",
        "cpu": "A19 Pro",
        "gpu": "Apple 6-core GPU",
        "year": "2026"
    },
    {
        "brand": "Samsung",
        "model": "Galaxy S26 Ultra",
        "category": "Premium Smartphone",
        "price": "$1,349",
        "specs": "Snapdragon 8 Gen 5, 12GB RAM, Galaxy AI 2026 features, 200MP camera",
        "cpu": "Snapdragon 8 Gen 5",
        "gpu": "Adreno 830",
        "year": "2026"
    }
]

# Merge logic: key by "model"
mobiles_map = {m["model"].lower(): m for m in existing_mobiles if "model" in m}
for m in mobile_updates:
    mobiles_map[m["model"].lower()] = m

with open(mobiles_path, "w", encoding="utf-8") as f:
    json.dump(list(mobiles_map.values()), f, indent=2)


# 3. Update/merge laptops.json
laptops_path = os.path.join(knowledge_dir, "laptops.json")
existing_laptops = []
if os.path.exists(laptops_path):
    try:
        with open(laptops_path, "r", encoding="utf-8") as f:
            existing_laptops = json.load(f)
    except Exception:
        pass

laptop_updates = [
    {
        "brand": "Apple",
        "model": "MacBook Pro 16 M4 Max",
        "category": "Premium Laptop",
        "price": "$3,490",
        "specs": "Apple M4 Max chip, 64GB Unified Memory, 1TB SSD, 2026 model",
        "cpu": "M4 Max",
        "gpu": "Apple 40-core GPU",
        "year": "2026"
    },
    {
        "brand": "Lenovo",
        "model": "ThinkPad X1 Carbon Gen 13",
        "category": "Enterprise Business Laptop",
        "price": "$1,850",
        "specs": "Intel Core Ultra 9 285H, 32GB LPDDR5X, 1TB PCIe Gen 4 SSD, 2026 release",
        "cpu": "Intel Core Ultra 9 285H",
        "gpu": "Intel Arc Graphics",
        "year": "2026"
    },
    {
        "brand": "ASUS",
        "model": "ROG Zephyrus G16 (2026)",
        "category": "Gaming and Creator Laptop",
        "price": "$2,100",
        "specs": "AMD Ryzen AI 9 HX 370, NVIDIA GeForce RTX 5080, 32GB RAM, 2026 model",
        "cpu": "AMD Ryzen AI 9 HX 370",
        "gpu": "NVIDIA GeForce RTX 5080",
        "year": "2026"
    }
]

# Merge logic: key by "model"
laptops_map = {l["model"].lower(): l for l in existing_laptops if "model" in l}
for l in laptop_updates:
    laptops_map[l["model"].lower()] = l

with open(laptops_path, "w", encoding="utf-8") as f:
    json.dump(list(laptops_map.values()), f, indent=2)


# 4. Update/merge processors.json
processors_path = os.path.join(knowledge_dir, "processors.json")
existing_processors = []
if os.path.exists(processors_path):
    try:
        with open(processors_path, "r", encoding="utf-8") as f:
            existing_processors = json.load(f)
    except Exception:
        pass

processor_updates = [
    {
        "type": "M4 Max",
        "brand": "Apple",
        "strengths": ["Neural Engine 40-core", "extreme unified memory bandwidth", "industry-leading AI inference"],
        "recommended_usage": ["Local AI development", "heavy video editing", "multimodal workload acceleration"]
    },
    {
        "type": "Intel Core Ultra 9",
        "brand": "Intel",
        "strengths": ["Dedicated Intel AI Boost NPU", "high clock speeds", "x86 architecture compatibility"],
        "recommended_usage": ["Copilot+ PC tasks", "office productivity", "general multitasking"]
    },
    {
        "type": "AMD Ryzen AI 9",
        "brand": "AMD",
        "strengths": ["XDNA 2 architecture NPU with 50+ TOPS", "excellent battery efficiency", "strong multi-threaded graphics"],
        "recommended_usage": ["Local LLM execution", "mobile productivity", "hybrid gaming workloads"]
    }
]

# Merge logic: key by "type"
processors_map = {p["type"].lower(): p for p in existing_processors if "type" in p}
for p in processor_updates:
    processors_map[p["type"].lower()] = p

with open(processors_path, "w", encoding="utf-8") as f:
    json.dump(list(processors_map.values()), f, indent=2)


# 5. Update/merge gpus.json
gpus_path = os.path.join(knowledge_dir, "gpus.json")
existing_gpus = []
if os.path.exists(gpus_path):
    try:
        with open(gpus_path, "r", encoding="utf-8") as f:
            existing_gpus = json.load(f)
    except Exception:
        pass

gpu_updates = [
    {
        "name": "NVIDIA GeForce RTX 5080",
        "family": "NVIDIA RTX 5000",
        "recommended_for": ["High-end Gaming", "Local AI Inference and Fine-tuning", "3D Rendering"]
    }
]

# Merge logic: key by "name"
gpus_map = {g["name"].lower(): g for g in existing_gpus if "name" in g}
for g in gpu_updates:
    gpus_map[g["name"].lower()] = g

with open(gpus_path, "w", encoding="utf-8") as f:
    json.dump(list(gpus_map.values()), f, indent=2)


# 6. Overwrite trends files to clean up and set explicit schemas
trends_data = {
    "ai_trends.json": [
        {
            "year": "2026",
            "trend": "On-device AI processing",
            "growth": "Critical",
            "summary": "2026 laptops require 40+ TOPS NPU for Windows Copilot+ PC certification.",
            "brands": ["Microsoft", "Intel", "AMD", "Qualcomm"]
        },
        {
            "year": "2026",
            "trend": "Agentic Workflows",
            "growth": "High",
            "summary": "Automated reasoning and planning directly on hardware for real-time task orchestration.",
            "brands": ["Apple", "Lenovo", "ASUS"]
        }
    ],
    "gpu_trends.json": [
        {
            "year": "2026",
            "trend": "NVIDIA RTX 5000 series domination",
            "growth": "High",
            "summary": "RTX 5080/5090 Blackwell architectures are the baseline for 2026 AI creator laptops.",
            "brands": ["NVIDIA", "ASUS", "MSI"]
        },
        {
            "year": "2026",
            "trend": "Integrated NPUs & Unified Memory",
            "growth": "High",
            "summary": "On-chip memory and dedicated AI acceleration blocks reduce discrete GPU reliance for standard AI workloads.",
            "brands": ["Apple", "Intel", "AMD"]
        }
    ],
    "market_trends.json": [
        {
            "year": "2026",
            "trend": "Enterprise AI Upgrade Cycle",
            "growth": "Critical",
            "summary": "Global enterprises are refreshing their fleets with 2026 Copilot+ standard hardware.",
            "brands": ["Lenovo", "Dell", "HP"]
        },
        {
            "year": "2026",
            "trend": "Premium smartphone stagnation",
            "growth": "Medium",
            "summary": "Saturating hardware speeds shift buyer interest toward ecosystem integration and on-device AI assistants.",
            "brands": ["Apple", "Samsung", "Google"]
        }
    ]
}

for filename, content in trends_data.items():
    with open(os.path.join(knowledge_dir, filename), "w", encoding="utf-8") as f:
        json.dump(content, f, indent=2)

print("Active 2026 knowledge database updated successfully.")
