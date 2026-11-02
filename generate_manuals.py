import os
import pymupdf

os.makedirs('data/Manuals', exist_ok=True)

def create_pdf(filepath, pages_data):
    doc = pymupdf.open()
    rect = pymupdf.Rect(50, 50, 545, 792)
    for title, text in pages_data:
        page = doc.new_page(width=595, height=842)
        full_text = f"{title}\n\n{text}"
        page.insert_textbox(rect, full_text, fontsize=10.5, fontname="helv")
    doc.save(filepath)
    doc.close()
    print(f"Generated: {filepath}")

# 1. HP200 Operations Manual
hp_ops_pages = [
    (
        "HP-200 OPERATIONS MANUAL\nDocument ID: HP-OPS-01 | Revision: 1.0 | Page 1 of 3",
        """1. EQUIPMENT IDENTITY AND PURPOSE
Machine ID: M-HP200
Model: HP-200
Description: Hydraulic forming press.
The HP-200 is a hydraulic forming press engineered for precision component forming under high hydraulic pressure.
Operating fluid: H46 hydraulic oil.

2. OPERATING REFERENCE VALUES
- Normal hydraulic pressure: 120 to 140 bar during the forming stage.
- Ready oil temperature: 35°C to 55°C (required temperature range for readiness).
- High-temperature warning threshold: Above 60°C.
- High-temperature stop threshold: 65°C or higher (immediate cycle cutoff).
- Reservoir oil level: Must remain between marked MIN and MAX level indicators.
- Low-pressure trigger threshold: Below 110 bar for more than 5 seconds during forming stage.

3. MACHINE OPERATING STATES
- OFF: Machine is completely powered down.
- READY: Starting preconditions are met (guard-closed indicator active, reservoir oil level between MIN and MAX, oil temperature between 35°C and 55°C). Note: A normal pressure reading in READY does not prove that pressure will remain normal during FORMING.
- FORMING: Machine actively delivers hydraulic tonnage to form parts.
- HOLD: Cycle paused or inhibited due to fault condition, awaiting review.

4. DIAGNOSTIC PRINCIPLES
A pressure reading alone cannot identify which individual component has failed. Low pressure does not automatically indicate that the hydraulic pump is damaged or worn."""
    ),
    (
        "HP-200 OPERATIONS MANUAL\nDocument ID: HP-OPS-01 | Revision: 1.0 | Page 2 of 3",
        """1. OPERATOR PRE-CYCLE REVIEW
Prior to initiating a forming cycle, the operator must verify:
- Machine ID display and machine state indication (must show READY).
- Guard-closed safety indicator. Never bypass safety interlocks under any circumstances.
- Reservoir sight-glass oil level (between MIN and MAX).
- Oil temperature indication (must be in ready range: 35°C to 55°C).
If any indication is abnormal, hold the cycle and report immediately.

2. ALARM CODES REFERENCE
- E17: Low hydraulic pressure. Triggered when pressure drops below 110 bar for more than 5 seconds during FORMING. Normal forming pressure is 120-140 bar. Required response: Record hydraulic pressure and current cycle stage; place machine on HOLD; request inspection checks. Note: E17 does not prove the pump has failed.
- E24: High oil temperature warning. Warning triggered above 60°C; automatic stop occurs at 65°C or above. (For example, at 62°C, temperature is in warning range: machine must be placed on HOLD and cooling-system inspection requested).
- E31: Guard-open indication. Safety interlock triggered. Cycle inhibited. Never bypass interlocks.
- E42: Return-filter restriction. Restriction detected in hydraulic return filter (RF-20). Operator must record indicator status and request filter inspection.

3. TEMPERATURE BEHAVIOR RULES
- 35°C to 55°C: Within normal ready range.
- Above 60°C: Warning condition.
- 65°C or higher: High-temperature stop.
Note: The manual does not specify a guaranteed cooldown duration."""
    ),
    (
        "HP-200 OPERATIONS MANUAL\nDocument ID: HP-OPS-01 | Revision: 1.0 | Page 3 of 3",
        """1. FAULT REPORTING REQUIREMENTS
When reporting an HP-200 operational fault or alarm, record:
- Machine ID (M-HP200), date, and exact timestamp.
- Active alarm code (e.g., E17, E24, E31, E42).
- Displayed hydraulic pressure and oil temperature.
- Active cycle stage and reservoir oil level.
- Visible external leakage observations.
- Whether the condition has previously occurred.

2. REPEATED FAULT ESCALATION
If low hydraulic pressure (E17) occurs repeatedly after documented checks have been reviewed:
- Maintain machine on HOLD.
- Escalate issue to authorized maintenance, referencing prior incident records.
- Warning: Never adjust or increase the hydraulic pressure setting just to suppress an alarm.

3. ROLES AND RESPONSIBILITIES
- Operator: Observes and records symptoms, active alarms, and operating parameters.
- Authorized Maintenance: Evaluates technical symptoms and conducts physical inspections.
- Designated Supervisor: Reviews maintenance findings and records the official return-to-service decision.

4. EXCLUDED INFORMATION / GUIDANCE LIMITS
The HP-200 manuals do not provide:
- Hydraulic pump replacement prices or spare parts costs.
- Component supplier contacts.
- Fastener tightening torques.
- Electrical wiring diagrams or internal hydraulic schematics.
- Internal component rebuild procedures.
- Pressure regulator modification steps.
- Guaranteed cycle times or service contract coverage."""
    )
]

# 2. HP200 Maintenance Manual
hp_mnt_pages = [
    (
        "HP-200 MAINTENANCE MANUAL\nDocument ID: HP-MNT-01 | Revision: 1.0 | Page 1 of 3",
        """1. MAINTENANCE REFERENCE DATA
- Equipment Model: HP-200 Forming Press (Machine ID: M-HP200).
- Hydraulic fluid specification: H46 hydraulic oil.
- Return-filter identifier: RF-20.
- Reservoir capacity & level: Maintain between MIN and MAX markings on sight-glass.
- Planned oil replacement interval: Every 2,000 operating hours or 12 months, whichever comes first.

2. INSPECTION BOUNDARIES & SAFETY PRECAUTIONS
Physical maintenance tasks must only be performed by authorized maintenance personnel.
All work must strictly adhere to facility isolation and stored-energy control procedures.
Safety Notice: The manual does not provide site isolation procedures. Personnel must never open pressurized hydraulic lines, remove protective safety guards, or alter internal machine valve settings.

3. RECORDING COMPLETED MAINTENANCE WORK
Whenever maintenance or inspection is completed, the technician must record:
- Machine ID (M-HP200).
- Current operating-hour reading.
- Date of inspection/service.
- Specific inspection item or component serviced.
- Physical observation and measured parameters.
- Action reference code.
- Authorized reviewer signature.
Important: An AI-generated suggestion or diagnostic note does not constitute completed maintenance."""
    ),
    (
        "HP-200 MAINTENANCE MANUAL\nDocument ID: HP-MNT-01 | Revision: 1.0 | Page 2 of 3",
        """1. SCHEDULED INSPECTION INTERVALS
- Before each shift: Inspect reservoir level and check for visible external leakage via sight-glass. Record oil level and leakage findings.
- Every 50 operating hours: Inspect the RF-20 return-filter restriction indicator. Record indicator status.
- Every 250 operating hours: Inspect cooling-air path and external hydraulic hoses for obstructions, physical damage, or leakage.
- Every 500 operating hours: Planned replacement of the RF-20 return filter. (Note: Earlier replacement is required if filter restriction is confirmed).
- Every 2,000 operating hours or 12 months: Planned replacement of H46 hydraulic oil (whichever limit is reached first).

2. RETURN FILTER (RF-20) & ALARM E42 REFERENCE
- E42 indicates restriction in the RF-20 hydraulic return filter on HP-200.
- Maintenance technicians must review the restriction indicator and previous service records.
- If restriction is confirmed, execute an authorized filter replacement.
- Note: The maintenance manual does not specify a calendar-based replacement interval for the RF-20 filter (only the 500 operating hours interval or condition-based replacement)."""
    ),
    (
        "HP-200 MAINTENANCE MANUAL\nDocument ID: HP-MNT-01 | Revision: 1.0 | Page 3 of 3",
        """1. LOW HYDRAULIC PRESSURE (E17) TROUBLESHOOTING OBSERVATIONS
When investigating alarm E17 on the HP-200, collect observations in the following mandatory order:
1. Reservoir level: Verify whether hydraulic fluid is between MIN and MAX markings.
2. Visible leakage: Inspect fittings, hoses, and manifolds for external leakage.
3. RF-20 restriction indicator: Verify whether the return-filter restriction indicator is tripped.
4. Oil temperature and recorded pressure during the forming stage (compare against normal 120-140 bar).
Important Diagnostic Note: Low oil level, leakage, or return-filter restriction are diagnostic observations; they do not individually prove the root cause. The manuals do not provide a diagnostic test that conclusively proves hydraulic pump failure. If E17 low pressure repeats, keep machine on HOLD and escalate.

2. HIGH OIL TEMPERATURE (E24) TROUBLESHOOTING
When investigating alarm E24, inspect:
- Cooling-air path: Check for dust accumulation, physical debris, or airflow obstruction.
- Cooling-fan status indication.
- Reservoir oil level.
- Recent machine operating cycle patterns.
Note: The manual does not provide cooling-fan replacement instructions or guaranteed cooldown times.

3. ESCALATION RECORD REQUIREMENTS
Escalation reports to authorized engineering must contain:
Machine ID, timestamp, operating hours, alarm code, pressure, oil temperature, reservoir level, leakage observations, RF-20 filter indicator state, cooling-fan indication, prior incident reference ID, and reviewing technician.

4. RETURN-TO-SERVICE AUTHORIZATION
Return-to-service can ONLY be authorized by the designated supervisor following technical maintenance review. The AI assistant cannot authorize machine restart, nor does alarm clearance alone permit restarting."""
    )
]

# 3. AC90 Operations and Maintenance Manual
ac_om_pages = [
    (
        "AC-90 OPERATIONS AND MAINTENANCE MANUAL\nDocument ID: AC-OM-01 | Revision: 1.0 | Page 1 of 3",
        """1. EQUIPMENT IDENTITY AND PURPOSE
Machine ID: M-AC90
Model: AC-90
Description: Industrial rotary screw air compressor.
The AC-90 is an industrial air compressor designed to provide steady pressurized plant air to production tooling.
Lubricant specification: AC-L32 compressor lubricant (Note: Never use H46 hydraulic oil in this equipment).

2. OPERATING REFERENCE VALUES
- Normal outlet pressure: 7.0 to 8.0 bar under steady demand in LOADED state.
- Low-pressure warning threshold: Below 6.5 bar for more than 10 seconds.
- Normal discharge temperature: 70°C to 90°C.
- High-temperature warning threshold: Above 95°C.
- High-temperature stop threshold: 105°C or higher (thermal trip).
- Lubricant level: Must remain between marked LOW and HIGH level sight indicators.

3. MACHINE OPERATING STATES
- READY: Preconditions satisfied, standby mode awaiting air demand.
- LOADED: Compressor actively delivering compressed air under system demand.
- HOLD: Operation interrupted or locked out for inspection.
Note: The normal outlet pressure of 7.0-8.0 bar applies specifically under steady demand in the LOADED state. A temporary transient pressure dip does not constitute an alarm condition."""
    ),
    (
        "AC-90 OPERATIONS AND MAINTENANCE MANUAL\nDocument ID: AC-OM-01 | Revision: 1.0 | Page 2 of 3",
        """1. ALARM CODES REFERENCE & DIAGNOSTIC LIMITS
- E17: High discharge temperature. On AC-90, E17 indicates discharge air temperature exceeding limits. (Normal: 70-90°C; Warning: Above 95°C; Stop: 105°C or higher). Required response: Record discharge temperature; place machine on HOLD if above 95°C; request cooling-air path review.
CRITICAL DISTINCTION: On AC-90, E17 means high discharge temperature. On HP-200, E17 means low hydraulic pressure. Never mix these machine models.
- E08: Low outlet pressure. Triggered when outlet pressure remains below 6.5 bar for more than 10 seconds under steady demand. Required response: Record pressure, duration, demand state, and check for audible/visible air leakage; inspect AF-10 inlet-filter restriction indicator. Note: E08 does not prove that the compressor airend element is worn.
- E31: Condensate-drain fault. Indicates automatic condensate-drain failure. (Contrast: On HP-200, E31 is guard-open). Required response: Record fault and request authorized drain inspection.
- E42: Inlet-filter restriction. Indicates restriction in the AF-10 compressor air inlet filter. Required action: Record indicator and review AF-10 service history.

2. TEMPERATURE RESPONSE EXAMPLES
If discharge temperature reaches 98°C:
- 98°C is above the 95°C warning threshold, but below the 105°C shutdown stop threshold.
- The compressor must remain on HOLD and the cooling air path must be inspected."""
    ),
    (
        "AC-90 OPERATIONS AND MAINTENANCE MANUAL\nDocument ID: AC-OM-01 | Revision: 1.0 | Page 3 of 3",
        """1. SCHEDULED MAINTENANCE INTERVALS
- Before each shift: Check AC-L32 lubricant level (between LOW and HIGH) and verify condensate-drain status.
- Every 100 operating hours: Inspect the AF-10 air inlet-filter restriction indicator. Record state.
- Every 400 operating hours: Inspect external cooling-air path for blockages and cleanliness.
- Every 600 operating hours: Planned replacement of AF-10 inlet filter. (Earlier replacement required if restriction confirmed).
- Every 3,000 operating hours or 12 months: Planned replacement of AC-L32 compressor lubricant (whichever occurs first).

2. INSPECTION VERSUS REPLACEMENT RULES
- For AF-10 inlet filter: Restriction indicator must be inspected every 100 operating hours. Planned replacement is scheduled every 600 operating hours.
- Note: The manual does not provide a calendar-based replacement interval for the AF-10 filter.

3. ESCALATION & RETURN-TO-SERVICE REQUIREMENTS
When an AC-90 abnormal condition occurs, record: Machine ID (M-AC90), timestamp, operating hours, active alarm, outlet pressure, discharge temperature, air demand state, lubricant sight-glass level, AF-10 filter indicator, and condensate-drain condition.
Physical maintenance requires authorized personnel using site pressure-release and isolation procedures (not contained in manual).
Return-to-service authorization: The designated supervisor alone records the return-to-service decision.

4. EXCLUDED INFORMATION
The manual does not provide: maintenance costs, spare parts pricing, supplier contacts, electrical schematics, bolt torque ratings, motor rewinding specifications, compressor element overhaul steps, expected remaining service life, or guaranteed repair times."""
    )
]

create_pdf('data/Manuals/HP200_Operations_Rev1_0.pdf', hp_ops_pages)
create_pdf('data/Manuals/HP200_Maintenance_Rev1_0.pdf', hp_mnt_pages)
create_pdf('data/Manuals/AC90_Operations_Maintenance_Rev1_0.pdf', ac_om_pages)

# Create machine_manual_index.csv
csv_content = """machine_id,model,machine_name,document_id,revision,pdf_filename
M-HP200,HP-200,Hydraulic forming press,HP-OPS-01,1.0,HP200_Operations_Rev1_0.pdf
M-HP200,HP-200,Hydraulic forming press,HP-MNT-01,1.0,HP200_Maintenance_Rev1_0.pdf
M-AC90,AC-90,Air compressor,AC-OM-01,1.0,AC90_Operations_Maintenance_Rev1_0.pdf
"""
with open('data/machine_manual_index.csv', 'w', encoding='utf-8') as f:
    f.write(csv_content)
print("Created data/machine_manual_index.csv")

# Create START_HERE.txt
start_here_content = """Round 1 Student Pack - Instructions & Rules

1. Read the challenge PDF first.
2. Use the CSV file (machine_manual_index.csv) to register machines and manuals.
3. Upload and index only the three PDFs inside Manuals/:
   - HP200_Operations_Rev1_0.pdf (HP-OPS-01, Rev 1.0)
   - HP200_Maintenance_Rev1_0.pdf (HP-MNT-01, Rev 1.0)
   - AC90_Operations_Maintenance_Rev1_0.pdf (AC-OM-01, Rev 1.0)
4. Each PDF has three pages. Page numbering starts at 1.
5. HP-200 has two manuals. Both are valid and must work together.
6. All machines and specifications are fictional training material.
7. AI model access and college rules are provided separately.
8. Development and evaluation have fixed timings.

CRITICAL RULE:
You must not use the challenge brief, START_HERE.txt or CSV as sources of machine maintenance answers.
Only the three PDF manuals are knowledge sources.
"""
with open('data/START_HERE.txt', 'w', encoding='utf-8') as f:
    f.write(start_here_content)
print("Created data/START_HERE.txt")

