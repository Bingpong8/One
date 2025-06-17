import streamlit as st

st.set_page_config(page_title="One", layout="centered", initial_sidebar_state="expanded")

st.title("Weird Localizer & N Calculator")

st.header("Presentation")
chief_complaint = st.text_input("e.g. weakness, dysarthria, numbness").strip()

st.header("Symptoms")

symptoms = st.multiselect("Choose symptom(s):", [
    "Right hemiparesis (Upper & Lower equally)",    # Subcortical
    "Right hemiparesis (Upper> Lower)",             # Cortical (e.g., MCA territory)
    "Right hemiparesis (Lower> Upper)",             # Cortical (e.g., ACA territory)
    "Left hemiparesis (Upper & Lower equally)",    # Subcortical
    "Left hemiparesis (Upper> Lower)",              # Cortical (e.g., MCA territory)
    "Left hemiparesis (Lower> Upper)",              # Cortical (e.g., ACA territory)
    "Aphasia",
    "Neglect",
    "Facial palsy (Upper & Lower face equally affected)", # LMN or brainstem (e.g., CN VII nucleus)
    "Facial palsy (Lower face only affected)",             # UMN (cortical or corticobulbar tract)
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

nihss_keywords = ["stroke", "tia", "cva", "ischemia", "hemorrhage", "infarct", "weakness", "numbness", "mute", "stuporous", "palsy", "dysarthria", "hemiparesis", "aoc", "alteration", "weak", "numb", "passing out", "seizure", "aphasia", "neglect", "vertigo", "ataxia", "sensory loss", "gaze palsy"]

use_nihss_from_symptoms = any(any(keyword in s.lower() for keyword in nihss_keywords) for s in symptoms)
use_nihss_from_chief_complaint = False
if chief_complaint:
    for keyword in nihss_keywords:
        if keyword in chief_complaint.lower():
            use_nihss_from_chief_complaint = True
            break
use_nihss = use_nihss_from_symptoms or use_nihss_from_chief_complaint


# --- Advanced Lesion Localization Logic (Processing Section - no direct display yet) ---
lesion_locations = set()
ambiguity_notes = []
suggest_imaging = False
affected_vessels = set()
vascular_analysis = set()

# Assuming lesion_locations is a set defined globally or passed as an argument
# lesion_locations = set()

def add_lesion(location_str):
    loc = location_str.strip() # Clean input
    loc_lower = loc.lower()

    # Define specific-to-general mappings for common anatomical structures
    # Keys are specific terms (or parts of them), values are the more general terms they imply.
    SPECIFIC_TO_GENERAL_MAPPING = {
        "right internal capsule": "Internal Capsule",
        "left internal capsule": "Internal Capsule",
        "right thalamus": "Thalamus",
        "left thalamus": "Thalamus",
        "right motor cortex": "Motor Cortex",
        "left motor cortex": "Motor Cortex",
        "right parietal lobe": "Parietal Lobe",
        "left parietal lobe": "Parietal Lobe",
        "right frontal lobe": "Frontal Lobe",
        "left frontal lobe": "Frontal Lobe",
        "right temporal lobe": "Temporal Lobe",
        "left temporal lobe": "Temporal Lobe",
        "right occipital lobe": "Occipital Lobe",
        "left occipital lobe": "Occipital Lobe",
        "lateral medulla": "Brainstem (General)",
        "pons": "Brainstem (General)",
        "medulla": "Brainstem (General)",
        "right basal ganglia": "Basal Ganglia",
        "left basal ganglia": "Basal Ganglia",
        "right subcortical white matter": "Subcortical White Matter",
        "left subcortical white matter": "Subcortical White Matter",
    }

    # First, check if the incoming lesion is a specific version of something already general
    added_specific = False
    for specific_term_part, general_term in SPECIFIC_TO_GENERAL_MAPPING.items():
        if specific_term_part in loc_lower:
            # If we're adding a specific term (e.g., "Right Internal Capsule")
            # And the general term already exists (e.g., "Internal Capsule")
            if general_term in lesion_locations:
                lesion_locations.remove(general_term) # Remove the general term
            lesion_locations.add(loc) # Add the specific term
            added_specific = True
            break # Once matched, no need to check other specific mappings

    if added_specific:
        return # We've handled this specific case, exit

    # If the incoming lesion is a general term, check if a more specific version already exists
    # If a more specific version of the incoming general term is already present, do NOT add the general one.
    if loc in ["Internal Capsule", "Thalamus", "Motor Cortex", "Parietal Lobe", "Frontal Lobe",
               "Temporal Lobe", "Occipital Lobe", "Basal Ganglia", "Subcortical White Matter"]:
        # Check if any specific variant of this general term already exists
        specific_exists = False
        for specific_term_part, general_term in SPECIFIC_TO_GENERAL_MAPPING.items():
            if general_term == loc: # If the current 'loc' is the general term in our map
                if f"right {general_term.lower()}" in [l.lower() for l in lesion_locations] or \
                   f"left {general_term.lower()}" in [l.lower() for l in lesion_locations]:
                    specific_exists = True
                    break
        if not specific_exists:
            lesion_locations.add(loc) # Add the general term only if no specific one exists
        return # Handled a general term, exit

    # Handle Brainstem hierarchy separately as it's a bit different
    if "brainstem" in loc_lower:
        if loc_lower == "lateral medulla" or loc_lower == "pons" or loc_lower == "medulla":
            # If adding specific brainstem part, remove general if present
            if "Brainstem (General)" in lesion_locations:
                lesion_locations.remove("Brainstem (General)")
            # Add specific brainstem part with consistent naming
            if loc_lower == "lateral medulla":
                lesion_locations.add("Lateral Medulla (Brainstem)")
            elif loc_lower == "pons":
                lesion_locations.add("Pons (Brainstem)")
            elif loc_lower == "medulla":
                lesion_locations.add("Medulla (Brainstem)")
        elif loc_lower == "brainstem (general)":
            # Add general brainstem only if no specific part already exists
            if not any(bs_part in [l.lower() for l in lesion_locations] for bs_part in ["lateral medulla (brainstem)", "pons (brainstem)", "medulla (brainstem)"]):
                lesion_locations.add("Brainstem (General)")
        else: # For other brainstem-related terms, add directly
            lesion_locations.add(loc)
        return

    # If none of the above specific/general rules apply, just add it.
    lesion_locations.add(loc)

# Example usage within your symptom rules:
# In your symptom rules, you would call add_lesion("Left Internal Capsule")
# or add_lesion("Internal Capsule") as appropriate. The add_lesion function
# itself now handles the intelligent de-duplication.

# Rule 1: Hemiparesis Patterns
if "Right hemiparesis (Upper & Lower equally)" in symptoms:
    add_lesion("Left internal capsule (Subcortical)")
    add_lesion("Left Thalamus") # Simplified
    affected_vessels.add("Left Lenticulostriate arteries (MCA deep branches)")
    affected_vessels.add("Thalamoperforating arteries (PCA deep branches)")
    suggest_imaging = True
elif "Right hemiparesis (Upper> Lower)" in symptoms:
    add_lesion("Left motor cortex")
    affected_vessels.add("Left Middle Cerebral Artery (MCA) - Superior Division")
    suggest_imaging = True
elif "Right hemiparesis (Lower> Upper)" in symptoms:
    add_lesion("Left motor cortex")
    affected_vessels.add("Left Anterior Cerebral Artery (ACA)")
    suggest_imaging = True

if "Left hemiparesis (Upper & Lower equally)" in symptoms:
    add_lesion("Right internal capsule (Subcortical)")
    add_lesion("Right Thalamus") # Simplified
    affected_vessels.add("Right Lenticulostriate arteries (MCA deep branches)")
    affected_vessels.add("Thalamoperforating arteries (PCA deep branches)")
    suggest_imaging = True
elif "Left hemiparesis (Upper> Lower)" in symptoms:
    add_lesion("Right motor cortex")
    affected_vessels.add("Right Middle Cerebral Artery (MCA) - Superior Division")
    suggest_imaging = True
elif "Left hemiparesis (Lower> Upper)" in symptoms:
    add_lesion("Right motor cortex")
    affected_vessels.add("Right Anterior Cerebral Artery (ACA)")
    suggest_imaging = True

# Rule 2: Aphasia
if "Aphasia" in symptoms:
    add_lesion("Left frontal lobe (Broca's area)")
    add_lesion("Left temporal lobe (Wernicke's area)")
    add_lesion("Left parietal lobe (Conduction Aphasia)")
    affected_vessels.add("Left Middle Cerebral Artery (MCA) - Superior Division")
    affected_vessels.add("Left Middle Cerebral Artery (MCA) - Inferior Division")
    suggest_imaging = True

# Rule 3: Neglect
if "Neglect" in symptoms:
    add_lesion("Right parietal lobe")
    add_lesion("Right frontal lobe")
    add_lesion("Right thalamus") # Simplified
    add_lesion("Right subcortical white matter") # Keeping this descriptive for now
    affected_vessels.add("Right Middle Cerebral Artery (MCA) - Inferior Division")
    suggest_imaging = True

# Rule 4: Facial Palsy
any_right_hemiparesis = any("Right hemiparesis" in s for s in symptoms)
any_left_hemiparesis = any("Left hemiparesis" in s for s in symptoms)

if "Facial palsy (Upper & Lower face equally affected)" in symptoms:
    add_lesion("Ipsilateral Pons (Facial nerve nucleus or exiting fascicles)")
    add_lesion("Ipsilateral Facial Nerve (Peripheral palsy)")
    affected_vessels.add("Basilar Artery branches (e.g., AICA, pontine arteries)")
    affected_vessels.add("External Carotid Artery branches (for peripheral facial nerve supply)")
    ambiguity_notes.append("For upper & lower face palsy, consider Bell's palsy (peripheral) vs. brainstem stroke/lesion.")
    suggest_imaging = True if use_nihss else suggest_imaging

elif "Facial palsy (Lower face only affected)" in symptoms:
    if any_right_hemiparesis:
        add_lesion("Left Motor Cortex") # Standardized
        add_lesion("Left Internal Capsule (Corticobulbar tract)") # Standardized
        affected_vessels.add("Left Middle Cerebral Artery (MCA) - Superior Division")
        affected_vessels.add("Left Lenticulostriate arteries (subcortical)")
    elif any_left_hemiparesis:
        add_lesion("Right Motor Cortex") # Standardized
        add_lesion("Right Internal Capsule (Corticobulbar tract)") # Standardized
        affected_vessels.add("Right Middle Cerebral Artery (MCA) - Superior Division")
        affected_vessels.add("Right Lenticulostriate arteries (subcortical)")
    else:
        add_lesion("Contralateral Motor Cortex or Corticobulbar Tract") # Standardized
        affected_vessels.add("Contralateral Middle Cerebral Artery (MCA) branches")
        affected_vessels.add("Contralateral Lenticulostriate arteries")
        ambiguity_notes.append("Lower face palsy without hemiparesis might suggest a focal cortical lesion or lacunar infarct.")
    suggest_imaging = True

# Rule 5: Vertigo and Ataxia (Brainstem/Cerebellum)
if "Vertigo" in symptoms:
    add_lesion("Cerebellum")
    add_lesion("Brainstem (Vestibular nuclei)") # Standardized
    affected_vessels.add("Posterior Inferior Cerebellar Artery (PICA)")
    affected_vessels.add("Anterior Inferior Cerebellar Artery (AICA)")
    affected_vessels.add("Superior Cerebellar Artery (SCA)")
    ambiguity_notes.append("Vertigo can be peripheral (inner ear) or central (brainstem/cerebellum). Consider other brainstem signs for central origin.")
    suggest_imaging = True if "Brainstem" in str(lesion_locations) or use_nihss else suggest_imaging
if "Ataxia (Limb)" in symptoms:
    add_lesion("Ipsilateral Cerebellar hemisphere")
    add_lesion("Cerebellar peduncles")
    add_lesion("Brainstem (Pons/Medulla - input/output to cerebellum)")
    affected_vessels.add("Superior Cerebellar Artery (SCA)")
    affected_vessels.add("AICA")
    affected_vessels.add("PICA")
    suggest_imaging = True
if "Ataxia (Truncal)" in symptoms:
    add_lesion("Cerebellar vermis")
    affected_vessels.add("Superior Cerebellar Artery (SCA)")
    affected_vessels.add("PICA (inferior vermis)")
    ambiguity_notes.append("Truncal ataxia is highly suggestive of cerebellar vermis involvement, often associated with gait instability.")
    suggest_imaging = True

# Rule 6: Dysarthria (Multiple locations)
if "Dysarthria" in symptoms:
    add_lesion("Cerebellum, Pons (Brainstem)") # Standardized
    add_lesion("Internal Capsule") # Standardized
    affected_vessels.add("Basilar Artery branches (pontine arteries)")
    affected_vessels.add("Lenticulostriate arteries")
    suggest_imaging = True if use_nihss else suggest_imaging

# Rule 7: Seizure (Cortical/Generalized)
if "Partial seizure" in symptoms:
    add_lesion("Focal cortical lesion (e.g., Frontal, Temporal, Parietal, Occipital lobe)")
    affected_vessels.add("Cortical branches of Middle Cerebral Artery (MCA)")
    affected_vessels.add("Anterior Cerebral Artery (ACA)")
    affected_vessels.add("Posterior Cerebral Artery (PCA)")
    ambiguity_notes.append("Partial seizures require localization of the seizure focus. Imaging is crucial.")
    suggest_imaging = True
if "Generalized seizure" in symptoms:
    add_lesion("Diffuse cortical dysfunction")
    ambiguity_notes.append("Generalized seizures often don't have a single focal lesion on imaging but can be associated with metabolic, toxic, or genetic causes. Imaging may still useful to rule out structural causes.")
    suggest_imaging = True

# Rule 8: Emotional Disturbances (Non-specific, but can be localized)
if "Emotional disturbances" in symptoms:
    add_lesion("Frontal lobe") # Standardized
    add_lesion("Temporal lobe (Amygdala, hippocampus)")
    add_lesion("Limbic system structures")
    affected_vessels.add("Anterior Cerebral Artery (ACA) branches (for frontal lobe)")
    affected_vessels.add("Middle Cerebral Artery (MCA) branches (for temporal lobe)")
    ambiguity_notes.append("Emotional disturbances are highly non-specific and can result from various neurological or psychiatric conditions. Lesion localization is challenging without other signs.")
    suggest_imaging = True if use_nihss else suggest_imaging

# Rule 9: Vision Loss
if "Vision loss (Homonymous Hemianopia)" in symptoms:
    st.info("For Homonymous Hemianopia, consider the contralateral lesion. E.g., Left HH -> Right Occipital/Optic Radiation.")
    add_lesion("Contralateral Occipital Lobe (Visual cortex)") # Standardized
    add_lesion("Contralateral Optic radiation (Parietal or Temporal lobe)")
    add_lesion("Contralateral Thalamus (Lateral Geniculate Nucleus)") # Standardized
    affected_vessels.add("Contralateral Posterior Cerebral Artery (PCA) - Calcarine branch")
    affected_vessels.add("Contralateral Middle Cerebral Artery (MCA) - deep branches (for optic radiations in temporal lobe)")
    affected_vessels.add("Contralateral Thalamoperforating arteries (from PCA)")
    suggest_imaging = True
elif "Vision loss (Unilateral - optic nerve related)" in symptoms:
    add_lesion("Ipsilateral Optic nerve")
    add_lesion("Optic Chiasm")
    affected_vessels.add("Ophthalmic Artery (branch of Internal Carotid Artery)")
    affected_vessels.add("Anterior Cerebral Artery (ACA) branches for optic chiasm")
    ambiguity_notes.append("Unilateral vision loss can also be ocular in origin. Neurological causes usually involve optic nerve or chiasm.")
    suggest_imaging = True

# Rule 10: Sensory Loss
if "Sensory loss (Hemibody, all modalities)" in symptoms:
    add_lesion("Contralateral Parietal Lobe (Somatosensory cortex)") # Standardized
    add_lesion("Contralateral Thalamus") # Standardized
    add_lesion("Contralateral Internal Capsule (Sensory tracts)") # Standardized
    affected_vessels.add("Contralateral Middle Cerebral Artery (MCA) - Parietal branches")
    affected_vessels.add("Contralateral Thalamoperforating arteries (from PCA)")
    affected_vessels.add("Contralateral Lenticulostriate arteries (from MCA)")
    affected_vessels.add("Anterior Choroidal Artery (from ICA)")
    suggest_imaging = True
elif "Sensory loss (Dissociated - e.g., pain/temp affected, light touch spared)" in symptoms:
    add_lesion("Brainstem (Lateral Medulla for Wallenberg's syndrome - ipsilateral face/contralateral body pain/temp)") # Specific detail here
    add_lesion("Spinal Cord") # Standardized
    affected_vessels.add("Posterior Inferior Cerebellar Artery (PICA) for lateral medulla")
    affected_vessels.add("Spinal Arteries (Anterior or Posterior Spinal Arteries)")
    ambiguity_notes.append("Dissociated sensory loss strongly suggests a brainstem or spinal cord lesion.")
    suggest_imaging = True

# Rule 11: Tongue Deviation
if "Tongue deviation" in symptoms:
    add_lesion("Ipsilateral Medulla (Hypoglossal nucleus - CN XII)")
    add_lesion("Ipsilateral Hypoglossal Nerve (Peripheral)")
    affected_vessels.add("Vertebral Artery or its medullary branches")
    ambiguity_notes.append("Tongue deviation can be due to central or peripheral lesions. Unilateral weakness causing deviation to the weak side.")
    suggest_imaging = True if use_nihss else suggest_imaging

# Rule 12: Horner’s syndrome
if "Horner’s syndrome" in symptoms:
    add_lesion("Ipsilateral Lateral Medulla (Wallenberg's syndrome)")
    add_lesion("Ipsilateral Pons (Brainstem)") # Standardized
    add_lesion("Hypothalamospinal tract (anywhere from hypothalamus down to T1)")
    add_lesion("Carotid Artery dissection (sympathetic chain involvement)")
    affected_vessels.add("Posterior Inferior Cerebellar Artery (PICA) for lateral medulla")
    affected_vessels.add("Basilar Artery branches (pontine arteries) for pons")
    affected_vessels.add("Carotid Artery (for dissection)")
    ambiguity_notes.append("Horner's syndrome requires careful evaluation for the level of sympathetic chain involvement (central, preganglionic, postganglionic).")
    suggest_imaging = True

# Rule 13: Gaze Palsy
if "Gaze palsy (Conjugate, toward lesion)" in symptoms:
    add_lesion("Ipsilateral Frontal eye field")
    add_lesion("Ipsilateral Pontine gaze center (PPRF)")
    affected_vessels.add("Middle Cerebral Artery (MCA) - Superior Division (frontal eye field)")
    affected_vessels.add("Basilar Artery branches (pontine arteries) for PPRF")
    suggest_imaging = True
elif "Gaze palsy (Conjugate, away from lesion)" in symptoms:
    add_lesion("Contralateral Frontal eye field (Irritative lesion)")
    add_lesion("Basal Ganglia/Thalamus (less common for conjugate deviation)")
    affected_vessels.add("Contralateral Middle Cerebral Artery (MCA) - Superior Division")
    affected_vessels.add("Lenticulostriate arteries (from MCA)")
    affected_vessels.add("Thalamoperforating arteries (from PCA)")
    suggest_imaging = True
elif "Gaze palsy (Internuclear Ophthalmoplegia - INO)" in symptoms:
    add_lesion("Medial Longitudinal Fasciculus (MLF) in Brainstem (usually Pons)")
    affected_vessels.add("Basilar Artery branches (pontine arteries, e.g., paramedian branches)")
    ambiguity_notes.append("INO is highly suggestive of a brainstem lesion, often seen in multiple sclerosis or stroke.")
    suggest_imaging = True


# --- Combine for Vascular Territory Analysis (Processing, not direct display) ---
# Special combined rules for common stroke syndromes
if "Right hemiparesis (Upper> Lower)" in symptoms and "Aphasia" in symptoms:
    vascular_analysis.add("Left Middle Cerebral Artery (MCA) - Superior Division (classic for Broca's aphasia and right arm/face weakness)")
    add_lesion("Left Frontal Lobe") # Standardized
    add_lesion("Left Parietal Lobe") # Standardized
    suggest_imaging = True
elif "Left hemiparesis (Upper> Lower)" in symptoms and "Neglect" in symptoms:
    vascular_analysis.add("Right Middle Cerebral Artery (MCA) - Inferior Division (classic for neglect and left arm/face weakness)")
    add_lesion("Right Parietal Lobe") # Standardized
    add_lesion("Right Temporal Lobe") # Standardized
    suggest_imaging = True
elif "Vision loss (Homonymous Hemianopia)" in symptoms and "Aphasia" in symptoms:
    vascular_analysis.add("Left Middle Cerebral Artery (MCA) - complete occlusion or Posterior Cerebral Artery (PCA) - with cortical aphasia")
    ambiguity_notes.append("Homonymous hemianopia with aphasia might suggest a large MCA stroke affecting visual pathways or a complex PCA stroke.")
    suggest_imaging = True
elif all(s in symptoms for s in ["Vertigo", "Dysarthria", "Facial palsy (Upper & Lower face equally affected)", "Sensory loss (Dissociated - e.g., pain/temp affected, light touch spared)"]):
    vascular_analysis.add("Vertebrobasilar System - Posterior Inferior Cerebellar Artery (PICA) - for Lateral Medullary (Wallenberg's) Syndrome")
    add_lesion("Ipsilateral Lateral Medulla")
    suggest_imaging = True
elif all(s in symptoms for s in ["Right hemiparesis (Upper & Lower equally)", "Facial palsy (Lower face only affected)", "Sensory loss (Hemibody, all modalities)"]):
    vascular_analysis.add("Left Lenticulostriate arteries (deep branches of MCA) - for Lacunar Syndrome (Pure Motor or Sensorimotor Stroke)")
    add_lesion("Left Internal Capsule") # Standardized
    add_lesion("Left Basal Ganglia") # Standardized
    suggest_imaging = True
elif all(s in symptoms for s in ["Left hemiparesis (Upper & Lower equally)", "Facial palsy (Lower face only affected)", "Sensory loss (Hemibody, all modalities)"]):
    vascular_analysis.add("Right Lenticulostriate arteries (deep branches of MCA) - for Lacunar Syndrome (Pure Motor or Sensorimotor Stroke)")
    add_lesion("Right Internal Capsule") # Standardized
    add_lesion("Right Basal Ganglia") # Standardized
    suggest_imaging = True


# --- Display Results Section ---

if lesion_locations or affected_vessels:
    # 1. Display Likely Lesion Locations
    st.header("Likely Lesion Locations")
    if lesion_locations:
        for loc in sorted(list(lesion_locations)):
            st.markdown(f"- {loc}")
    else:
        st.info("No specific lesion locations identified from selected symptoms, but vascular involvement may be suggested below.")

    if ambiguity_notes:
        st.subheader("Considerations/Ambiguities:")
        for note in sorted(list(set(ambiguity_notes))):
            st.info(f"- {note}")

    # 2. Display Affected Vascular Territory Analysis
    st.header("Affected Vascular Territory Analysis")
    if vascular_analysis:
        st.subheader("Most Likely Affected Arterial Supply:")
        for vessel in sorted(list(vascular_analysis)):
            st.markdown(f"- **{vessel}**")

        # Now, list additional individual vessels *not already covered by the specific syndromes*
        additional_vessels_to_display = set()
        for individual_vessel in affected_vessels:
            is_covered = False
            for syndrome_vessel in vascular_analysis:
                # This checks if the individual vessel string is *contained within* a syndrome vessel string.
                # Example: "Left Middle Cerebral Artery (MCA) - Superior Division" is "contained" in
                # "Left Middle Cerebral Artery (MCA) - Superior Division (classic for Broca's aphasia...)"
                if individual_vessel in syndrome_vessel:
                    is_covered = True
                    break
            if not is_covered:
                additional_vessels_to_display.add(individual_vessel)

        if additional_vessels_to_display:
            st.markdown("---")
            st.info("Additional potentially affected vessels based on individual symptoms:")
            for vessel in sorted(list(additional_vessels_to_display)):
                st.markdown(f"- {vessel}")
    else:
        if affected_vessels:
            st.subheader("Potentially Affected Arterial Supply (based on individual symptoms):")
            for vessel in sorted(list(affected_vessels)):
                st.markdown(f"- **{vessel}**")
        else:
            st.info("No specific arterial territory analysis available for selected symptoms.")

    # 3. Next Steps (Imaging Recommendation)
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
    st.header("NIHSS Score Calculator")

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
        "Motor arm (No drift, Drift no Hit, Drift & Hit, Some against gravity, No against gravity, No movement)": ["0", "1", "2", "3", "4"],
        "Motor leg (Same as arm)": ["0", "1", "2", "3", "4"],
        "Limb ataxia (No to Both limbs ataxia)": ["0", "1", "2"],
        "Sensory (Normal, Can sense Touch, No sense)": ["0", "1", "2"],
        "Language (Normal to Global aphasia)": ["0", "1", "2", "3"],
        "Dysarthria (No to Severe dysarthria)": ["0", "1", "2"],
        "Extinction/Inattention (Normal to Neglect)": ["0", "1", "2"]
    }

    entered_scores = {}
    for item, options in nihss_data.items():
        val = st.selectbox(f"{item}", options, key=f"nihss_{item.replace(' ', '_').replace('–', '').replace('&', '').replace('(','').replace(')','').replace(',','').lower()}")
        if val != "":
            entered_scores[item] = int(val)
            score += int(val)
        else:
            missing_items.append(item)

    st.subheader(f"Total NIHSS Score: **{score}**")
    if missing_items:
        st.warning("Missing data for: " + ", ".join(missing_items))

# At the end of your app script
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='font-size:10px; color:gray;'>poorly written by thINGamabob, good patriotic techmarine and their evil twin</p>", unsafe_allow_html=True)
