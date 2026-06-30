from fpdf import FPDF
from datetime import datetime


class ReguDriftPitchPDF(FPDF):
    def header(self):
        # Full Page Dark Background
        self.set_fill_color(19, 19, 20)
        self.rect(0, 0, 210, 297, 'F')

        # Premium Midnight Slate Corporate Palette
        self.set_fill_color(11, 15, 25)  # Primary Midnight Canvas (#0B0F19)
        self.rect(0, 0, 210, 28, 'F')

        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 16)
        self.text(12, 12, "REGUDRIFT AI")

        self.set_font("Helvetica", "I", 9)
        self.set_text_color(164, 174, 196)
        self.text(12, 18, "Continuous Infrastructure Compliance Engine for Financial Institutions")

        self.set_font("Helvetica", "B", 8)
        self.set_text_color(16, 185, 129)  # Success Emerald Green
        self.text(150, 12, "MARKET BRIEFING & MVP BRIEF")

        self.set_text_color(141, 152, 178)
        self.set_font("Courier", "", 8)
        self.text(150, 18, f"COMPILE DATE: {datetime.now().strftime('%m/%d/%Y')}")
        self.ln(24)

    def footer(self):
        self.set_y(-18)
        self.set_fill_color(19, 19, 20)  # Surface Dim (#131314)
        self.rect(0, 282, 210, 15, 'F')

        self.set_font("Helvetica", "I", 8)
        self.set_text_color(100, 110, 130)
        self.cell(0, 10, "CONFIDENTIAL - proprietary architecture summary for fintech founders & risk boards", 0, 0,
                  "L")
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "R")

    def heading_section(self, title):
        self.ln(6)
        self.set_fill_color(32, 31, 32)  # Surface Container High
        self.set_text_color(229, 226, 226)
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 7, f"  {title}", 0, 1, 'L', fill=True)
        self.ln(3)

    def sub_heading(self, text):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(195, 198, 212)
        self.cell(0, 6, text, 0, 1, 'L')
        self.ln(1)

    def body_para(self, text):
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(200, 200, 205)
        self.multi_cell(0, 5, text)
        self.ln(2)

    def bullet_point(self, title, description):
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(245, 158, 11)  # Alert Amber
        self.write(5, "  * ")
        self.set_text_color(220, 220, 225)
        self.write(5, f"{title}: ")
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(180, 180, 185)
        self.write(5, f"{description}\n")


# Initialization and Document Rules Setup
pdf = ReguDriftPitchPDF()
pdf.set_auto_page_break(auto=True, margin=20)
pdf.add_page()
pdf.set_margins(12, 15, 12)

# --- SECTION 1 ---
pdf.heading_section("1. THE STATUS QUO & TRADITIONAL COMPLIANCE FRICTION")
pdf.body_para(
    "In the modern financial technology ecosystem, staying compliant has evolved into a highly reactive, "
    "multi-million-dollar operational friction point. Regulators like SEBI, RBI, and international frameworks "
    "demand strict technical protections. However, a systemic gap exists between written regulations and "
    "active system configurations."
)
pdf.ln(2)
pdf.bullet_point("The Text-to-Code Disconnect",
                 "Regulators publish massive, text-heavy legal directive manuals, while cloud engineers operate entirely via Infrastructure-as-Code (laC) repositories like Terraform. There is no structural interface linking abstract guidelines to production templates.")
pdf.bullet_point("The Point-in-Time Audit Trap",
                 "Traditional security reviews are manual, expensive, and point-in-time. The moment external advisors complete a quarterly review, a single developer pushing a microservice update can instantly drift the environment out of regulatory alignment.")
pdf.bullet_point("Engineering Throughput Loss",
                 "When an official audit window approaches, senior cloud developers must abandon core feature sprints to manually scrub infrastructure logs, scrape environment schemas, and compile historical validation evidence.")

# --- SECTION 2 ---
pdf.heading_section("2. THE SOLUTION: REGUDRIFT AI AUTOMATION CELL")
pdf.body_para(
    "ReguDrift AI solves this friction by acting as a real-time semantic translation middleware layer between "
    "dense legal guidelines and internal cloud states. The architecture compiles a continuous evaluation engine:"
)
pdf.ln(1)
pdf.bullet_point("Semantic Legal Parser",
                 "Ingests complex PDF manual guidelines, automatically partitioning long-form parameters into distinct, overlapping contextual target evaluation clauses.")
pdf.bullet_point("Qdrant Proximity Vector Search",
                 "Maps abstract technical descriptions straight to concrete code blocks via vector proximity search. The system recognizes that code parameters mean the same thing as legal mandates, even when using entirely distinct terminology.")
pdf.bullet_point("Automated Continuous Verification",
                 "Runs checks on every infrastructure delta, alerting security officers to structural drifts the precise second an unsafe asset modification enters the staging stream.")

# --- SECTION 3 ---
pdf.heading_section("3. PROVING THE VALUE PROFILE: EVIDENCE MATRIX (SESSION #7)")
pdf.body_para(
    "To demonstrate the immediate operational risk reduction, let us evaluate the automated execution path "
    "of our compliance core during a simulation run against an enterprise financial framework (Session #7):"
)
pdf.ln(2)

# Custom Visual Layout Box for Health Score Drop
pdf.set_fill_color(147, 0, 10)  # Warning Red Hue Container
pdf.rect(12, pdf.get_y(), 186, 12, 'F')
pdf.set_font("Helvetica", "B", 10)
pdf.set_text_color(255, 218, 214)
pdf.text(16, pdf.get_y() + 8, "CRITICAL COMPLIANCE DRIFT DETECTED: AUDIT HEALTH DROPPED TO 45%")
pdf.ln(15)

pdf.sub_heading("Isolated Delta Vulnerability Gaps:")
pdf.bullet_point("Vulnerability 1 (Log Stream Integrity)",
                 "SEBI directive requires centralized log repositories to be cryptographically signed at the application level using HMAC-SHA256 signatures before persistence. The live environment was found lacking signature injection pipelines.")
pdf.bullet_point("Vulnerability 2 (Storage Encryption Standards)",
                 "Regulations mandate log aggregate storage utilize dedicated Customer-Managed Keys (CMK) with automated annual rotation. ReguDrift caught an AWS container running default cloud-provider keys (storage_encrypted=false).")

# --- SECTION 4 ---
pdf.add_page()  # Shift to page 2 for high-density code and ROI data
pdf.heading_section("4. AUTOMATED REMEDIATION BLUEPRINT CODES")
pdf.body_para(
    "ReguDrift AI does not merely call out system flaws; it builds the concrete code required to fix them. "
    "Below is the exact, type-safe Terraform block compiled automatically by our remediation module to "
    "resolve the storage container encryption breach, enforcing CMK configurations and programmatic annual key rotation:"
)
pdf.ln(2)

# Code Block Emulation Window
pdf.set_fill_color(5, 7, 11)  # Terminal Dark Black Code Canvas
pdf.rect(12, pdf.get_y(), 186, 44, 'F')
pdf.set_font("Courier", "", 8.5)
pdf.set_text_color(141, 152, 178)  # Monospace gray text
pdf.text(16, pdf.get_y() + 6, "# Auto-generated remediation code block for Regulatory Clause 4.2(b)")
pdf.text(16, pdf.get_y() + 12, "resource \"aws_kms_key\" \"telemetry_encryption\" {")
pdf.text(16, pdf.get_y() + 18, "  description             = \"KMS key for financial telemetry DB\"")
pdf.text(16, pdf.get_y() + 24, "  enable_key_rotation     = true  # Resolves regulatory compliance drift")
pdf.text(16, pdf.get_y() + 30, "}")
pdf.text(16, pdf.get_y() + 36, "resource \"aws_rds_cluster\" \"financial_telemetry\" {")
pdf.text(16, pdf.get_y() + 42, "  storage_encrypted       = true; kms_key_id = aws_kms_key.telemetry_encryption.arn")
pdf.text(16, pdf.get_y() + 48, "}")
pdf.ln(54)

# --- SECTION 5 ---
pdf.heading_section("5. EXECUTIVE ADVANTAGES & BUSINESS METRICS ACCELERATION")
pdf.body_para(
    "Deploying ReguDrift AI inside a financial ecosystem transitions compliance operations from an expensive risk "
    "mitigation task into an automated infrastructure asset:"
)
pdf.ln(1)
pdf.bullet_point("100% Secure Local Deployment",
                 "Financial institutions cannot pass infrastructure metadata or logs to external third-party public models. ReguDrift AI is containerized locally, running completely within your private cloud environment boundaries.")
pdf.bullet_point("Instant Executive Boardroom Reporting",
                 "Eliminates weeks of presentation formatting. At any moment, risk officers can extract professional, courtroom-grade audit maps containing structural proof and timestamps with one click.")
pdf.bullet_point("Reclaim 10+ Weeks of Product Development",
                 "By provisioning automated code blueprints directly to developers, infrastructure engineers avoid manual research and can fix vulnerabilities in minutes, accelerating feature release timelines.")

# --- CALL TO ACTION ---
pdf.ln(6)
pdf.set_fill_color(11, 25, 40)  # Deep Navy CTA Highlight Box
pdf.rect(12, pdf.get_y(), 186, 18, 'F')
pdf.set_font("Helvetica", "B", 10)
pdf.set_text_color(255, 255, 255)
pdf.text(16, pdf.get_y() + 7, "PROSPECTUS NEXT STEP STRATEGY:")
pdf.set_font("Helvetica", "", 9.5)
pdf.set_text_color(180, 200, 220)
pdf.text(16, pdf.get_y() + 13,
         "Schedule a 15-minute secure container demo to check your cloud clusters for hidden regulatory drift.")

# Output Save Target
pdf.output("ReguDrift_AI_Fintech_Pitch.pdf")
print("Success! Pitch Prospectus PDF Document built safely inside your project environment.")