
import sys
import os
import json

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.workflow import graph_app

def test_related():
    print("🧪 Testing Related Commands...")
    print("-----------------------------------")
    
    thread_id = "test_user_connected_cmds"
    config = {"configurable": {"thread_id": thread_id}}
    
    # Turn 1: Broad Intent
    input_1 = "Buatkan surat undangan rapat evaluasi."
    print(f"\n[Turn 1] User: '{input_1}'")
    state_1 = graph_app.invoke({"user_input": input_1}, config=config)
    
    # Check Turn 1 Result
    json_1 = state_1.get('parsed_json')
    print(f"   📋 JSON 1: {json_1}")
    
    # Turn 2: Specific Detail (Refinement)
    input_2 = "Jam 8 malam."
    print(f"\n[Turn 2] User: '{input_2}'")
    state_2 = graph_app.invoke({"user_input": input_2}, config=config)
    
    # Check Turn 2 Result
    # Ideally, this should contain the Merged info (Undangan + Jam 8 malam)
    # OR at least the agent should understand it refers to the previous context.
    json_2 = state_2.get('parsed_json')
    print(f"   📋 JSON 2: {json_2}")
    
    # Analysis
    if json_2:
        parsed = json.loads(json_2)
        if parsed.get('intent_type') == 'WORK':
            print("\n✅ Listener identified WORK intent.")
            # Check if it kept the 'undangan_internal' kind or lost it
            if parsed.get('jenis_surat') == 'undangan_internal':
                print("   🤯 AMAZING: It remembered 'undangan_internal'!")
            else:
                print("   ⚠️ ISSUE: It forgot 'undangan_internal' (Context lost).")
                
            if parsed.get('data', {}).get('waktu') == '20:00': # 8 malam
                print("   ✅ Time extracted correctly.")
        else:
            print("\n❌ Listener failed to identify WORK intent (likely classified as CHAT or Ask).")

if __name__ == "__main__":
    test_related()
