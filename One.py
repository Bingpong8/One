import streamlit as st

st.set_page_config(page_title="One", layout="centered", initial_sidebar_state="expanded")

st.title("Weird Localizer & N Calculator")

st.header("Chief Complaint")
chief_complaint = st.text_input("e.g., 'weakness', 'dysarthria', 'numbness'", "").strip()

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

# Helper function to add a lesion location, handling standardization
def add_lesion(location_str):
    # Standardize common variations or overlapping terms
    if "internal capsule" in location_str.lower():
        if "right internal capsule" in location_str.lower():
            lesion_locations.add("Right Internal Capsule")
        elif "left internal capsule" in location_str.lower():
            lesion_locations.add("Left Internal Capsule")
        else:
            lesion_locations.add("Internal Capsule") # Fallback for generic
    elif "thalamus" in location_str.lower():
        if "right thalamus" in location_str.lower():
            lesion_locations.add("Right Thalamus")
        elif "left thalamus" in location_str.lower():
            lesion_locations.add("Left Thalamus")
        else:
            lesion_locations.add("Thalamus") # Fallback for generic
    elif "motor cortex" in location_str.lower() or "precentral gyrus" in location_str.lower():
        if "right motor cortex" in location_str.lower() or "right precentral gyrus" in location_str.lower():
            lesion_locations.add("Right Motor Cortex")
        elif "left motor cortex" in location_str.lower() or "left precentral gyrus" in location_str.lower():
            lesion_locations.add("Left Motor Cortex")
        else:
            lesion_locations.add("Motor Cortex")
    elif "parietal lobe" in location_str.lower():
        if "right parietal lobe" in location_str.lower():
            lesion_locations.add("Right Parietal Lobe")
        elif "left parietal lobe" in location_str.lower():
            lesion_locations.add("Left Parietal Lobe")
        else:
            lesion_locations.add("Parietal Lobe")
    elif "frontal lobe" in location_str.lower():
        if "right frontal lobe" in location_str.lower():
            lesion_locations.add("Right Frontal Lobe")
        elif "left frontal lobe" in location_str.lower():
            lesion_locations.add("Left Frontal Lobe")
        else:
            lesion_locations.add("Frontal Lobe")
    elif "temporal lobe" in location_str.lower():
        if "right temporal lobe" in location_str.lower():
            lesion_locations.add("Right Temporal Lobe")
        elif "left temporal lobe" in location_str.lower():
            lesion_locations.add("Left Temporal Lobe")
        else:
            lesion_locations.add("Temporal Lobe")
    elif "occipital lobe" in location_str.lower():
        if "right occipital lobe" in location_str.lower():
            lesion_locations.add("Right Occipital Lobe")
        elif "left occipital lobe" in location_str.lower():
            lesion_locations.add("Left Occipital Lobe")
        else:
            lesion_locations.add("Occipital Lobe")
    elif "pons" in location_str.lower():
        lesion_locations.add("Pons (Brainstem)")
    elif "medulla" in location_str.lower():
        lesion_locations.add("Medulla (Brainstem)")
    elif "cerebellum" in location_str.lower():
        lesion_locations.add("Cerebellum")
    elif "brainstem" in location_str.lower():
        lesion_locations.add("Brainstem (General)")
    elif "spinal cord" in location_str.lower():
        lesion_locations.add("Spinal Cord")
    elif "basal ganglia" in location_str.lower():
        if "right basal ganglia" in location_str.lower():
            lesion_locations.add("Right Basal Ganglia")
        elif "left basal ganglia" in location_str.lower():
            lesion_locations.add("Left Basal Ganglia")
        else:
            lesion_locations.add("Basal Ganglia")
    else: # Add as is if no specific standardization rule
        lesion_locations.add(location_str)


# Rule 1: Hemiparesis Patterns
if "Right hemiparesis (Upper & Lower equally)" in symptoms:
    add_lesion("Left internal capsule (Subcortical)")
    add_lesion("Left Thalamus") # Simplified
    affected_vessels.add("Left Lenticulostriate arteries (MCA deep branches)")
    affected_vessels.add("Thalamoperforating arteries (PCA deep branches)")
    suggest_imaging = True
elif "Right hemiparesis (Upper> Lower)" in symptoms:
    add_lesion("Left motor cortex (Middle Cerebral Artery territory)")
    affected_vessels.add("Left Middle Cerebral Artery (MCA) - Superior Division")
    suggest_imaging = True
elif "Right hemiparesis (Lower> Upper)" in symptoms:
    add_lesion("Left motor cortex (Anterior Cerebral Artery territory)")
    affected_vessels.add("Left Anterior Cerebral Artery (ACA)")
    suggest_imaging = True

if "Left hemiparesis (Upper & Lower equally)" in symptoms:
    add_lesion("Right internal capsule (Subcortical)")
    add_lesion("Right Thalamus") # Simplified
    affected_vessels.add("Right Lenticulostriate arteries (MCA deep branches)")
    affected_vessels.add("Thalamoperforating arteries (PCA deep branches)")
    suggest_imaging = True
elif "Left hemiparesis (Upper> Lower)" in symptoms:
    add_lesion("Right motor cortex (Middle Cerebral Artery territory)")
    affected_vessels.add("Right Middle Cerebral Artery (MCA) - Superior Division")
    suggest_imaging = True
elif "Left hemiparesis (Lower> Upper)" in symptoms:
    add_lesion("Right motor cortex (Anterior Cerebral Artery territory)")
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
    add_lesion("Pons (Brainstem)") # Standardized
    add_lesion("Cerebellum")
    add_lesion("Internal Capsule") # Standardized
    add_lesion("Motor Cortex (Bilateral lesions)") # Standardized
    affected_vessels.add("Basilar Artery branches (pontine arteries)")
    affected_vessels.add("Lenticulostriate arteries")
    affected_vessels.add("ACA/MCA/PCA branches (non-specific)")
    ambiguity_notes.append("Dysarthria is a non-localizing sign alone, but in combination with other deficits, it helps pinpoint the lesion.")
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
