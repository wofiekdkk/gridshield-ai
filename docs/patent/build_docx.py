"""
Native Microsoft Word (.docx) Generator for Patent Application
Uses python-docx to generate 100% compliant, native Word documents.
"""
import os
import datetime
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

PATENT_DIR = "D:/gridshield-ai/docs/patent"
os.makedirs(PATENT_DIR, exist_ok=True)
DOCX_PATH = os.path.join(PATENT_DIR, "GridShield_AI_Patent_Application.docx")

doc = Document()

# Set Standard Margins (1 inch / 72 pt)
sections = doc.sections
for section in sections:
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)

# Configure Default Styles
normal_style = doc.styles['Normal']
normal_style.font.name = 'Times New Roman'
normal_style.font.size = Pt(11)
normal_style.font.color.rgb = RGBColor(0x11, 0x11, 0x11)
normal_style.paragraph_format.line_spacing = 1.15
normal_style.paragraph_format.space_after = Pt(6)

def add_title(text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(24)
    p.paragraph_format.space_after = Pt(12)
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(16)
    run.font.bold = True
    return p

def add_heading_1(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text.upper())
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.font.bold = True
    run.font.underline = True
    return p

def add_heading_2(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(11)
    run.font.bold = True
    run.font.italic = True
    return p

def add_body(text, bold_prefix=""):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_after = Pt(6)
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.bold = True
    p.add_run(text)
    return p

def add_claim(number_str, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.left_indent = Inches(0.25)
    p.paragraph_format.space_after = Pt(8)
    r_num = p.add_run(number_str)
    r_num.font.bold = True
    p.add_run(" " + text)
    return p

# -------------------------------------------------------------
# COVER PAGE / HEADER
# -------------------------------------------------------------
add_title("PATENT APPLICATION SPECIFICATION")

p_sub = doc.add_paragraph()
p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_sub.paragraph_format.space_after = Pt(18)
r_sub = p_sub.add_run(
    "Constraint-Aware AIoT Power Grid Self-Healing and Autonomous Fault Recovery System Using Digital Twin, "
    "Multi-Modal Anomaly Detection, Topology-Aware Fault Localization, Cascading Risk Prediction, and Recovery Optimization"
)
r_sub.font.size = Pt(13)
r_sub.font.bold = True

meta_p = doc.add_paragraph()
meta_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
meta_p.paragraph_format.space_after = Pt(24)
r_meta = meta_p.add_run(
    f"Filing Date: {datetime.date.today().strftime('%B %d, %Y')}\n"
    "Application Number: [To Be Assigned]\n"
    "International Classifications: H02J 3/00, G05B 23/02, G06N 20/00, G06F 30/18\n"
    "Inventor(s): [Full Legal Name(s)] | Assignee: [University / Organization Name]"
)
r_meta.font.size = Pt(9.5)
r_meta.font.italic = True

# -------------------------------------------------------------
# ABSTRACT
# -------------------------------------------------------------
add_heading_1("Abstract of the Disclosure")
add_body(
    "A system and method for autonomous self-healing of electrical power distribution networks comprising: "
    "a virtual power grid simulation engine (110) configured to model electrical topology and compute real-time AC power flow; "
    "a virtual Internet of Things (IoT) sensor network (120) generating multi-modal electrical measurements including voltage, current, "
    "frequency, active power, reactive power, and temperature; a high-concurrency relational telemetry database (135) with B-tree timestamp indexing; "
    "a multi-layer anomaly detection module (140) combining rule-based electrical constraint monitoring with isolation forest machine learning; "
    "a topology-aware fault localization engine (160) utilizing graph-theoretic analysis of the grid network to identify faulted components; "
    "a cascading failure risk predictor (170) that estimates secondary failure probabilities through graph propagation modeling; "
    "a constraint-aware recovery optimization engine (180) that generates candidate recovery configurations, validates each against hard electrical constraints "
    "including thermal limits, voltage bounds, transformer capacity, network connectivity, and critical load preservation, and selects an optimal feasible recovery plan; "
    "and a closed-loop verification module (195) that re-simulates power flow post-recovery and iterates if stability is not achieved. "
    "The system operates as a software-based digital twin (199) enabling reproducible experimentation of grid self-healing without physical hardware."
)

# -------------------------------------------------------------
# TECHNICAL FIELD
# -------------------------------------------------------------
add_heading_1("Technical Field of the Invention")
add_body(
    "The present invention relates generally to electrical power grid monitoring, fault detection, and autonomous recovery systems. "
    "More particularly, the invention relates to an integrated Artificial Intelligence of Things (AIoT) platform that combines virtual "
    "sensor infrastructure, high-throughput time-series database storage, multi-modal anomaly detection, topology-aware fault localization, "
    "cascading failure prediction, 24-hour predictive load forecasting, and constraint-aware recovery optimization to enable autonomous self-healing of electrical power networks."
)

# -------------------------------------------------------------
# BACKGROUND OF THE INVENTION
# -------------------------------------------------------------
add_heading_1("Background of the Invention")
add_body(
    "Electrical power grids are among the most critical and complex engineered systems in existence, comprising interconnected "
    "generators, transformers, transmission lines, substations, and millions of end-user loads. Maintaining grid stability requires "
    "continuous monitoring of electrical parameters and rapid response to faults."
)
add_body(
    "Conventional Supervisory Control and Data Acquisition (SCADA) systems and Energy Management Systems (EMS) provide real-time monitoring "
    "of grid parameters using fixed-threshold alarms. While effective at detecting gross abnormalities, such systems suffer from significant limitations:\n\n"
    "1. Detection Without Understanding: Traditional systems detect anomalies but lack the capability to classify fault types, localize fault positions within grid topology, or predict cascading consequences.\n\n"
    "2. Lack of Cascade Modeling: Existing systems do not model cascading failure propagation. A single line failure redistributes power flows across the network, overloading adjacent components and triggering sequential trips.\n\n"
    "3. Absence of Constraint Reasoning: Recovery actions in conventional systems do not account for real-time electrical state limits. An automated switching action may violate thermal limits on alternate paths, creating new faults while resolving the original one.\n\n"
    "4. Sensor Unreliability & Database Latency: High-frequency IoT telemetry streams often cause database bottlenecks or misidentify sensor dropouts as physical grid faults.\n\n"
    "5. Impracticality of Physical Testing: Experimentation on physical infrastructure is unsafe, prohibited by regulations, and non-reproducible."
)

# -------------------------------------------------------------
# SUMMARY OF THE INVENTION
# -------------------------------------------------------------
add_heading_1("Summary of the Invention")
add_body(
    "The present invention provides a system and method for autonomous power grid self-healing that addresses prior art deficiencies through an "
    "integrated AIoT architecture comprising seven novel subsystems operating in a closed loop:\n"
    "• Multi-Modal Virtual IoT Sensing Layer (120)\n"
    "• High-Performance Relational Database (135) with Write-Ahead Logging (WAL) and B-Tree Timestamp Indexing\n"
    "• Multi-Layer Anomaly Detection Engine (140) combining hard rules and Isolation Forest ML\n"
    "• Topology-Aware Fault Localization Engine (160) utilizing graph-theoretic analysis\n"
    "• Cascading Failure Risk Predictor (170) estimating secondary propagation\n"
    "• 24-Hour Predictive Load Forecasting Module with Confidence Interval Bands\n"
    "• Constraint-Aware Recovery Optimization Engine (180) validating thermal, voltage, and connectivity bounds\n"
    "• Closed-Loop Verification Module (195) re-simulating post-action stability\n"
    "• Digital Twin Control Center (199) rendering live kinematic power flow and interactive asset health scores."
)

# -------------------------------------------------------------
# BRIEF DESCRIPTION OF THE DRAWINGS
# -------------------------------------------------------------
add_heading_1("Brief Description of the Drawings")
add_body("FIG. 1 is a formal block diagram of the overall constraint-aware AIoT power grid self-healing architecture.")
add_body("FIG. 2 is a detailed flowchart of the closed-loop autonomous self-healing pipeline execution sequence.")
add_body("FIG. 3 is an electrical single-line schematic of the virtual power grid topology with redundant interties.")
add_body("FIG. 4 is an architectural schematic of the multi-layer anomaly detection and 12-class fault classifier.")
add_body("FIG. 5 is a process flow diagram of the constraint-aware recovery optimization engine and physical gate.")
add_body("FIG. 6 is a schematic layout diagram of the digital twin control room dashboard.")

# -------------------------------------------------------------
# DETAILED DESCRIPTION
# -------------------------------------------------------------
add_heading_1("Detailed Description of the Preferred Embodiments")
add_heading_2("1. Integrated System Architecture (FIG. 1)")
add_body(
    "Referring to FIG. 1, the system (100) comprises a virtual power grid simulation module (110), a virtual IoT sensor network (120), "
    "a data ingestion layer (130), a high-concurrency database engine (135), a multi-layer anomaly detection engine (140), a fault classification module (150), "
    "a topology-aware fault localization engine (160), a cascading failure risk predictor (170), a constraint-aware recovery optimization engine (180), "
    "an action executor (190), a post-recovery verification module (195), and a digital twin interface (199).\n\n"
    "The power grid simulation module (110) computes real-time AC/DC power flow solutions using Newton-Raphson iterations. "
    "The virtual IoT sensor network (120) generates multi-modal measurements comprising voltage (V), current (I), frequency (f), active power (P), "
    "reactive power (Q), and temperature (T)."
)

add_heading_2("2. High-Concurrency Telemetry Database (135)")
add_body(
    "The database engine (135) employs a relational SQL engine configured with Write-Ahead Logging (WAL) mode to permit concurrent read and write operations "
    "from multiple virtual IoT sensor agents without database locks. A B-tree index (idx_sensor_reading_time) is established on the combination of sensor_id and timestamp, "
    "enabling time-series range queries for chart rendering with O(log N) retrieval complexity."
)

add_heading_2("3. Constraint-Aware Recovery Optimization (FIG. 5)")
add_body(
    "The recovery engine (180) enforces hard physical constraint gates:\n"
    "(1) Line thermal capacity: I <= I_max\n"
    "(2) Voltage bounds: 0.95 <= V <= 1.05 p.u.\n"
    "(3) Network connectivity graph preservation\n"
    "(4) Transformer capacity: S <= S_rated\n"
    "(5) Power balance: Sum(P_gen) = Sum(P_load) + P_loss\n"
    "(6) Critical load preservation: Hospital emergency feeders (30 MW) are maintained."
)

# -------------------------------------------------------------
# CLAIMS (1 to 20)
# -------------------------------------------------------------
add_heading_1("Claims")
p_cl = doc.add_paragraph()
p_cl.add_run("What is claimed is:").font.bold = True

claims_data = [
    ("1.", "A system for autonomous self-healing of an electrical power grid, comprising:\n"
           "  (a) a power grid simulation engine (110) configured to model an electrical network topology comprising buses, generators, transmission lines, transformers, loads, and switching devices;\n"
           "  (b) a virtual sensor network (120) comprising software-simulated sensor agents configured to generate multi-modal electrical measurements;\n"
           "  (c) a high-concurrency database (135) utilizing Write-Ahead Logging and B-Tree timestamp indexing;\n"
           "  (d) a multi-layer anomaly detection module (140) comprising a rule-based constraint checker, a machine learning anomaly detector, and a temporal analyzer;\n"
           "  (e) a fault classification module (150) categorizing anomalies into a plurality of fault types;\n"
           "  (f) a topology-aware fault localization engine (160) computing fault probability rankings across network nodes;\n"
           "  (g) a cascading failure risk predictor (170) simulating secondary failure probabilities;\n"
           "  (h) a constraint-aware recovery optimization engine (180) validating candidate plans against hard electrical limits; and\n"
           "  (i) a closed-loop verification module (195) configured to re-simulate power flow post-recovery."),
    ("2.", "The system of claim 1, wherein the hard electrical constraints comprise line thermal capacity limits, transformer loading limits, bus voltage bounds, network connectivity requirements, generator capacity limits, power balance equations, and critical load preservation requirements."),
    ("3.", "The system of claim 1, wherein the recovery optimization engine computes an objective function J(P) = w1*RestoredLoad - w2*CascadeRisk - w3*SwitchingCost - w4*OverloadPenalty."),
    ("4.", "The system of claim 1, wherein the virtual sensor network generates measurements incorporating baseline operating values, stochastic noise, diurnal load patterns, inter-sensor correlations, and fault-induced deviations proportional to fault severity."),
    ("5.", "The system of claim 1, wherein the anomaly detection module distinguishes genuine grid faults from sensor faults by cross-referencing adjacent graph sensors."),
    ("6.", "The system of claim 1, wherein the fault classification module employs a machine learning classifier trained on simulated fault scenarios across at least twelve fault categories."),
    ("7.", "The system of claim 1, wherein the fault localization engine uses graph-theoretic analysis to compute a ranked list of candidate fault locations with confidence scores."),
    ("8.", "The system of claim 1, further comprising a digital twin visualization interface configured to render grid topology, kinematic animated power flow, asset health scores (0-100), and floating telemetry badges via WebSockets."),
    ("9.", "The system of claim 1, wherein the recovery optimization engine prioritizes restoration of critical loads including hospitals, emergency services, and communication infrastructure over non-critical loads."),
    ("10.", "A method for autonomous self-healing of an electrical power grid, comprising the steps of:\n"
            "  (a) ingesting multi-modal sensor measurements into a relational time-series database;\n"
            "  (b) detecting anomalies using a multi-layer detection engine;\n"
            "  (c) classifying the anomaly into a fault type using a machine learning model;\n"
            "  (d) localizing the fault using graph-theoretic network analysis;\n"
            "  (e) predicting cascading failure risk on neighboring branches;\n"
            "  (f) synthesizing candidate recovery configurations;\n"
            "  (g) validating candidates against physical constraint gates and rejecting infeasible candidates;\n"
            "  (h) selecting an optimal feasible plan using multi-objective scoring;\n"
            "  (i) executing the plan on the grid simulation; and\n"
            "  (j) verifying post-recovery grid stability."),
    ("11.", "The method of claim 10, wherein the entire detect-to-recover cycle completes in under two seconds without human intervention."),
    ("12.", "The method of claim 10, wherein the system operates entirely within a software-based simulation environment without requiring physical electrical hardware."),
    ("13.", "A non-transitory computer-readable medium storing instructions that, when executed by a processor, cause the processor to perform the method of claim 10."),
    ("14.", "The system of claim 1, wherein the machine learning anomaly detector comprises an isolation forest model trained on normal operating data."),
    ("15.", "The system of claim 1, wherein the cascading failure risk predictor computes a quantitative risk score between 0 and 1 based on severity-weighted graph propagation."),
    ("16.", "The system of claim 1, wherein the high-concurrency database supports concurrent multi-sensor reads and writes under Write-Ahead Logging mode with sub-millisecond query latency."),
    ("17.", "The system of claim 1, wherein candidate recovery configurations generated by the recovery engine include component isolation via breaker commands, load transfer, generation adjustments, and controlled load shedding."),
    ("18.", "The system of claim 1, wherein the digital twin visualization interface renders kinematic stroke animation representing active AC power flow."),
    ("19.", "The method of claim 10, further comprising logging every fault detection, classification, localization, cascade prediction, candidate plan evaluation, and recovery execution in an audit log."),
    ("20.", "The system of claim 1, wherein the entire platform is deployed on a single computing system without external hardware dependency.")
]

for c_num, c_text in claims_data:
    add_claim(c_num, c_text)

# Save Native Document
doc.save(DOCX_PATH)
print(f"[SUCCESS] Native Microsoft Word (.docx) Patent Specification Created: {DOCX_PATH}")
