import PyInstaller.__main__
import os
import shutil

# Clean previous builds
if os.path.exists("build"):
    shutil.rmtree("build")
if os.path.exists("dist"):
    shutil.rmtree("dist")

print("Starting Build Process for 'The Secretary Swarm'...")

# Define data to include (internal use if needed, but we rely on external for templates)
# We still bundle them internally just in case code falls back, but primarily we want external.
datas = [
    ("templates;templates"),
    ("README.md;.")
]

args = [
    "launcher.py",             # Entry point
    "--name=TheSecretary",     # Name of the executable
    "--onedir",                # One directory bundle
    "--noconfirm",             # Overwrite output directory
    "--console",               # Show console
    "--clean",                 # Clean cache
    "--hidden-import=docxtpl",
    "--hidden-import=python-docx",
    "--hidden-import=google.generativeai",
    "--hidden-import=telebot",
    "--hidden-import=supabase",
    "--hidden-import=langgraph",
    "--hidden-import=PIL",
    "--hidden-import=pypdf"
]

# Add data arguments for internal bundle
for d in datas:
    args.append(f"--add-data={d}")

PyInstaller.__main__.run(args)

print("PyInstaller Build Complete.")

# --- POST BUILD STEPS ---
print("Performing Post-Build Operations...")

dist_path = os.path.join("dist", "TheSecretary")

# 1. Copy Templates to Root (for user editing)
src_templates = "templates"
dst_templates = os.path.join(dist_path, "templates")
if os.path.exists(src_templates):
    if os.path.exists(dst_templates):
        shutil.rmtree(dst_templates) 
    shutil.copytree(src_templates, dst_templates)
    print(f"Copied {src_templates} to {dst_templates}")

# 2. Copy README and USER_MANUAL if exists
files_to_copy = ["README.md", "USER_MANUAL.md"]
for f in files_to_copy:
    if os.path.exists(f):
        shutil.copy2(f, os.path.join(dist_path, f))
        print(f"Copied {f}")

print("Build & Packaging Complete! Check the 'dist/TheSecretary' folder.")
