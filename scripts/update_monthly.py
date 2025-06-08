import subprocess
from pathlib import Path

print("🚀 Starting monthly digest generation...")

# Run the updated generate_all_monthlies.py
subprocess.run(["python", "generate_all_monthlies.py"], check=True)

# Stage changes in monthly/
print("📦 Staging monthly digest updates...")
subprocess.run(["git", "add", "monthly/"], check=True)

# Commit the changes
print("📝 Committing updates...")
subprocess.run(["git", "commit", "-m", "Auto-update monthly digests"], check=True)

# Push to the remote
print("🌐 Pushing to GitHub...")
subprocess.run(["git", "push"], check=True)

print("✅ Monthly digest update complete.")
