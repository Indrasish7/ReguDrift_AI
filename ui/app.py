import os
import asyncio
import streamlit as tf  # Streamlit standard import as tf or st, let's use standard st for code readability
import httpx
import pandas as pd
from reporter import CompliancePDFReporter


# Setup page layout metadata
st = tf # Standard convention mapping
st.set_page_config(
    page_title="ReguDrift AI | Compliance Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fetch dynamic backend container URL from environment
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# SaaS Custom Aesthetics Injection
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .main-header {
        font-size: 2.6rem;
        font-weight: 700;
        background: linear-gradient(135deg, #FF4B4B, #FF8F8F);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: #B0B0B0;
        margin-bottom: 2rem;
    }
    
    .status-card {
        padding: 1.2rem;
        border-radius: 12px;
        background-color: #1E222A;
        border: 1px solid #2A303C;
        margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar System Health Status Console
st.sidebar.image(
    "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=400&q=80",
    use_container_width=True,
    caption="ReguDrift AI Core"
)
st.sidebar.title("System Status")
st.sidebar.markdown("---")

# Query health of the backend container dynamically
try:
    response = httpx.get(f"{BACKEND_URL}/health", timeout=3.0)
    if response.status_code == 200:
        health_data = response.json()
        st.sidebar.success("● Gateway Online")
        st.sidebar.info(f"Environment: **{health_data.get('env', 'production').upper()}**")
        st.sidebar.info(f"Vector Store: **{health_data.get('vector_store_provider', 'qdrant').upper()}**")
    else:
        st.sidebar.error("▲ Gateway Offline")
except Exception:
    st.sidebar.error("▲ Gateway Unreachable")

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **ReguDrift AI v1.0.0**  
    Enterprise Regulatory Auditing & Compliance Delta Persistence Carrier.
    """
)

# App Main Hero Section
st.markdown("<h1 class='main-header'>🛡️ ReguDrift AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Asynchronous Enterprise Compliance Drift Auditor & Actionable Remediation Console</p>", unsafe_allow_html=True)

# Tabs Navigation Setup
tab1, tab2, tab3 = st.tabs([
    "📥 Policy Ingestion Hub", 
    "⚡ Live Audit Console", 
    "📊 Risk & Remediation Center"
])

# Initialize session state for holding telemetry payload between reloads
if "analysis_payload" not in st.session_state:
    st.session_state.analysis_payload = None
if "relational_record_id" not in st.session_state:
    st.session_state.relational_record_id = None


# =====================================================================
# TAB 1: POLICY INGESTION HUB
# =====================================================================
with tab1:
    st.header("Upload Policy Documents")
    st.write(
        "Ingest internal operations guidelines, security manuals, or compliance manuals. "
        "Files will be parsed asynchronously into logical clauses, indexed with parent hierarchies, "
        "and embedded for semantic lookup."
    )
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Data Upload Configuration")
        document_id = st.text_input(
            "Document ID Slug", 
            value="internal_security_v1",
            help="Unique code identifier for mapping references."
        )
        uploaded_file = st.file_uploader(
            "Choose policy document", 
            type=["txt", "pdf"],
            help="Supports structured PDF files or raw TXT documents."
        )
        
        if st.button("Index and Store Policy"):
            if not uploaded_file:
                st.warning("Please upload a file before indexing.")
            else:
                with st.spinner("Processing document stream, segmenting clauses, and generating embeddings..."):
                    try:
                        # Convert uploaded file to dynamic byte payload
                        file_bytes = uploaded_file.read()
                        files = {"file": (uploaded_file.name, file_bytes, uploaded_file.type)}
                        data = {"document_id": document_id}
                        
                        response = httpx.post(
                            f"{BACKEND_URL}/api/v1/compliance/ingest",
                            data=data,
                            files=files,
                            timeout=60.0
                        )
                        
                        if response.status_code == 201:
                            ingest_data = response.json()
                            st.success(f"🎉 Policy document successfully indexed!")
                            
                            # Cache values in session state
                            st.session_state.last_ingested_id = ingest_data.get("document_id")
                            st.session_state.last_chunks_count = ingest_data.get("chunks_count")
                            st.session_state.last_record_id = ingest_data.get("relational_record_id")
                        else:
                            st.error(f"Failed to ingest document: {response.text}")
                    except Exception as e:
                        st.error(f"Connection to backend failed: {e}")
                        
    with col2:
        st.subheader("Ingestion Status Feed")
        if "last_ingested_id" in st.session_state:
            st.markdown(
                f"""
                <div class="status-card">
                    <h4>Latest Ingested Run</h4>
                    <p>Doc ID: <b>{st.session_state.last_ingested_id}</b></p>
                    <p>Relational SQL Record ID: <b>{st.session_state.last_record_id}</b></p>
                    <p>Total Chunks Embedded: <b>{st.session_state.last_chunks_count}</b></p>
                    <p style="color: #4CAF50;">● Ingested and Indexed</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.info("No policy indexed in this session yet. Upload a document to view coordinates.")


# =====================================================================
# TAB 2: LIVE AUDIT CONSOLE
# =====================================================================
with tab2:
    st.header("Trigger Regulatory Update Audit")
    st.write(
        "Paste new regulatory bulletins, compliance changes, or legal updates below. "
        "The stateful agent loop will parse the update, search our active vector index for policy matches, "
        "and draft detailed remediation blueprints."
    )
    st.markdown("---")
    
    update_text = st.text_area(
        "Raw Regulatory Bulletin Payload",
        height=200,
        placeholder="Example: Section 1.2: Central telemetry console and log files must be cryptographically protected using active encryption keys."
    )
    
    if st.button("Execute Regulatory Drift Analysis"):
        if not update_text.strip():
            st.warning("Please paste regulatory text to evaluate.")
        else:
            # We display status progress updates keeping the user engaged in standard SaaS mode
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            async def run_analysis():
                try:
                    status_text.text("1. Creating Plan & Search queries...")
                    progress_bar.progress(15)
                    
                    status_text.text("2. Querying active Vector database and aggregating evidence...")
                    progress_bar.progress(40)
                    
                    status_text.text("3. Analyzing compliance gaps and drift evidence...")
                    progress_bar.progress(65)
                    
                    status_text.text("4. Compiling Remediation Blueprints and historical logs...")
                    progress_bar.progress(85)
                    
                    # Execute FastAPI rest call
                    payload = {"update_text": update_text}
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            f"{BACKEND_URL}/api/v1/compliance/analyze",
                            json=payload,
                            timeout=120.0
                        )
                        
                    progress_bar.progress(100)
                    status_text.text("Analysis complete!")
                    
                    if response.status_code == 200:
                        res_data = response.json()
                        st.session_state.relational_record_id = res_data.get("relational_record_id")
                        st.session_state.analysis_payload = res_data.get("telemetry")
                        st.success("Audit complete! Proceed to the 'Risk & Remediation Center' to view reports.")
                    else:
                        st.error(f"Analysis request failed: {response.text}")
                except Exception as e:
                    progress_bar.progress(100)
                    status_text.text("Analysis failed.")
                    st.error(f"Failed to communicate with API Gateway: {e}")
                    
            asyncio.run(run_analysis())


# =====================================================================
# TAB 3: RISK & REMEDIATION CENTER
# =====================================================================
with tab3:
    st.header("Drift & Risk Assessment Findings")
    st.write(
        "Parses the consolidated Audit persistence records. Review threat severities, "
        "compliance metrics, and structured blueprints."
    )
    st.markdown("---")
    
    payload = st.session_state.analysis_payload
    record_id = st.session_state.relational_record_id
    
    if not payload:
        st.info("No compliance audit results cached. Paste a regulatory bulletin in 'Live Audit Console' and analyze.")
    else:
        report = payload.get("report")
        analysis = payload.get("analysis")
        plan = payload.get("plan")
        
        # Display key executive stats
        col1, col2, col3, col4 = st.columns(4)
        
        # 1. Overall Status with custom HSL alert coloring
        status_value = "Compliant"
        if report:
            # Map status based on matrices
            statuses = [gap.get("status") for gap in report.get("compliance_drift_matrix", [])]
            if "Non-Compliant" in statuses:
                status_value = "Non-Compliant"
            elif "Partial" in statuses:
                status_value = "Partial"
                
        with col1:
            if status_value == "Non-Compliant":
                st.markdown(
                    '<div style="background-color: #5C1D1D; padding: 1rem; border-radius: 8px; border: 1px solid #FF4B4B;">'
                    f'<p style="margin:0; font-size:0.8rem; color:#FFA5A5;">OVERALL STATUS</p>'
                    f'<h3 style="margin:0; color:#FF8888;">● {status_value}</h3>'
                    '</div>',
                    unsafe_allow_html=True
                )
            elif status_value == "Partial":
                st.markdown(
                    '<div style="background-color: #5C4A1D; padding: 1rem; border-radius: 8px; border: 1px solid #FFC83B;">'
                    f'<p style="margin:0; font-size:0.8rem; color:#FFEAA5;">OVERALL STATUS</p>'
                    f'<h3 style="margin:0; color:#FFE088;">▲ {status_value}</h3>'
                    '</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    '<div style="background-color: #1D5C2C; padding: 1rem; border-radius: 8px; border: 1px solid #4CAF50;">'
                    f'<p style="margin:0; font-size:0.8rem; color:#A5FFA5;">OVERALL STATUS</p>'
                    f'<h3 style="margin:0; color:#88FF88;">✔ {status_value}</h3>'
                    '</div>',
                    unsafe_allow_html=True
                )
                
        with col2:
            st.metric("SQL Audit ID", f"#{record_id}" if record_id != -1 else "N/A")
        with col3:
            st.metric("Gaps Located", len(report.get("drift_remediation_blueprints", [])) if report else 0)
        with col4:
            st.metric("Remediation Effort", f"{report.get('remediation_timeline_weeks', 0)} Weeks" if report else "0 Weeks")
            
        st.markdown("---")
        
        # Display Plan objectives and Executive Summary
        col_left, col_right = st.columns([1, 2])
        
        with col_left:
            st.subheader("Analysis Objectives")
            if plan:
                for obj in plan.get("analysis_objectives", []):
                    st.markdown(f"- {obj}")
            else:
                st.write("No plan objectives recorded.")
                
            st.subheader("Executed Search Queries")
            if plan:
                for q in plan.get("search_queries", []):
                    st.code(q)
                    
        with col_right:
            st.subheader("Executive Audit Summary")
            if report:
                st.info(report.get("executive_summary"))
            else:
                st.write("No executive summary compiled.")
                
        st.markdown("---")
        
        # Display Compliance Drift Matrix table
        st.subheader("Compliance Drift Matrix mappings")
        if report:
            matrix_data = []
            for item in report.get("compliance_drift_matrix", []):
                matrix_data.append({
                    "Regulatory Clause": item.get("regulatory_clause"),
                    "Internal Policy Ref": item.get("internal_policy_reference"),
                    "Status": item.get("status"),
                    "Delta Mapping Details": item.get("delta_evidence")
                })
            df = pd.DataFrame(matrix_data)
            st.dataframe(df, use_container_width=True)
            
        st.markdown("---")
        
        # Display Actionable Remediation Blueprints
        st.subheader("Technical Remediation Blueprints")
        if report:
            blueprints = report.get("drift_remediation_blueprints", [])
            if not blueprints:
                st.success("No compliance drift gaps found! System remains fully aligned.")
            else:
                for bp in blueprints:
                    severity = bp.get("severity_rating", "LOW")
                    clarity = bp.get("clarity_score", 100)
                    clause = bp.get("clause_at_risk")
                    blueprint_text = bp.get("technical_remediation_blueprint")
                    
                    # Highlight blueprint headers according to severity
                    if severity in ["HIGH", "CRITICAL"]:
                        header_html = f'<span style="background-color: #5C1D1D; padding: 4px 8px; border-radius: 4px; color: #FF8888; font-weight:bold;">{severity}</span>'
                    elif severity == "MEDIUM":
                        header_html = f'<span style="background-color: #5C4A1D; padding: 4px 8px; border-radius: 4px; color: #FFE088; font-weight:bold;">{severity}</span>'
                    else:
                        header_html = f'<span style="background-color: #2E5C1D; padding: 4px 8px; border-radius: 4px; color: #88FF88; font-weight:bold;">{severity}</span>'
                        
                    with st.expander(f"Gap: {clause}"):
                        st.markdown(
                            f"""
                            **Severity Rating**: {header_html}  
                            **Regulatory Clarity Score**: `{clarity}/100`
                            
                            **Engineering Remediation blueprint Guide**:
                            
                            {blueprint_text}
                            """,
                            unsafe_allow_html=True
                        )
                
            # --- PDF Generation and Export Engine ---
            st.markdown("---")
            st.subheader("Executive PDF Export Center")
            st.write(
                "Compile and download a formal, institutional-grade compliance gap audit report "
                "containing the executive summary, findings matrix, and remediation blueprints."
            )
            
            try:
                # Compile PDF bytes dynamically using session state data
                pdf_bytes = CompliancePDFReporter.build_audit_pdf(payload, record_id)
                
                st.download_button(
                    label="📥 Download Institutional PDF Audit Report",
                    data=pdf_bytes,
                    file_name=f"ReguDrift_Audit_Report_ID{record_id}.pdf",
                    mime="application/pdf",
                    help="Compiles the visual corporate-branded PDF including code-block blueprints."
                )
            except Exception as e:
                st.error(f"Failed to generate PDF Report: {e}")
