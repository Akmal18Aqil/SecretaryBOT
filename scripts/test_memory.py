
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.workflow import graph_app

def test_memory():
    print("🧠 Testing Memory (Checkpointers)...")
    print("-----------------------------------")
    
    thread_id = "test_user_007"
    config = {"configurable": {"thread_id": thread_id}}
    
    # 1. Turn 1: Initial Request (incomplete info)
    print("\n[Turn 1] User: 'Buatkan surat.'")
    # Simulate a generic request. In a real scenario, the bot would ask for more info.
    # For this test, we just want to see if the state is saved.
    inputs_1 = {"user_input": "Buatkan surat."}
    state_1 = graph_app.invoke(inputs_1, config=config)
    
    print(f"✅ Turn 1 Finished. State ID: {thread_id}")
    
    # 2. Turn 2: Follow up
    print("\n[Turn 2] User: 'Undangan rapat.'")
    inputs_2 = {"user_input": "Undangan rapat."}
    
    # We inspect the graph state BEFORE Turn 2 using get_state to see if it remembers Turn 1
    current_snapshot = graph_app.get_state(config)
    print(f"🧐 Memory Inspection (Pre-Turn 2):")
    if current_snapshot.values:
        print(f"   Saved State keys: {list(current_snapshot.values.keys())}")
        print(f"   Last user_input in memory: '{current_snapshot.values.get('user_input')}'")
        
        if current_snapshot.values.get('user_input') == "Buatkan surat.":
            print("   ✅ SUCCESS: Bot remembers 'Buatkan surat.'")
        else:
            print("   ❌ FAIL: Bot forgot Turn 1.")
    else:
        print("   ❌ FAIL: No state found.")
            
    # Execute Turn 2
    state_2 = graph_app.invoke(inputs_2, config=config)
    print("\n✅ Turn 2 Finished.")

if __name__ == "__main__":
    test_memory()
