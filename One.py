import streamlit as st

st.set_page_config(page_title="One", layout="centered", initial_sidebar_state="expanded")

st.title("Weird Localizer & N Calculator")

# --- Chief Complaint Text Input ---
st.header("Chief Complaint")
chief_complaint = st.text_input("e.g., 'weakness', 'dysarthria', 'numbness'", "").strip()

# Symptom checklist
st.header("Symptoms")

symptoms = st.multiselect("Choose symptom(s):", [
    "Right hemiparesis (Upper & Lower equally)",   # Subcortical
    "Right hemiparesis (Upper> Lower)",              # Cortical (e.g., MCA territory)
    "Right hemiparesis (Lower> Upper)",              # Cortical (e.g., ACA territory)
    "Left hemiparesis (Upper & Lower equally)",   # Subcortical
    "Left hemiparesis (Upper> Lower)",               # Cortical (e.g., MCA territory)
    "Left hemiparesis (Lower> Upper)",               # Cortical (e.g., ACA territory)
    "Aphasia",
    "Neglect",
    "Facial palsy (Upper & Lower face equally affected)", # LMN or brainstem (e.g., CN VII nucleus)
    "Facial palsy (Lower face only affected)",           # UMN (cortical or corticobulbar tract)
    "Vertigo",
    "Dysarthria",
    "Partial seizure",       
    "Generalized seizure",   
    "Emotional disturbances", 
    "Vision loss (Homonymous Hemianopia)",
    "Vision loss (Unilateral - optic nerve related)",
    "Ataxia (Limb)",
    "Ataxia (Truncal)",
    "Sensory loss (Hemibody, all modalities)",
    "Sensory loss (Dissociated - e.g., pain/temp affected, light touch spared)", # Brainstem/spinal cord
    "Tongue deviation",
    "Horner’s syndrome",
    "Gaze palsy (Conjugate, toward lesion)",
    "Gaze palsy (Conjugate, away from lesion)",
    "Gaze palsy (Internuclear Ophthalmoplegia - INO)" # Specific brainstem lesion
])

# Determine if NIHSS should be used
nihss_keywords = ["stroke", "tia", "cva", "ischemia", "hemorrhage", "infarct", "weakness", "numbness", "mute", "stuporous", "palsy", "dysarthria", "hemiparesis", "aoc", "alteration", "weak", "numb", "passing out", "seizure", "aphasia", "neglect", "vertigo", "ataxia", "sensory loss", "gaze palsy"]

use_nihss_from_symptoms = any(any(keyword in s.lower() for keyword in nihss_keywords) for s in symptoms)
use_nihss_from_chief_complaint = False
if chief_complaint:
    for keyword in nihss_keywords:
        if keyword in chief_complaint.lower():
            use_nihss_from_chief_complaint = True
            break
use_nihss = use_nihss_from_symptoms or use_nihss_from_chief_complaint


# --- Advanced Lesion Localization Logic ---
st.header("Likely Lesion Locations")

lesion_locations = set() # Use a set to store unique locations
ambiguity_notes = [] # To store notes about ambiguous data
suggest_imaging = False # Flag to suggest imaging

# Rule 1: Hemiparesis Patterns
# Right side weakness -> Left Hemisphere
if "Right hemiparesis (Upper & Lower equally)" in symptoms:
    lesion_locations.add("Left internal capsule (Subcortical)")
    lesion_locations.add("Left Thalamus (if sensory also affected)")
    affected_vessels.add("Left Lenticulostriate arteries (MCA deep branches) or Thalamoperforating arteries (PCA deep branches)")
    suggest_imaging = True
elif "Right hemiparesis (Upper> Lower)" in symptoms:
    lesion_locations.add("Left motor cortex (Middle Cerebral Artery territory)")
    affected_vessels.add("Left Middle Cerebral Artery (MCA) - Superior Division")
    suggest_imaging = True
elif "Right hemiparesis (Lower> Upper)" in symptoms:
    lesion_locations.add("Left motor cortex (Anterior Cerebral Artery territory)")
    affected_vessels.add("Left Anterior Cerebral Artery (ACA)")
    suggest_imaging = True

# Left side weakness -> Right Hemisphere
if "Left hemiparesis (Upper & Lower equally)" in symptoms:
    lesion_locations.add("Right internal capsule (Subcortical)")
    lesion_locations.add("Right Thalamus (if sensory also affected)")
    affected_vessels.add("Right Lenticulostriate arteries (MCA deep branches) or Thalamoperforating arteries (PCA deep branches)")
    suggest_imaging = True
elif "Left hemiparesis (Upper> Lower)" in symptoms:
    lesion_locations.add("Right motor cortex (Middle Cerebral Artery territory)")
    affected_vessels.add("Right Middle Cerebral Artery (MCA) - Superior Division")
    suggest_imaging = True
elif "Left hemiparesis (Lower> Upper)" in symptoms:
    lesion_locations.add("Right motor cortex (Anterior Cerebral Artery territory)")
    affected_vessels.add("Right Anterior Cerebral Artery (ACA)")
    suggest_imaging = True

# Rule 2: Aphasia
if "Aphasia" in symptoms:
    lesion_locations.add("Left frontal lobe (Broca's area) - Expressive Aphasia")
    lesion_locations.add("Left temporal lobe (Wernicke's area) - Receptive Aphasia")
    lesion_locations.add("Left parietal lobe (Conduction Aphasia)")
    affected_vessels.add("Left Middle Cerebral Artery (MCA) - Superior or Inferior Division (depending on type)")
    suggest_imaging = True # Aphasia often warrants imaging

# Rule 3: Neglect
if "Neglect" in symptoms:
    lesion_locations.add("Right parietal lobe")
    lesion_locations.add("Right frontal lobe")
    lesion_locations.add("Right thalamus")
    lesion_locations.add("Right subcortical white matter")
    affected_vessels.add("Right Middle Cerebral Artery (MCA) - Inferior Division")
    suggest_imaging = True

# Rule 4: Facial Palsy
# Combine check for general hemiparesis for side-specific UMN facial palsy
any_right_hemiparesis = any("Right hemiparesis" in s for s in symptoms)
any_left_hemiparesis = any("Left hemiparesis" in s for s in symptoms)

if "Facial palsy (Upper & Lower face equally affected)" in symptoms:
    lesion_locations.add("Ipsilateral Pons (Facial nerve nucleus or exiting fascicles)")
    lesion_locations.add("Ipsilateral Facial Nerve (Peripheral palsy)")
    affected_vessels.add("Basilar Artery branches (e.g., AICA, pontine arteries) or External Carotid Artery branches (for peripheral facial nerve supply)")
    ambiguity_notes.append("For upper & lower face palsy, consider Bell's palsy (peripheral) vs. brainstem stroke/lesion.")
    suggest_imaging = True if use_nihss else suggest_imaging # If stroke suspected, image

elif "Facial palsy (Lower face only affected)" in symptoms:
    if any_right_hemiparesis:
        lesion_locations.add("Left precentral gyrus (Lower face motor cortex)")
        lesion_locations.add("Left internal capsule (Corticobulbar tract)")
        affected_vessels.add("Left Middle Cerebral Artery (MCA) - Superior Division (cortical) or Lenticulostriate arteries (subcortical)")
    elif any_left_hemiparesis:
        lesion_locations.add("Right precentral gyrus (Lower face motor cortex)")
        lesion_locations.add("Right internal capsule (Corticobulbar tract)")
        affected_vessels.add("Right Middle Cerebral Artery (MCA) - Superior Division (cortical) or Lenticulostriate arteries (subcortical)")
    else: # If UMN facial palsy without clear hemiparesis
        lesion_locations.add("Contralateral motor cortex or corticobulbar tract")
        affected_vessels.add("Contralateral Middle Cerebral Artery (MCA) branches or Lenticulostriate arteries")
        ambiguity_notes.append("Lower face palsy without hemiparesis might suggest a focal cortical lesion or lacunar infarct.")
    suggest_imaging = True

# Rule 5: Vertigo and Ataxia (Brainstem/Cerebellum)
if "Vertigo" in symptoms:
    lesion_locations.add("Cerebellum (Vestibulocerebellum)")
    lesion_locations.add("Brainstem (Vestibular nuclei - e.g., lateral medulla for Wallenberg's)")
    affected_vessels.add("Posterior Inferior Cerebellar Artery (PICA) for lateral medulla (Wallenberg's)")
    affected_vessels.add("Anterior Inferior Cerebellar Artery (AICA) or Superior Cerebellar Artery (SCA) for cerebellum/pons")
    ambiguity_notes.append("Vertigo can be peripheral (inner ear) or central (brainstem/cerebellum). Consider other brainstem signs for central origin.")
    suggest_imaging = True if "Brainstem" in str(lesion_locations) or use_nihss else suggest_imaging
if "Ataxia (Limb)" in symptoms:
    lesion_locations.add("Ipsilateral Cerebellar hemisphere")
    lesion_locations.add("Cerebellar peduncles")
    lesion_locations.add("Brainstem (Pons/Medulla - input/output to cerebellum)")
    affected_vessels.add("Superior Cerebellar Artery (SCA), AICA, or PICA depending on cerebellar/brainstem location")
    suggest_imaging = True
if "Ataxia (Truncal)" in symptoms:
    lesion_locations.add("Cerebellar vermis")
    affected_vessels.add("Superior Cerebellar Artery (SCA) or PICA (inferior vermis)")
    ambiguity_notes.append("Truncal ataxia is highly suggestive of cerebellar vermis involvement, often associated with gait instability.")
    suggest_imaging = True

# Rule 6: Dysarthria (Multiple locations)
if "Dysarthria" in symptoms:
    lesion_locations.add("Pons (Corticobulbar tracts, lower cranial nerves)")
    lesion_locations.add("Cerebellum")
    lesion_locations.add("Internal capsule")
    lesion_locations.add("Motor cortex (Bilateral lesions)")
    affected_vessels.add("Basilar Artery branches (pontine arteries), Lenticulostriate arteries, ACA/MCA/PCA branches, non-specific")
    ambiguity_notes.append("Dysarthria is a non-localizing sign alone, but in combination with other deficits, it helps pinpoint the lesion.")
    suggest_imaging = True if use_nihss else suggest_imaging

# Rule 7: Seizure (Cortical/Generalized)
if "Partial seizure" in symptoms:
    lesion_locations.add("Focal cortical lesion (e.g., Frontal, Temporal, Parietal, Occipital lobe)")
    ambiguity_notes.append("Partial seizures require localization of the seizure focus. Imaging is crucial.")
    suggest_imaging = True
if "Generalized seizure" in symptoms:
    lesion_locations.add("Diffuse cortical dysfunction")
    ambiguity_notes.append("Generalized seizures often don't have a single focal lesion on imaging but can be associated with metabolic, toxic, or genetic causes. Imaging may still useful to rule out structural causes.")
    suggest_imaging = True # Still good practice to image

# Rule 8: Emotional Disturbances (Non-specific, but can be localized)
if "Emotional disturbances" in symptoms:
    lesion_locations.add("Frontal lobe (Orbitofrontal, medial prefrontal cortex)")
    lesion_locations.add("Temporal lobe (Amygdala, hippocampus)")
    lesion_locations.add("Limbic system structures")
    affected_vessels.add("Anterior Cerebral Artery (ACA) branches (for frontal lobe), Middle Cerebral Artery (MCA) branches (for temporal lobe)")
    ambiguity_notes.append("Emotional disturbances are highly non-specific and can result from various neurological or psychiatric conditions. Lesion localization is challenging without other signs.")
    suggest_imaging = True if use_nihss else suggest_imaging 

# Rule 9: Vision Loss
if "Vision loss (Homonymous Hemianopia)" in symptoms:
    st.info("For Homonymous Hemianopia, consider the contralateral lesion. E.g., Left HH -> Right Occipital/Optic Radiation.")
    lesion_locations.add("Contralateral Occipital lobe (Visual cortex)")
    lesion_locations.add("Contralateral Optic radiation (Parietal or Temporal lobe)")
    lesion_locations.add("Contralateral Thalamus (Lateral Geniculate Nucleus)")
    affected_vessels.add("Contralateral Posterior Cerebral Artery (PCA) - Calcarine branch (for occipital cortex)")
    affected_vessels.add("Contralateral Middle Cerebral Artery (MCA) - deep branches (for optic radiations in temporal lobe)")
    suggest_imaging = True
elif "Vision loss (Unilateral, optic nerve related)" in symptoms:
    lesion_locations.add("Ipsilateral Optic nerve")
    lesion_locations.add("Optic Chiasm")
    affected_vessels.add("Ophthalmic Artery (branch of Internal Carotid Artery) for optic nerve")
    affected_vessels.add("Anterior Cerebral Artery (ACA) branches for optic chiasm")
    ambiguity_notes.append("Unilateral vision loss can also be ocular in origin. Neurological causes usually involve optic nerve or chiasm.")
    suggest_imaging = True

# Rule 10: Sensory Loss
if "Sensory loss (Hemibody, all modalities)" in symptoms:
    lesion_locations.add("Contralateral Parietal lobe (Somatosensory cortex)")
    lesion_locations.add("Contralateral Thalamus (VPL/VPM nucleus)")
    lesion_locations.add("Contralateral Internal capsule (Sensory tracts)")
    affected_vessels.add("Contralateral Middle Cerebral Artery (MCA) - Parietal branches")
    affected_vessels.add("Contralateral Thalamoperforating arteries (from PCA)")
    affected_vessels.add("Contralateral Lenticulostriate arteries (from MCA) or Anterior Choroidal Artery (from ICA)")
    suggest_imaging = True
elif "Sensory loss (Dissociated - e.g., pain/temp affected, light touch spared)" in symptoms:
    lesion_locations.add("Brainstem (Lateral Medulla for Wallenberg's syndrome - ipsilateral face/contralateral body pain/temp)")
    lesion_locations.add("Spinal Cord (Syringomyelia, Brown-Séquard - level dependent)")
    affected_vessels.add("Posterior Inferior Cerebellar Artery (PICA) for lateral medulla")
    affected_vessels.add("Spinal Arteries (Anterior or Posterior Spinal Arteries) for spinal cord")
    ambiguity_notes.append("Dissociated sensory loss strongly suggests a brainstem or spinal cord lesion.")
    suggest_imaging = True

# Rule 11: Tongue Deviation
if "Tongue deviation" in symptoms:
    lesion_locations.add("Ipsilateral Medulla (Hypoglossal nucleus - CN XII)")
    lesion_locations.add("Ipsilateral Hypoglossal Nerve (Peripheral)")
    suggest_imaging = True if use_nihss else suggest_imaging

# Rule 12: Horner’s syndrome
if "Horner’s syndrome" in symptoms:
    lesion_locations.add("Ipsilateral Lateral Medulla (Wallenberg's syndrome)")
    lesion_locations.add("Ipsilateral Pons")
    lesion_locations.add("Hypothalamospinal tract (anywhere from hypothalamus down to T1)")
    lesion_locations.add("Carotid Artery dissection (sympathetic chain involvement)")
    affected_vessels.add("Posterior Inferior Cerebellar Artery (PICA) for lateral medulla")
    affected_vessels.add("Basilar Artery branches (pontine arteries) for pons")
    affected_vessels.add("Carotid Artery (for dissection)")
    ambiguity_notes.append("Horner's syndrome requires careful evaluation for the level of sympathetic chain involvement (central, preganglionic, postganglionic).")
    suggest_imaging = True

# Rule 13: Gaze Palsy
if "Gaze palsy (Conjugate, toward lesion)" in symptoms:
    lesion_locations.add("Ipsilateral Frontal eye field")
    lesion_locations.add("Ipsilateral Pontine gaze center (PPRF)")
    affected_vessels.add("Middle Cerebral Artery (MCA) - Superior Division (frontal eye field)")
    affected_vessels.add("Basilar Artery branches (pontine arteries) for PPRF")
    suggest_imaging = True
elif "Gaze palsy (Conjugate, away from lesion)" in symptoms:
    lesion_locations.add("Contralateral Frontal eye field (Irritative lesion)")
    suggest_locations.add("Basal Ganglia/Thalamus (less common for conjugate deviation)")
    affected_vessels.add("Contralateral Middle Cerebral Artery (MCA) - Superior Division")
    affected_vessels.add("Lenticulostriate arteries (from MCA) or Thalamoperforating arteries (from PCA)")
    suggest_imaging = True
elif "Gaze palsy (Internuclear Ophthalmoplegia - INO)" in symptoms:
    lesion_locations.add("Medial Longitudinal Fasciculus (MLF) in Brainstem (usually Pons)")
    affected_vessels.add("Basilar Artery branches (pontine arteries, e.g., paramedian branches)")
    suggest_imaging = True


# --- Combine for Vascular Territory Analysis (New Section) ---
st.header("Step 4: Affected Vascular Territory Analysis") # Added Step 4
vascular_analysis = set()

# Special combined rules for common stroke syndromes
# Example: Right hemiparesis (Arm > Leg) + Aphasia -> Left MCA superior division
if "Right hemiparesis (Upper> Lower)" in symptoms and "Aphasia" in symptoms:
    vascular_analysis.add("Left Middle Cerebral Artery (MCA) - Superior Division (classic for Broca's aphasia and right arm/face weakness)")
    lesion_locations.add("Left Frontal and Parietal Lobes") # Reinforce specific lobes
    suggest_imaging = True
elif "Left hemiparesis (Upper> Lower)" in symptoms and "Neglect" in symptoms:
    vascular_analysis.add("Right Middle Cerebral Artery (MCA) - Inferior Division (classic for neglect and left arm/face weakness)")
    lesion_locations.add("Right Parietal and Temporal Lobes") # Reinforce specific lobes
    suggest_imaging = True
elif "Homonymous Hemianopia" in symptoms and "Aphasia" in symptoms:
    vascular_analysis.add("Left Middle Cerebral Artery (MCA) - complete occlusion or Posterior Cerebral Artery (PCA) - with cortical aphasia")
    ambiguity_notes.append("Homonymous hemianopia with aphasia might suggest a large MCA stroke affecting visual pathways or a complex PCA stroke.")
    suggest_imaging = True
elif "Vertigo" in symptoms and "Dysarthria" in symptoms and "Ipsilateral Facial palsy (Upper & Lower face equally affected)" in symptoms and "Contralateral sensory loss" in symptoms:
    vascular_analysis.add("Vertebrobasilar System - Posterior Inferior Cerebellar Artery (PICA) - for Lateral Medullary (Wallenberg's) Syndrome")
    lesion_locations.add("Ipsilateral Lateral Medulla")
    suggest_imaging = True
elif "Right hemiparesis (Upper & Lower equally)" in symptoms and "Right Facial palsy (Lower face only affected)" in symptoms and "Right sensory loss (Hemibody, all modalities)" in symptoms:
    vascular_analysis.add("Left Lenticulostriate arteries (deep branches of MCA) - for Lacunar Syndrome (Pure Motor or Sensorimotor Stroke)")
    lesion_locations.add("Left Internal Capsule or Basal Ganglia")
    suggest_imaging = True
elif "Left hemiparesis (Upper & Lower equally)" in symptoms and "Left Facial palsy (Lower face only affected)" in symptoms and "Left sensory loss (Hemibody, all modalities)" in symptoms:
    vascular_analysis.add("Right Lenticulostriate arteries (deep branches of MCA) - for Lacunar Syndrome (Pure Motor or Sensorimotor Stroke)")
    lesion_locations.add("Right Internal Capsule or Basal Ganglia")
    suggest_imaging = True


if vascular_analysis:
    st.subheader("Most Likely Affected Arterial Supply:")
    for vessel in sorted(list(vascular_analysis)):
        st.markdown(f"- **{vessel}**")
    if affected_vessels: # Also list individual vessel suggestions if specific patterns weren't met
        st.markdown("---")
        st.info("Additional potentially affected vessels based on individual symptoms:")
        for vessel in sorted(list(affected_vessels)):
            if vessel not in vascular_analysis: # Avoid duplicating
                st.markdown(f"- {vessel}")
else:
    if affected_vessels: # If no combined pattern, show individual vessel suggestions
        st.subheader("Potentially Affected Arterial Supply (based on individual symptoms):")
        for vessel in sorted(list(affected_vessels)):
            st.markdown(f"- **{vessel}**")
    else:
        st.info("No specific arterial territory analysis available for selected symptoms.")

# Display Results
if lesion_locations:
    st.subheader("Likely Lesion Locations") # Changed to Step 5
    for loc in sorted(list(lesion_locations)):
        st.markdown(f"- {loc}")

    if ambiguity_notes:
        st.subheader("Considerations/Ambiguities:")
        for note in sorted(list(set(ambiguity_notes))):
            st.info(f"- {note}")

    if suggest_imaging or use_nihss:
        st.subheader("Next Steps:")
        st.success("Given the symptoms and potential vascular involvement, **imaging (CT or MRI scan of the brain)** is highly recommended to confirm the lesion location and etiology (e.g., ischemic stroke, hemorrhage).")
        if "Spinal Cord" in str(lesion_locations):
            st.success("If spinal cord involvement is suspected (e.g., dissociated sensory loss), **MRI of the spine** may also be indicated.")
        st.info("Consult with a neurologist for definitive diagnosis and management.")

else:
    st.warning("No specific lesion or vascular territory suggested. Please refine symptom selection or enter a chief complaint.")
    if chief_complaint:
        st.info("If symptoms are vague or non-localizing, consultation is recommended for further evaluation.")


# NIHSS Calculator if stroke/TIA mentioned
if use_nihss:
    st.header("NIHSS Score Calculator") # Changed to Step 6

    st.markdown("NIHSS calculator is shown because a relevant chief complaint or symptom was entered (e.g., 'weakness', 'aphasia').")

    score = 0
    missing_items = []

    nihss_data = {
        "LOC (Alert to Unresponsive)": ["0", "1", "2", "3"],
        "Month & Age": ["0", "1", "2"],
        "Blink eyes & Squeeze hands": ["0", "1", "2"],
        "Horizontal gaze palsy (Normal to Forced gaze palsy)": ["0", "1", "2"],
        "Visual (No to Complete hemianopia)": ["0", "1", "2", "3"],
        "Facial palsy (No to Complete paralysis)": ["0", "1", "2", "3"],
        "Motor arm (No drift, Drift no Hit, Drift & Hit, Some against gravity, No against gravity, No movement)": ["0", "1", "2", "3", "4"], # Changed wording to match earlier versions, assuming consistency is preferred
        "Motor leg (Same as arm)": ["0", "1", "2", "3", "4"], # Changed wording to match earlier versions, assuming consistency is preferred
        "Limb ataxia (No to Both limbs ataxia)": ["0", "1", "2"],
        "Sensory (Normal, Can sense Touch, No sense)": ["0", "1", "2"],
        "Language (Normal to Global aphasia)": ["0", "1", "2", "3"],
        "Dysarthria (No to Severe dysarthria)": ["0", "1", "2"],
        "Extinction/Inattention (Normal to Neglect)": ["0", "1", "2"]
    }

    entered_scores = {}
    for item, options in nihss_data.items():
        val = st.selectbox(f"{item}", options, key=f"nihss_{item.replace(' ', '_').replace('–', '').replace('&', '').replace('(','').replace(')','').replace(',','')}") # Made key more robust
        if val != "":
            entered_scores[item] = int(val)
            score += int(val)
        else:
            missing_items.append(item)

    st.subheader(f"Total NIHSS Score: **{score}**")
    if missing_items:
        st.warning("Missing data for: " + ", ".join(missing_items))
"# poorly written by thINGamabob" 
