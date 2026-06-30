from fpdf import FPDF
from datetime import datetime

class CompliancePDF(FPDF):
    def __init__(self, overall_status: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.overall_status = overall_status
        self.in_cover = True

    def header(self):
        if self.in_cover:
            return
        
        # Deep Navy top line accent
        self.set_fill_color(26, 54, 93) # Deep Navy (RGB: 26, 54, 93)
        self.rect(0, 0, 210, 8, "F")
        
        self.set_y(12)
        self.set_font("helvetica", "B", 8)
        self.set_text_color(71, 85, 105) # Slate (RGB: 71, 85, 105)
        self.cell(0, 5, "REGUDRIFT AI  |  ENTERPRISE COMPLIANCE AUDIT", ln=0, align="L")
        
        # Date on right
        date_str = datetime.now().strftime("%Y-%m-%d")
        self.cell(0, 5, f"DATE: {date_str}", ln=1, align="R")
        
        # Horizontal thin dividing line
        self.set_draw_color(203, 213, 225) # Slate-200 (RGB: 203, 213, 225)
        self.line(10, 18, 200, 18)
        self.ln(5)

    def footer(self):
        if self.in_cover:
            return
            
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(148, 163, 184) # Slate-400 (RGB: 148, 163, 184)
        
        # Horizontal thin footer line
        self.set_draw_color(226, 232, 240) # Slate-100 (RGB: 226, 232, 240)
        self.line(10, self.get_y() - 2, 200, self.get_y() - 2)
        
        self.cell(0, 10, "CONFIDENTIAL  -  REGUDRIFT COMPLIANCE ENGINE", ln=0, align="L")
        # Page numbers using native {nb} placeholder
        self.cell(0, 10, f"Page {self.page_no()} of {{nb}}", ln=0, align="R")


class CompliancePDFReporter:
    @staticmethod
    def build_audit_pdf(audit_data: dict, record_id: int) -> bytes:
        """
        Builds a high-fidelity dynamic corporate PDF for regulatory compliance gap analysis.
        
        Args:
            audit_data: Dictionary holding full analysis telemetry (report, analysis, plan).
            record_id: Integer relational primary key SQL record ID.
            
        Returns:
            Raw PDF document bytes.
        """
        report = audit_data.get("report") or {}
        analysis = audit_data.get("analysis") or {}
        plan = audit_data.get("plan") or {}
        
        # Determine overall status
        status_value = "Compliant"
        statuses = [gap.get("status") for gap in report.get("compliance_drift_matrix", [])]
        if "Non-Compliant" in statuses:
            status_value = "Non-Compliant"
        elif "Partial" in statuses:
            status_value = "Partial"
            
        pdf = CompliancePDF(overall_status=status_value, orientation="P", unit="mm", format="A4")
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.alias_nb_pages()
        
        # ==========================================
        # PAGE 1: COVER PAGE
        # ==========================================
        pdf.add_page()
        pdf.in_cover = True
        
        # Elegant header accent box
        pdf.set_fill_color(26, 54, 93) # Deep Navy
        pdf.rect(0, 0, 210, 45, "F")
        
        # Red accent line
        pdf.set_fill_color(239, 68, 68) # Red accent line
        pdf.rect(0, 45, 210, 3, "F")
        
        pdf.set_y(15)
        pdf.set_font("helvetica", "B", 24)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 10, "REGUDRIFT AI", ln=1, align="C")
        
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(0, 10, "STATEFUL COMPLIANCE DRIFT AUDITING PLATFORM", ln=1, align="C")
        
        pdf.set_y(65)
        pdf.set_font("helvetica", "B", 18)
        pdf.set_text_color(30, 41, 59) # Slate-800
        pdf.cell(0, 10, "INSTITUTIONAL COMPLIANCE AUDIT REPORT", ln=1, align="L")
        
        # Draw metadata panel
        pdf.ln(5)
        pdf.set_fill_color(248, 250, 252) # Slate-50
        pdf.set_draw_color(226, 232, 240) # Slate-100
        pdf.rect(10, pdf.get_y(), 190, 65, "DF")
        
        pdf.set_y(pdf.get_y() + 5)
        pdf.set_x(15)
        pdf.set_font("helvetica", "B", 10)
        pdf.set_text_color(71, 85, 105) # Slate
        pdf.cell(50, 8, "SQL Audit Run ID:", ln=0)
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 8, f"#{record_id}" if record_id != -1 else "N/A", ln=1)
        
        pdf.set_x(15)
        pdf.set_font("helvetica", "B", 10)
        pdf.set_text_color(71, 85, 105)
        pdf.cell(50, 8, "Compliance Status:", ln=0)
        
        # Style status text
        pdf.set_font("helvetica", "B", 10)
        if status_value == "Non-Compliant":
            pdf.set_text_color(220, 38, 38) # Red
            pdf.cell(0, 8, f"{status_value} (Critical Risk Gaps Located)", ln=1)
        elif status_value == "Partial":
            pdf.set_text_color(217, 119, 6) # Orange
            pdf.cell(0, 8, f"{status_value} (Operational Alignment Gaps)", ln=1)
        else:
            pdf.set_text_color(22, 163, 74) # Green
            pdf.cell(0, 8, f"{status_value} (Full Operational Alignment)", ln=1)
            
        pdf.set_x(15)
        pdf.set_font("helvetica", "B", 10)
        pdf.set_text_color(71, 85, 105)
        pdf.cell(50, 8, "Evaluation Date:", ln=0)
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(30, 41, 59)
        date_str = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        pdf.cell(0, 8, date_str, ln=1)
        
        pdf.set_x(15)
        pdf.set_font("helvetica", "B", 10)
        pdf.set_text_color(71, 85, 105)
        pdf.cell(50, 8, "System Environment:", ln=0)
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 8, "PRODUCTION - Docker Containerized Cluster", ln=1)
        
        pdf.set_x(15)
        pdf.set_font("helvetica", "B", 10)
        pdf.set_text_color(71, 85, 105)
        pdf.cell(50, 8, "Target Vector Collection:", ln=0)
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 8, "regudrift_compliance_chunks (QDRANT)", ln=1)
        
        pdf.set_y(140)
        
        # Render a nice footer notice on cover page
        pdf.set_font("helvetica", "I", 9)
        pdf.set_text_color(100, 116, 139) # slate-500
        pdf.cell(0, 5, "This is an automated analytical compliance drift report compiled by ReguDrift AI.", ln=1, align="C")
        pdf.cell(0, 5, "Structured analysis performed using deep-semantic legal chunkers and stateful AI orchestration.", ln=1, align="C")
        
        # ==========================================
        # PAGE 2+: REPORT CONTENT
        # ==========================================
        pdf.add_page()
        pdf.in_cover = False
        
        # SECTION 1: EXECUTIVE AUDIT SUMMARY
        pdf.set_font("helvetica", "B", 14)
        pdf.set_text_color(26, 54, 93) # Deep Navy
        pdf.cell(0, 8, "1. Executive Audit Summary", ln=1, align="L")
        pdf.ln(2)
        
        # Executive Summary Callout Box
        exec_summary = report.get("executive_summary", "No executive summary compiled.")
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(51, 65, 85) # slate-700
        
        # Draw side borders and gray fill for executive summary callout box
        pdf.set_fill_color(248, 250, 252) # slate-50
        pdf.set_draw_color(71, 85, 105) # Slate
        
        width = 180
        start_y = pdf.get_y()
        pdf.set_x(15)
        pdf.multi_cell(width, 5, exec_summary, ln=1, fill=True)
        end_y = pdf.get_y()
        
        # Draw thick left line
        pdf.set_draw_color(26, 54, 93) # Deep Navy
        pdf.set_line_width(1.5)
        pdf.line(10, start_y, 10, end_y)
        pdf.set_line_width(0.2) # reset line width
        
        pdf.ln(10)
        
        # SECTION 2: COMPLIANCE DRIFT MATRIX
        pdf.set_font("helvetica", "B", 14)
        pdf.set_text_color(26, 54, 93) # Deep Navy
        pdf.cell(0, 8, "2. Compliance Drift Matrix Mappings", ln=1, align="L")
        pdf.ln(2)
        
        matrix_mappings = report.get("compliance_drift_matrix", [])
        if not matrix_mappings:
            pdf.set_font("helvetica", "I", 10)
            pdf.set_text_color(100, 116, 139)
            pdf.cell(0, 8, "No active drift matrix mappings available.", ln=1)
        else:
            for idx, mapping in enumerate(matrix_mappings):
                clause = mapping.get("regulatory_clause", "N/A")
                policy_ref = mapping.get("internal_policy_reference", "N/A")
                status = mapping.get("status", "N/A")
                delta = mapping.get("delta_evidence", "N/A")
                
                # Check for page break space (need at least 55mm)
                if pdf.get_y() > 230:
                    pdf.add_page()
                    
                start_y = pdf.get_y()
                
                # Determine color based on status
                if status == "Non-Compliant":
                    badge_bg = (254, 226, 226) # light red
                    badge_fg = (220, 38, 38) # red
                    border_color = (239, 68, 68) # red
                elif status == "Partial":
                    badge_bg = (254, 243, 199) # light yellow
                    badge_fg = (217, 119, 6) # orange
                    border_color = (245, 158, 11) # yellow-500
                else:
                    badge_bg = (220, 252, 231) # light green
                    badge_fg = (22, 163, 74) # green
                    border_color = (16, 185, 129) # green-500
                    
                # Card Background and left border
                pdf.set_fill_color(255, 255, 255)
                pdf.set_draw_color(226, 232, 240) # slate-200
                pdf.rect(10, start_y, 190, 52, "DF") # draw background card
                
                # Thick left border indicator
                pdf.set_fill_color(*border_color)
                pdf.rect(10, start_y, 2, 52, "F")
                
                pdf.set_y(start_y + 3)
                pdf.set_x(15)
                
                # Header of Card
                pdf.set_font("helvetica", "B", 10)
                pdf.set_text_color(26, 54, 93)
                pdf.cell(0, 5, f"Mapping Reference #{idx+1}", ln=1)
                
                pdf.set_x(15)
                pdf.set_font("helvetica", "B", 9)
                pdf.set_text_color(71, 85, 105)
                pdf.cell(40, 5, "Regulatory Clause:", ln=0)
                pdf.set_font("helvetica", "", 9)
                pdf.set_text_color(30, 41, 59)
                pdf.multi_cell(130, 5, clause, ln=1)
                
                pdf.set_x(15)
                pdf.set_font("helvetica", "B", 9)
                pdf.set_text_color(71, 85, 105)
                pdf.cell(40, 5, "Internal Policy Ref:", ln=0)
                pdf.set_font("helvetica", "", 9)
                pdf.set_text_color(30, 41, 59)
                pdf.multi_cell(130, 5, policy_ref, ln=1)
                
                pdf.set_x(15)
                pdf.set_font("helvetica", "B", 9)
                pdf.set_text_color(71, 85, 105)
                pdf.cell(40, 5, "Status:", ln=0)
                pdf.set_font("helvetica", "B", 9)
                pdf.set_text_color(*badge_fg)
                pdf.cell(0, 5, status.upper(), ln=1)
                
                pdf.set_x(15)
                pdf.set_font("helvetica", "B", 9)
                pdf.set_text_color(71, 85, 105)
                pdf.cell(40, 5, "Delta Evidence:", ln=0)
                pdf.set_font("helvetica", "I", 9)
                pdf.set_text_color(100, 116, 139)
                pdf.multi_cell(130, 4.5, delta, ln=1)
                
                pdf.ln(5)
                
        pdf.ln(10)
        
        # SECTION 3: TECHNICAL REMEDIATION BLUEPRINTS
        if pdf.get_y() > 220:
            pdf.add_page()
            
        pdf.set_font("helvetica", "B", 14)
        pdf.set_text_color(26, 54, 93) # Deep Navy
        pdf.cell(0, 8, "3. Technical Remediation Blueprints", ln=1, align="L")
        pdf.ln(2)
        
        blueprints = report.get("drift_remediation_blueprints", [])
        if not blueprints:
            pdf.set_font("helvetica", "I", 10)
            pdf.set_text_color(100, 116, 139)
            pdf.cell(0, 8, "No active gaps or remediation blueprints required.", ln=1)
        else:
            for idx, bp in enumerate(blueprints):
                clause = bp.get("clause_at_risk", "N/A")
                severity = bp.get("severity_rating", "LOW")
                clarity = bp.get("clarity_score", 100)
                blueprint_text = bp.get("technical_remediation_blueprint", "N/A")
                
                # Check page break
                if pdf.get_y() > 200:
                    pdf.add_page()
                    
                pdf.set_font("helvetica", "B", 11)
                pdf.set_text_color(30, 41, 59)
                pdf.cell(0, 6, f"3.{idx+1} Remediation: {clause}", ln=1)
                
                # Draw severity/clarity metrics
                pdf.set_font("helvetica", "B", 9)
                pdf.set_text_color(71, 85, 105)
                pdf.cell(30, 5, "Severity Rating:", ln=0)
                
                if severity in ["HIGH", "CRITICAL"]:
                    pdf.set_text_color(220, 38, 38)
                elif severity == "MEDIUM":
                    pdf.set_text_color(217, 119, 6)
                else:
                    pdf.set_text_color(22, 163, 74)
                    
                pdf.cell(40, 5, severity, ln=0)
                
                pdf.set_font("helvetica", "B", 9)
                pdf.set_text_color(71, 85, 105)
                pdf.cell(35, 5, "Regulatory Clarity:", ln=0)
                pdf.set_font("helvetica", "", 9)
                pdf.set_text_color(30, 41, 59)
                pdf.cell(0, 5, f"{clarity}/100", ln=1)
                
                pdf.ln(2)
                
                # Remediation Blueprint Box in Courier (monospace code block)
                pdf.set_font("courier", "", 9)
                pdf.set_text_color(30, 41, 59)
                
                pdf.set_fill_color(241, 245, 249) # slate-100 (light grey)
                pdf.set_x(15)
                pdf.multi_cell(180, 4.5, blueprint_text, ln=1, fill=True)
                
                pdf.ln(6)
                
        # Return PDF bytes cleanly
        return bytes(pdf.output())
