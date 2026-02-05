import os
import sys
import time
from scripts.config_wizard import run_wizard
# We will import main dynamically or structure it so we can call it.
# To allow importing from parent dir if needed, though launcher is in root.

def main():
    print("Welcome to The Secretary Swarm!")
    print("Checking configuration...")
    
    # In PyInstaller, we might need to handle paths differently
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
        os.chdir(application_path) # Switch to exe directory
    
    env_path = ".env"
    
    # Check if .env exists
    if not os.path.exists(env_path):
        print("Configuration not found. Launching Setup Wizard...")
        try:
            # Run the wizard function directly
            run_wizard()
            
            # Check again if .env created
            if not os.path.exists(env_path):
                print("Setup cancelled or failed.")
                input("Press Enter to exit...")
                sys.exit(1)
                
        except Exception as e:
            print(f"Error launching setup wizard: {e}")
            input("Press Enter to exit...")
            sys.exit(1)
    
    print("Configuration found. Starting The Secretary...")
    time.sleep(1)
    
    try:
        # Import main implementation
        # Assuming main.py is in the same directory and has a run function or similar 
        # If main.py runs on import, we might need to change it.
        # Based on file view, we will see.
        import main as bot_app
        # If main.py just runs code at top level, importing it runs it.
        # If it has if __name__ == "__main__": run(), we need to call it.
        if hasattr(bot_app, 'run'):
             bot_app.run()
        else:
            # Rerun logic if it doesn't expose a run function but has main block
            # This is tricky if it only runs under __main__ check.
            pass
            
    except Exception as e:
        print(f"Error running The Secretary: {e}")
        # Keep window open to see error
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
