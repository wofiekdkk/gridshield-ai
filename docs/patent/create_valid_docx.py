"""
Native OpenXML Microsoft Word (.docx) Generator for Patent Application
Creates a 100% compliant .docx ZIP package using Python standard library.
"""
import os
import zipfile
from xml.sax.saxutils import escape
import datetime

PATENT_DIR = "D:/gridshield-ai/docs/patent"
os.makedirs(PATENT_DIR, exist_ok=True)
DOCX_PATH = os.path.join(PATENT_DIR, "GridShield_AI_Patent_Application.docx")

# Patent Document Text Data
TITLE = "Constraint-Aware AIoT Power Grid Self-Healing and Autonomous Fault Recovery System Using Digital Twin, Multi-Modal Anomaly Detection, Topology-Aware Fault Localization, Cascading Risk Prediction, and Recovery Optimization"

ABSTRACT = (
    "A system and method for autonomous self-healing of electrical power distribution networks comprising: "
    "a virtual power grid simulation engine (110) configured to model electrical topology and compute real-time AC power flow; "
    "a virtual Internet of Things (IoT) sensor network (120) generating multi-modal electrical measurements including voltage, current, "
    "frequency, active power, reactive power, and temperature; a multi-layer anomaly detection module (140) combining rule-based electrical "
    "constraint monitoring with isolation forest machine learning; a topology-aware fault localization engine (160) utilizing graph-theoretic "
    "analysis of the grid network to identify faulted components; a cascading failure risk predictor (170) that estimates secondary failure "
    "probabilities through graph propagation modeling; a constraint-aware recovery optimization engine (180) that generates candidate recovery "
    "configurations, validates each against hard electrical constraints including thermal limits, voltage bounds, transformer capacity, network "
    "connectivity, and critical load preservation, and selects an optimal feasible recovery plan; and a closed-loop verification module (195) "
    "that re-simulates power flow post-recovery and iterates if stability is not achieved. The system operates as a software-based digital twin (199) "
    "enabling reproducible experimentation of grid self-healing without physical hardware."
)

FIELD = (
    "The present invention relates generally to electrical power grid monitoring, fault detection, and autonomous recovery systems. "
    "More particularly, the invention relates to an integrated Artificial Intelligence of Things (AIoT) platform that combines virtual "
    "sensor infrastructure, multi-modal anomaly detection, topology-aware fault localization, cascading failure prediction, and "
    "constraint-aware recovery optimization to enable autonomous self-healing of electrical power distribution networks."
)

BACKGROUND_P1 = (
    "Electrical power grids are among the most critical and complex engineered systems in existence, comprising interconnected "
    "generators, transformers, transmission lines, substations, and millions of end-user loads. Maintaining grid stability requires "
    "continuous monitoring of electrical parameters and rapid response to faults."
)

BACKGROUND_P2 = (
    "Conventional Supervisory Control and Data Acquisition (SCADA) systems and Energy Management Systems (EMS) provide real-time monitoring "
    "of grid parameters using fixed-threshold alarms. While effective at detecting gross abnormalities, such systems suffer from significant limitations:\n"
    "1. Detection Without Understanding: Traditional systems detect anomalies but lack the capability to classify fault types, localize fault positions within grid topology, or predict cascading consequences.\n"
    "2. Lack of Cascade Modeling: Existing systems do not model cascading failure propagation. A single line failure redistributes power flows across the network, overloading adjacent components and triggering sequential trips.\n"
    "3. Absence of Constraint Reasoning: Recovery actions in conventional systems do not account for real-time electrical state limits. An automated switching action may violate thermal limits on alternate paths, creating new faults while resolving the original one.\n"
    "4. Sensor Unreliability: IoT sensor dropouts or corrupted measurements can produce readings indistinguishable from genuine grid faults, causing improper switching operations.\n"
    "5. Impracticality of Physical Testing: Experimentation on physical infrastructure is unsafe and non-reproducible."
)

SUMMARY = (
    "The present invention provides a system and method for autonomous power grid self-healing that addresses prior art deficiencies through an "
    "integrated AIoT architecture comprising seven novel subsystems operating in a closed loop:\n"
    "• Multi-Modal Virtual IoT Sensing Layer (120)\n"
    "• Multi-Layer Anomaly Detection Engine (140) combining hard rules and Isolation Forest ML\n"
    "• Topology-Aware Fault Localization Engine (160) utilizing graph-theoretic analysis\n"
    "• Cascading Failure Risk Predictor (170) estimating secondary propagation\n"
    "• Constraint-Aware Recovery Optimization Engine (180) validating thermal, voltage, and connectivity bounds\n"
    "• Closed-Loop Verification Module (195) re-simulating post-action stability\n"
    "• Digital Twin Control Center (199) rendering live grid topology."
)

DRAWINGS = (
    "FIG. 1 is a block diagram of the overall constraint-aware AIoT power grid self-healing architecture.\n"
    "FIG. 2 is a flowchart of the closed-loop autonomous self-healing pipeline execution sequence.\n"
    "FIG. 3 is an electrical single-line schematic of the virtual power grid topology with redundant interties.\n"
    "FIG. 4 is an architectural schematic of the multi-layer anomaly detection and 12-class fault classifier.\n"
    "FIG. 5 is a process flow diagram of the constraint-aware recovery optimization engine and physical gate.\n"
    "FIG. 6 is a schematic layout diagram of the digital twin control room dashboard."
)

DETAILED = (
    "Referring to FIG. 1, the system (100) comprises a virtual power grid simulation module (110), a virtual IoT sensor network (120), "
    "a data ingestion layer (130), a multi-layer anomaly detection engine (140), a fault classification module (150), a topology-aware "
    "fault localization engine (160), a cascading failure risk predictor (170), a constraint-aware recovery optimization engine (180), "
    "an action executor (190), a post-recovery verification module (195), and a digital twin interface (199).\n\n"
    "The power grid simulation module (110) computes real-time AC/DC power flow solutions using Newton-Raphson iterations. "
    "The virtual IoT sensor network (120) generates multi-modal measurements comprising voltage (V), current (I), frequency (f), active power (P), "
    "reactive power (Q), and temperature (T).\n\n"
    "The recovery engine (180) enforces hard physical constraint gates: (1) Line thermal capacity I <= I_max; (2) Voltage bounds 0.95 <= V <= 1.05 p.u.; "
    "(3) Network connectivity graph preservation; (4) Transformer capacity S <= S_rated; (5) Power balance Sum(P_gen) = Sum(P_load) + P_loss; "
    "(6) Critical load preservation (Hospitals 30 MW)."
)

CLAIMS = [
    "1. A system for autonomous self-healing of an electrical power grid, comprising:\n"
    "  (a) a power grid simulation engine (110) configured to model an electrical network topology comprising buses, generators, transmission lines, transformers, loads, and switching devices, and to compute power flow solutions;\n"
    "  (b) a virtual sensor network (120) comprising a plurality of software-simulated sensor agents configured to generate periodic multi-modal measurements including voltage, current, frequency, active power, reactive power, and temperature;\n"
    "  (c) a multi-layer anomaly detection module (140) comprising a rule-based constraint checker, a machine learning anomaly detector, and a temporal pattern analyzer;\n"
    "  (d) a fault classification module (150) configured to categorize detected anomalies into a plurality of fault types;\n"
    "  (e) a topology-aware fault localization engine (160) configured to represent the grid as a graph and compute fault probability rankings;\n"
    "  (f) a cascading failure risk predictor (170) configured to simulate power flow redistribution following a fault;\n"
    "  (g) a constraint-aware recovery optimization engine (180) configured to generate candidate recovery configurations, validate each against hard electrical constraints, reject infeasible candidates, and select an optimal feasible plan; and\n"
    "  (h) a closed-loop verification module (195) configured to re-simulate power flow post-recovery.",

    "2. The system of claim 1, wherein the hard electrical constraints comprise line thermal limits, transformer loading limits, bus voltage bounds, network connectivity requirements, generator capacity limits, power balance equations, and critical load preservation requirements.",

    "3. The system of claim 1, wherein the recovery optimization engine computes an objective function J(P) = w1*RestoredLoad - w2*CascadeRisk - w3*SwitchingCost - w4*OverloadPenalty.",

    "4. The system of claim 1, wherein the virtual sensor network generates measurements incorporating baseline operating values, stochastic noise, diurnal load patterns, inter-sensor correlations, and fault-induced deviations proportional to fault severity.",

    "5. The system of claim 1, wherein the anomaly detection module distinguishes genuine grid faults from sensor faults by cross-referencing adjacent graph sensors.",

    "6. The system of claim 1, wherein the fault classification module employs a machine learning classifier trained on simulated fault scenarios across at least twelve fault categories.",

    "7. The system of claim 1, wherein the fault localization engine uses graph-theoretic analysis to compute a ranked list of candidate fault locations with confidence scores.",

    "8. The system of claim 1, further comprising a digital twin visualization interface configured to render grid topology, component states, sensor readings, fault locations, and recovery actions in real time via WebSockets.",

    "9. The system of claim 1, wherein the recovery optimization engine prioritizes restoration of critical loads including hospitals, emergency services, and communication infrastructure over non-critical loads.",

    "10. A method for autonomous self-healing of an electrical power grid, comprising the steps of:\n"
    "  (a) ingesting multi-modal sensor measurements from a virtual IoT sensor network;\n"
    "  (b) detecting anomalies using a multi-layer detection engine;\n"
    "  (c) classifying the detected anomaly into a fault type using a trained machine learning classifier;\n"
    "  (d) localizing the fault to a specific grid component using graph-theoretic analysis;\n"
    "  (e) predicting cascading failure risk by simulating power flow redistribution;\n"
    "  (f) generating candidate recovery configurations;\n"
    "  (g) validating candidates against hard electrical constraints and rejecting infeasible candidates;\n"
    "  (h) selecting an optimal feasible recovery plan using multi-objective optimization;\n"
    "  (i) executing the selected recovery plan on the grid simulation;\n"
    "  (j) verifying post-recovery grid stability through re-simulation; and\n"
    "  (k) iterating if stability is not achieved.",

    "11. The method of claim 10, wherein the entire detect-to-recover cycle completes in under two seconds without human intervention.",

    "12. The method of claim 10, wherein the system operates entirely within a software-based simulation environment without requiring physical electrical hardware.",

    "13. A non-transitory computer-readable medium storing instructions that, when executed by a processor, cause the processor to perform the method of claim 10.",

    "14. The system of claim 1, wherein the machine learning anomaly detector comprises an isolation forest model trained on normal operating data.",

    "15. The system of claim 1, wherein the cascading failure risk predictor computes a quantitative risk score between 0 and 1 based on severity-weighted graph propagation.",

    "16. The system of claim 1, wherein the virtual IoT sensor network simulates communication delays, packet drops, and sensor dropouts.",

    "17. The system of claim 1, wherein candidate recovery configurations generated by the recovery engine include component isolation via breaker commands, load transfer, generation adjustments, and controlled load shedding.",

    "18. The system of claim 1, wherein the digital twin visualization interface includes clickable grid components opening real-time metrics, AI confidence indicators, and fault risk estimates.",

    "19. The method of claim 10, further comprising logging every fault detection, classification, localization, cascade prediction, candidate plan evaluation, and recovery execution in an audit log.",

    "20. The system of claim 1, wherein the entire platform is deployed on a single computing system without external hardware dependency."
]

# OpenXML XML File Generators
def make_content_types():
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>'''

def make_rels():
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''

def make_doc_rels():
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>'''

def make_styles():
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults>
    <w:rPrDefault>
      <w:rPr>
        <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>
        <w:sz w:val="22"/>
      </w:rPr>
    </w:rPrDefault>
  </w:docDefaults>
</w:styles>'''

def build_document_xml():
    p_xml = []
    
    # Document Title
    p_xml.append('''<w:p><w:pPr><w:jc w:val="center"/><w:spacing w:after="240"/></w:pPr>
      <w:r><w:rPr><w:b/><w:sz w:val="32"/></w:rPr><w:t>PATENT APPLICATION SPECIFICATION</w:t></w:r></w:p>''')

    p_xml.append(f'''<w:p><w:pPr><w:jc w:val="center"/><w:spacing w:after="360"/></w:pPr>
      <w:r><w:rPr><w:b/><w:sz w:val="26"/></w:rPr><w:t>{escape(TITLE)}</w:t></w:r></w:p>''')

    # Filing Metadata
    meta = f"Filing Date: {datetime.date.today().strftime('%B %d, %Y')} | Classifications: H02J 3/00, G05B 23/02, G06N 20/00"
    p_xml.append(f'''<w:p><w:pPr><w:jc w:val="center"/><w:spacing w:after="480"/></w:pPr>
      <w:r><w:rPr><w:i/><w:sz w:val="20"/></w:rPr><w:t>{escape(meta)}</w:t></w:r></w:p>''')

    def add_heading(text):
        p_xml.append(f'''<w:p><w:pPr><w:spacing w:before="360" w:after="120"/><w:keepNext/></w:pPr>
          <w:r><w:rPr><w:b/><w:sz w:val="26"/><w:u w:val="single"/></w:rPr><w:t>{escape(text.upper())}</w:t></w:r></w:p>''')

    def add_paragraph(text, bold_prefix=""):
        lines = text.split('\n')
        for line in lines:
            if not line.strip():
                continue
            p_xml.append(f'''<w:p><w:pPr><w:jc w:val="both"/><w:spacing w:after="120"/></w:pPr>
              {"<w:r><w:rPr><w:b/></w:rPr><w:t>" + escape(bold_prefix) + "</w:t></w:r>" if bold_prefix else ""}
              <w:r><w:t>{escape(line.strip())}</w:t></w:r></w:p>''')

    # Sections
    add_heading("Abstract of the Disclosure")
    add_paragraph(ABSTRACT)

    add_heading("Technical Field of the Invention")
    add_paragraph(FIELD)

    add_heading("Background of the Invention")
    add_paragraph(BACKGROUND_P1)
    add_paragraph(BACKGROUND_P2)

    add_heading("Summary of the Invention")
    add_paragraph(SUMMARY)

    add_heading("Brief Description of the Drawings")
    add_paragraph(DRAWINGS)

    add_heading("Detailed Description of the Preferred Embodiments")
    add_paragraph(DETAILED)

    add_heading("Claims")
    p_xml.append('''<w:p><w:pPr><w:spacing w:after="180"/></w:pPr>
      <w:r><w:rPr><w:b/></w:rPr><w:t>What is claimed is:</w:t></w:r></w:p>''')

    for claim in CLAIMS:
        p_xml.append(f'''<w:p><w:pPr><w:jc w:val="both"/><w:spacing w:after="180"/><w:ind w:left="360"/></w:pPr>
          <w:r><w:t>{escape(claim)}</w:t></w:r></w:p>''')

    body = "".join(p_xml)
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    {body}
  </w:body>
</w:document>'''

# Create Genuine OpenXML .docx ZIP File
def generate_docx_zip():
    with zipfile.ZipFile(DOCX_PATH, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', make_content_types())
        z.writestr('_rels/.rels', make_rels())
        z.writestr('word/_rels/document.xml.rels', make_doc_rels())
        z.writestr('word/styles.xml', make_styles())
        z.writestr('word/document.xml', build_document_xml())
    print(f"[SUCCESS] Native Microsoft Word (.docx) Specification Created: {DOCX_PATH}")

if __name__ == "__main__":
    generate_docx_zip()
