import streamlit as st
import dill

@st.cache_resource
def load_model():
    import boto3
    import cloudpickle
    # Fetch model from S3
    s3_client = boto3.client('s3')
    bucket_name = 'eligibot'
    key = 'model.pkl'
    # Download the model file into memory
    obj = s3_client.get_object(Bucket=bucket_name, Key=key)
    model = dill.loads(obj['Body'].read())
    return model



input_data = '''This study aims to explore the recommended phase 2 dose and evaluate the safety, tolerability and preliminary antitumor activity of BGB-16673 monotherapy at the recommended Phase 2 dose for the selected B-cell malignancy expansion cohorts
Conditions: B-cell Malignancy, Non-Hodgkin Lymphoma, Mantle Cell Lymphoma, Chronic Lymphocytic Leukemia/Small Lymphocytic Lymphoma, Waldenström Macroglobulinemia, Marginal Zone Lymphoma, Follicular Lymphoma, DLBCL Unclassifiable, Richter’s Transformation
Trial Arms:
1. Label: Phase 1a Monotherapy Dose Escalation
Type: EXPERIMENTAL
Description: BGB-16673 will be orally administered.
Interventionnames: Drug: BGB-16673
2. Label: Phase 1b Monotherapy Safety Expansion
Type: EXPERIMENTAL
Description: BGB-16673 will be orally administered.
Interventionnames: Drug: BGB-16673
3. Label: Phase 2 Monotherapy Dose Expansion
Type: EXPERIMENTAL
Description: BGB-16673 will be administered at the recommended Phase 2 dose (RP2D) that was identified in Part 1.
Interventionnames: Drug: BGB-16673
Trial Interventions:
1. Type: DRUG
Name: BGB-16673
Description: Orally administered
Armgrouplabels: Phase 1a Monotherapy Dose Escalation, Phase 1b Monotherapy Safety Expansion, Phase 2 Monotherapy Dose Expansion
Primary Outcomes:
1. Measure: Phase 1: Number of participants with adverse events (AEs) and serious adverse events (SAEs)
Description: Number of participants with AEs and SAEs as graded by the National Cancer Institute- Common Terminology Criteria for Adverse Events Version 5 (NCI CTCAE 5.0), including AEs that meet protocol-defined dose-limiting toxicity (DLT) criteria.
2. Measure: Phase 1: Recommended Phase 2 dose (RP2D) of BGB-16673
Description: As determined by the sponsor based on the Safety Monitoring Committee’s recommendation considering totality of the available clinical safety, clinical efficacy, pharmacokinetics, and pharmacodynamics data.
3. Measure: Phase 1a: Maximum tolerated dose (MTD) of BGB-16673
Description: The highest dose evaluated as recommended by the Bayesian Optimal Interval Design with Informative Prior (iBOIN) design or the maximum assessed dose (MAD).
4. Measure: Phase 2: Overall Response Rate (ORR) in participants with Relapsed/Refractory (R/R) Mantle Cell Lymphoma (MCL)
Description: ORR is defined as the percentage of participants with partial response or better according to the Independent Review Committee (IRC) assessment and as determined by Lugano criteria.
5. Measure: Phase 2: ORR in participants with R/R Chronic Lymphocytic Leukemia/Small Lymphocytic Lymphoma (CLL/SLL)
Description: ORR is defined as the percentage of participants with partial response or better as assessed by the IRC and determined by the International Workshop on Chronic Lymphocytic Leukemia (iwCLL) criteria.
Key Inclusion Criteria
1. Provision of signed and dated written informed consent prior to any study
2. Eastern Cooperative Oncology Group (ECOG) Performance Status of 0 to 2
3. Adequate organ function of coagulation function, liver function, renal function and pancreatic function and measure disease per disease-specific response criteria
4. Phase 1: Confirmed diagnosis of R/R Marginal Zone Lymphoma (MZL), Follicular Lymphoma (grade 1-3a), Waldenström Macroglobulinemia (WM), non-germinal center B-cell (non-GCB) diffuse large B-cell lymphoma (DLBCL), Richter’s transformation to DLBCL, MCL, or CLL/SLL
5. Phase 2: Confirmed diagnosis of MCL, or CLL/SLL
6. Highly effective method of birth control during study treatment period, and for at least 90 days after the last dose of the study drug
Key Exclusion Criteria
1. Prior malignancy (other than the disease under study) within the past 2 years, except for curatively treated basal or squamous skin cancer, superficial bladder cancer, carcinoma in situ of the cervix or breast, or localized Gleason score ≤ 6 prostate cancer
2. Require ongoing systemic treatment for any other malignancy or systemic corticosteroid treatment
3. Receiving treatment with a strong CYP3A inhibitor or inducer ≤ 14 days before the first dose of BGB-16673, or proton-pump inhibitors ≤ 5 days before the first dose of BGB-16673.
4. Current or history of central nervous involvement
5. Prior autologous stem cell transplant unless ≥ 3 months after transplant, prior chimeric cell therapy unless ≥ 6 months after cell infusion, prior allogeneic stem cell transplant ≤ 6 months before the first dose of the study drug
Note: Other protocol defined Inclusion/Exclusion criteria may apply
Sex: ALL
Minimum Age: 18 Years'''

if st.button("Predict"):
    model = load_model()
    prediction = model.predict([input_data])
    st.success(f"Prediction: {prediction[0]}")