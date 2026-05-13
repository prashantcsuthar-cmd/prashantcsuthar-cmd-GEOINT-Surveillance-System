
import streamlit as st
import PIL.Image as Image
import random
import time

# --- 1. MOCK COMPUTER VISION LAYER ---
# In Semester 3, you can replace this with: model = YOLO("best.pt")
def computer_vision_processor(uploaded_image):
    # Simulating object detection results
    possible_detections = [
        {"label": "Bunker", "is_rectangular": True, "is_new": True},
        {"label": "Convoy", "is_linear": True, "has_metal": True}
    ]
    
    # Randomly simulate what the "AI Camera" sees for this demo
    detection = random.choice(possible_detections)
    confidence = random.uniform(0.88, 0.99)
    
    # Extracting Predicates/Facts from the pixels
    extracted_facts = {
        'IsRectangular': detection.get('is_rectangular', False),
        'IsLinear': detection.get('is_linear', False),
        'HasMetallicSignature': detection.get('has_metal', False),
        'IsNew': detection.get('is_new', False),
        'CV_Confidence': confidence,
        'DetectedObject': detection['label']
    }
    return extracted_facts

# --- 2. THE KNOWLEDGE-BASED INFERENCE ENGINE (10 RULES) ---
def run_inference(facts):
    kb = facts.copy()
    trace = []
    
    # Forward Chaining Loop
    progress = True
    while progress:
        progress = False
        
        # Rule 1 & 2: Infrastructure Detection
        if kb.get('IsRectangular') and kb.get('IsNearLAC') and 'PossibleBunker' not in kb:
            kb['PossibleBunker'] = True
            trace.append("Rule 1: Geometric analysis identifies Potential Bunker near border.")
            progress = True
        
        if kb.get('PossibleBunker') and kb.get('IsNew') and 'ActiveConstruction' not in kb:
            kb['ActiveConstruction'] = True
            trace.append("Rule 2: Temporal change detection confirms Active Construction.")
            progress = True

        # Rule 3 & 4: Movement Detection
        if kb.get('HasMetallicSignature') and kb.get('IsLinear') and 'PossibleConvoy' not in kb:
            kb['PossibleConvoy'] = True
            trace.append("Rule 3: Radar signature identifies Linear Metallic Cluster (Possible Convoy).")
            progress = True
            
        if kb.get('PossibleConvoy') and kb.get('HeadingTowardBorder') and 'TacticalMovement' not in kb:
            kb['TacticalMovement'] = True
            trace.append("Rule 4: Vector analysis confirms Tactical Movement toward LAC.")
            progress = True

        # Rule 5, 6, 7: Threat Assessment
        if kb.get('TacticalMovement') and kb.get('ThreatLevel') != "High":
            kb['ThreatLevel'] = "High"
            kb['Action'] = "DEPLOY RECON DRONE"
            trace.append("Rule 6 & 7: HIGH THREAT - Immediate aerial reconnaissance required.")
            progress = True
        elif kb.get('ActiveConstruction') and kb.get('ThreatLevel') != "Medium":
            kb['ThreatLevel'] = "Medium"
            kb['Action'] = "INCREASE SATELLITE MONITORING"
            trace.append("Rule 5 & 8: MEDIUM THREAT - Persistent monitoring initiated.")
            progress = True
            
        # Rule 9: Low Threat Case
        if not kb.get('IsNew') and 'ThreatLevel' not in kb:
            kb['ThreatLevel'] = "Low"
            kb['Action'] = "ROUTINE LOGGING"
            trace.append("Rule 9: Historical object detected. Routine logging.")
            progress = True

    return kb, trace

# --- 3. STREAMLIT DASHBOARD INTERFACE ---
st.set_page_config(page_title="Advanced GEOINT AI", layout="wide")

st.title("🛡️ Advanced GEOINT Surveillance System")
st.markdown("### Integration of Computer Vision & Symbolic Reasoning")
st.write("**Lead Developer:** Prashanth C | IIT Jodhpur")

# Sidebar for Contextual Data (Human-in-the-loop)
st.sidebar.header("Operational Context")
is_near = st.sidebar.checkbox("Location is near LAC (Border)?", value=True)
heading_border = st.sidebar.checkbox("Is movement heading toward Border?")

uploaded_file = st.file_uploader("Upload Satellite Imagery or Drone Feed", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="Incoming Surveillance Feed", use_container_width=True)
    
    if st.button("Initialize AI Analysis"):
        with st.status("Analyzing Visuals & Running Inference...", expanded=True) as status:
            st.write("Extracting features via CV Layer...")
            cv_facts = computer_vision_processor(img)
            time.sleep(1)
            
            st.write("Injecting Tactical Rules...")
            context = {'IsNearLAC': is_near, 'HeadingTowardBorder': heading_border}
            final_results, log = run_inference({**cv_facts, **context})
            time.sleep(0.5)
            status.update(label="Analysis Complete!", state="complete", expanded=False)

        # Final Display
        st.divider()
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Detected Entity", final_results['DetectedObject'])
        with c2:
            st.metric("CV Confidence", f"{final_results['CV_Confidence']:.1%}")
        with c3:
            threat = final_results.get('ThreatLevel', 'Low')
            st.metric("Threat Assessment", threat)

        if threat == "High":
            st.error(f"🚨 ALERT: {final_results.get('Action')}")
        elif threat == "Medium":
            st.warning(f"⚠️ CAUTION: {final_results.get('Action')}")
        else:
            st.success(f"✅ STATUS: {final_results.get('Action')}")

        with st.expander("System Reasoning Trace (KBES Logic)"):
            for step in log:
                st.write(f"🔹 {step}")
