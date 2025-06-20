import streamlit as st

st.set_page_config(page_title="One", layout="centered", initial_sidebar_state="expanded")

st.title("Weird Localizer & N Calculator")

st.header("Presentation")
chief_complaint = st.text_input("e.g. weakness, dysarthria, numbness").strip()

st.header("Symptoms")

symptoms = st.multiselect("Choose symptom(s):", [
    "Right hemiparesis (Upper & Lower equally)",    
    "Right hemiparesis (Upper> Lower)",             
    "Right hemiparesis (Lower> Upper)",             
    "Left hemiparesis (Upper & Lower equally)",    
    "Left hemiparesis (Upper> Lower)",              
    "Left hemiparesis (Lower> Upper)",             
    "Aphasia",
    "Neglect",
    "Facial palsy (Upper & Lower face equally affected)", 
    "Facial palsy (Lower face only affected)",             
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
    "Sensory loss (Dissociated - e.g. pain/temp affected, light touch spared)", 
    "Tongue deviation",
    "Horner’s syndrome",
    "Gaze palsy (Conjugate, toward lesion)",
    "Gaze palsy (Conjugate, away from lesion)",
    "Gaze palsy (Internuclear Ophthalmoplegia - INO)"
    "Chorea",
    "Hemiballism",
    "Nystagmus",
    "Hiccup (Persistent/Intractable)"
])

# Determine if NIHSS should be used
nihss_keywords = ["weakness", "numbness", "mute", "stuporous", "palsy", "dysarthria", "hemiparesis", "aoc", "alteration", "weak", "numb", "passing out", "seizure", "aphasia", "neglect", "vertigo", "ataxia", "sensory loss", "gaze palsy", "chorea", "hemiballism", "nystagmus", "hiccup"]

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
ambiguity_notes = set() # Use a set to automatically handle duplicate notes
suggest_imaging = False
affected_vessels = set()
vascular_analysis = set()

# Helper function to add a lesion location, handling standardization and common overlaps
def add_lesion(location_str):
    loc = location_str.strip()
    loc_lower = loc.lower()

    # Comprehensive standardization and de-duplication logic
    # Prioritize specific terms, but ensure general terms are added if no specific ones exist for a category.
  
    # 1. Handle specific brainstem parts vs. general brainstem
    if "lateral medulla" in loc_lower or "pons" in loc_lower or "medulla" in loc_lower:
        specific_brainstem_term = ""
        if "lateral medulla" in loc_lower:
            specific_brainstem_term = "Lateral Medulla (Brainstem)"
        elif "pons" in loc_lower:
            specific_brainstem_term = "Pons (Brainstem)"
        elif "medulla" in loc_lower: # Catch general medulla if not lateral
            specific_brainstem_term = "Medulla (Brainstem)"

        if specific_brainstem_term:
            # If a specific brainstem part is being added, remove general brainstem if present
            if "Brainstem (General)" in lesion_locations:
                lesion_locations.remove("Brainstem (General)")
            lesion_locations.add(specific_brainstem_term)
            return # Handled
    elif "brainstem" in loc_lower: # Catch general brainstem only if no specific parts are already there
        if not any(bs_part in l for l in lesion_locations for bs_part in ["Lateral Medulla", "Pons", "Medulla (Brainstem)"]):
            lesion_locations.add("Brainstem (General)")
        return # Handled

    # 2. Handle internal capsule variations
    if "internal capsule" in loc_lower:
        if "right internal capsule" in loc_lower:
            if "Left Internal Capsule" in lesion_locations: # If opposite side specific already exists, don't remove
                pass
            elif "Internal Capsule" in lesion_locations: # If general exists, remove it
                lesion_locations.remove("Internal Capsule")
            lesion_locations.add("Right Internal Capsule")
        elif "left internal capsule" in loc_lower:
            if "Right Internal Capsule" in lesion_locations:
                pass
            elif "Internal Capsule" in lesion_locations:
                lesion_locations.remove("Internal Capsule")
            lesion_locations.add("Left Internal Capsule")
        else: # Generic "Internal Capsule"
            # Add generic only if no specific left/right already exists
            if not ("Right Internal Capsule" in lesion_locations or "Left Internal Capsule" in lesion_locations):
                lesion_locations.add("Internal Capsule")
        return # Handled

    # 3. Handle Thalamus variations
    if "thalamus" in loc_lower:
        if "right thalamus" in loc_lower:
            if "Left Thalamus" in lesion_locations:
                pass
            elif "Thalamus" in lesion_locations:
                lesion_locations.remove("Thalamus")
            lesion_locations.add("Right Thalamus")
        elif "left thalamus" in loc_lower:
            if "Right Thalamus" in lesion_locations:
                pass
            elif "Thalamus" in lesion_locations:
                lesion_locations.remove("Thalamus")
            lesion_locations.add("Left Thalamus")
        else: # Generic "Thalamus"
            if not ("Right Thalamus" in lesion_locations or "Left Thalamus" in lesion_locations):
                lesion_locations.add("Thalamus")
        return # Handled

    # 4. Handle Motor Cortex variations
    if "motor cortex" in loc_lower or "precentral gyrus" in loc_lower:
        if "right motor cortex" in loc_lower or "right precentral gyrus" in loc_lower:
            if "Left Motor Cortex" in lesion_locations:
                pass
            elif "Motor Cortex" in lesion_locations:
                lesion_locations.remove("Motor Cortex")
            lesion_locations.add("Right Motor Cortex")
        elif "left motor cortex" in loc_lower or "left precentral gyrus" in loc_lower:
            if "Right Motor Cortex" in lesion_locations:
                pass
            elif "Motor Cortex" in lesion_locations:
                lesion_locations.remove("Motor Cortex")
            lesion_locations.add("Left Motor Cortex")
        else: # Generic "Motor Cortex"
            if not ("Right Motor Cortex" in lesion_locations or "Left Motor Cortex" in lesion_locations):
                lesion_locations.add("Motor Cortex")
        return # Handled

    # 5. Handle Lobe variations (Parietal, Frontal, Temporal, Occipital)
    lobes = ["parietal", "frontal", "temporal", "occipital"]
    for lobe in lobes:
        if f"{lobe} lobe" in loc_lower:
            if f"right {lobe} lobe" in loc_lower:
                if f"Left {lobe.capitalize()} Lobe" in lesion_locations:
                    pass
                elif f"{lobe.capitalize()} Lobe" in lesion_locations:
                    lesion_locations.remove(f"{lobe.capitalize()} Lobe")
                lesion_locations.add(f"Right {lobe.capitalize()} Lobe")
            elif f"left {lobe} lobe" in loc_lower:
                if f"Right {lobe.capitalize()} Lobe" in lesion_locations:
                    pass
                elif f"{lobe.capitalize()} Lobe" in lesion_locations:
                    lesion_locations.remove(f"{lobe.capitalize()} Lobe")
                lesion_locations.add(f"Left {lobe.capitalize()} Lobe")
            else: # Generic Lobe
                if not (f"Right {lobe.capitalize()} Lobe" in lesion_locations or f"Left {lobe.capitalize()} Lobe" in lesion_locations):
                    lesion_locations.add(f"{lobe.capitalize()} Lobe")
            return # Handled

    # 6. Handle Basal Ganglia variations
    if "basal ganglia" in loc_lower:
        if "right basal ganglia" in loc_lower:
            if "Left Basal Ganglia" in lesion_locations:
                pass
            elif "Basal Ganglia" in lesion_locations:
                lesion_locations.remove("Basal Ganglia")
            lesion_locations.add("Right Basal Ganglia")
        elif "left basal ganglia" in loc_lower:
            if "Right Basal Ganglia" in lesion_locations:
                pass
            elif "Basal Ganglia" in lesion_locations:
                lesion_locations.remove("Basal Ganglia")
            lesion_locations.add("Left Basal Ganglia")
        else: # Generic "Basal Ganglia"
            if not ("Right Basal Ganglia" in lesion_locations or "Left Basal Ganglia" in lesion_locations):
                lesion_locations.add("Basal Ganglia")
        return # Handled

    # 7. Handle Subcortical White Matter variations
    if "subcortical white matter" in loc_lower:
        if "right subcortical white matter" in loc_lower:
            if "Left Subcortical White Matter" in lesion_locations:
                pass
            elif "Subcortical White Matter" in lesion_locations:
                lesion_locations.remove("Subcortical White Matter")
            lesion_locations.add("Right Subcortical White Matter")
        elif "left subcortical white matter" in loc_lower:
            if "Right Subcortical White Matter" in lesion_locations:
                pass
            elif "Subcortical White Matter" in lesion_locations:
                lesion_locations.remove("Subcortical White Matter")
            lesion_locations.add("Left Subcortical White Matter")
        else: # Generic "Subcortical White Matter"
            if not ("Right Subcortical White Matter" in lesion_locations or "Left Subcortical White Matter" in lesion_locations):
                lesion_locations.add("Subcortical White Matter")
        return # Handled

    # Default: Add as is if no specific standardization rule
    lesion_locations.add(loc)


# --- NEW: Helper to standardize vessel names for de-duplication within affected_vessels ---
def standardize_vessel_name(vessel_str):
    v_lower = vessel_str.lower()

    # Prioritize most specific forms if they are explicitly mentioned
    if "middle cerebral artery (mca) - superior division" in v_lower:
        return "Middle Cerebral Artery (MCA) - Superior Division"
    if "middle cerebral artery (mca) - inferior division" in v_lower:
        return "Middle Cerebral Artery (MCA) - Inferior Division"
    if "posterior inferior cerebellar artery (pica)" in v_lower:
        return "Posterior Inferior Cerebellar Artery (PICA)"
    if "anterior inferior cerebellar artery (aica)" in v_lower:
        return "Anterior Inferior Cerebellar Artery (AICA)"
    if "superior cerebellar artery (sca)" in v_lower:
        return "Superior Cerebellar Artery (SCA)"
    if "lenticulostriate arteries" in v_lower:
        return "Lenticulostriate arteries"
    if "thalamoperforating arteries" in v_lower:
        return "Thalamoperforating arteries"
    if "anterior cerebral artery (aca)" in v_lower:
        return "Anterior Cerebral Artery (ACA)"
    if "posterior cerebral artery (pca)" in v_lower:
        if "calcarine branch" in v_lower:
            return "Posterior Cerebral Artery (PCA) - Calcarine branch"
        return "Posterior Cerebral Artery (PCA)"
    if "basilar artery" in v_lower:
        return "Basilar Artery" # Keeping it general here, specialized branches are handled below
    if "vertebral artery" in v_lower:
        return "Vertebral Artery"
    if "ophthalmic artery" in v_lower:
        return "Ophthalmic Artery"
    if "internal carotid artery (ica)" in v_lower or "internal carotid artery" in v_lower:
        return "Internal Carotid Artery (ICA)"
    if "external carotid artery (eca)" in v_lower or "external carotid artery" in v_lower:
        return "External Carotid Artery (ECA)"
    if "spinal arteries" in v_lower:
        return "Spinal Arteries"
    if "anterior choroidal artery" in v_lower:
        return "Anterior Choroidal Artery"

    # General arterial systems / groups (less specific, but still useful)
    if "middle cerebral artery (mca) branches" in v_lower or "mca branches" in v_lower:
        return "Middle Cerebral Artery (MCA) branches"
    if "basilar artery branches" in v_lower or "pontine arteries" in v_lower:
        return "Basilar Artery branches (pontine arteries)"
    if "contralateral middle cerebral artery (mca) branches" in v_lower:
        return "Contralateral Middle Cerebral Artery (MCA) branches"
    if "contralateral lenticulostriate arteries" in v_lower:
        return "Contralateral Lenticulostriate arteries"
    if "contralateral posterior cerebral artery (pca) - calcarine branch" in v_lower:
        return "Contralateral Posterior Cerebral Artery (PCA) - Calcarine branch"
    if "contralateral thalamoperforating arteries" in v_lower:
        return "Contralateral Thalamoperforating arteries"

    # If no specific rule matches, return original (or a cleaned version)
    return vessel_str.strip()

# --- NEW: Function to intelligently add vessels to affected_vessels set ---
def add_vessel_to_affected(vessel_name_raw):
    standardized_vessel = standardize_vessel_name(vessel_name_raw)

    # Check for direct duplicates first (set handles this implicitly, but good to think about)
    if standardized_vessel in affected_vessels:
        return # Already present in its standardized form

    # Handle specific vs. general relationships for de-duplication
    # This is similar to the add_lesion logic, but for vessels

    # Define mappings of specific vessel terms to their more general parents/categories
    # The key is a part of the specific vessel name, the value is the general vessel name
    # that it makes redundant if the specific one is present.
    # Note: These are canonical/standardized names returned by standardize_vessel_name
    SPECIFIC_TO_GENERAL_VESSEL_MAP = {
        "MCA Superior Division": "Middle Cerebral Artery (MCA) branches",
        "MCA Inferior Division": "Middle Cerebral Artery (MCA) branches",
        "Lenticulostriate arteries": "Middle Cerebral Artery (MCA) branches",
        "Posterior Inferior Cerebellar Artery (PICA)": "Basilar Artery branches (pontine arteries)",
        "Anterior Inferior Cerebellar Artery (AICA)": "Basilar Artery branches (pontine arteries)",
        "Superior Cerebellar Artery (SCA)": "Basilar Artery branches (pontine arteries)",
        "Thalamoperforating arteries": "Posterior Cerebral Artery (PCA)",
        "Posterior Cerebral Artery (PCA) - Calcarine branch": "Posterior Cerebral Artery (PCA)",
        "Ophthalmic Artery": "Internal Carotid Artery (ICA)",
        "Anterior Choroidal Artery": "Internal Carotid Artery (ICA)",
        # Add contralateral mappings if necessary, or ensure standardize_vessel_name handles side
        "Contralateral Middle Cerebral Artery (MCA) branches": "Middle Cerebral Artery (MCA) branches", # Generalizes side for comparison
        "Contralateral Lenticulostriate arteries": "Lenticulostriate arteries",
        "Contralateral Posterior Cerebral Artery (PCA) - Calcarine branch": "Posterior Cerebral Artery (PCA) - Calcarine branch",
        "Contralateral Thalamoperforating arteries": "Thalamoperforating arteries",
    }
    
    # Clean up the exact matches from the dictionary to avoid infinite loops or incorrect removal
    # Example: If "Lenticulostriate arteries" is mapped to itself as a general term, it won't remove.
    # The purpose is to remove *less specific* versions.

    # Check if a more specific version of an existing general vessel is being added
    for existing_vessel in list(affected_vessels): # Iterate over a copy to allow modification
        standardized_existing = standardize_vessel_name(existing_vessel)
        
        # Check if the incoming standardized_vessel makes the existing_vessel redundant
        # (i.e., incoming is more specific, existing is its general form)
        for specific_term, general_term in SPECIFIC_TO_GENERAL_VESSEL_MAP.items():
            if standardized_vessel == specific_term and standardized_existing == general_term:
                affected_vessels.remove(existing_vessel)
                # No 'return' here, we still need to add the specific vessel
                
    # Check if the incoming vessel is a general term that is made redundant by an already existing specific term
    is_redundant = False
    for specific_term, general_term in SPECIFIC_TO_GENERAL_VESSEL_MAP.items():
        if standardized_vessel == general_term: # If the incoming is a general term
            # Check if any of its specific variants are already in affected_vessels
            # This requires checking the *standardized* forms of existing vessels against the specific_term
            for existing_in_set in affected_vessels:
                if standardize_vessel_name(existing_in_set) == specific_term:
                    is_redundant = True
                    break
        if is_redundant:
            break

    if not is_redundant:
        affected_vessels.add(standardized_vessel) # Add the standardized form


# --- Replaced direct .add() calls with add_vessel_to_affected() ---

# Rule 1: Hemiparesis Patterns
# Right side weakness -> Left Hemisphere
if "Right hemiparesis (Upper & Lower equally)" in symptoms:
    add_lesion("Left internal capsule")
    add_lesion("Left Thalamus")
    add_vessel_to_affected("Lenticulostriate arteries") # Standardized name
    add_vessel_to_affected("Thalamoperforating arteries") # Standardized name
    suggest_imaging = True
elif "Right hemiparesis (Upper> Lower)" in symptoms:
    add_lesion("Left motor cortex")
    add_vessel_to_affected("Middle Cerebral Artery (MCA) - Superior Division") # Standardized name
    suggest_imaging = True
elif "Right hemiparesis (Lower> Upper)" in symptoms:
    add_lesion("Left motor cortex")
    add_vessel_to_affected("Anterior Cerebral Artery (ACA)") # Standardized name
    suggest_imaging = True

# Left side weakness -> Right Hemisphere
if "Left hemiparesis (Upper & Lower equally)" in symptoms:
    add_lesion("Right internal capsule")
    add_lesion("Right Thalamus")
    add_vessel_to_affected("Lenticulostriate arteries") # Standardized name
    add_vessel_to_affected("Thalamoperforating arteries") # Standardized name
    suggest_imaging = True
elif "Left hemiparesis (Upper> Lower)" in symptoms:
    add_lesion("Right motor cortex")
    add_vessel_to_affected("Middle Cerebral Artery (MCA) - Superior Division") # Standardized name
    suggest_imaging = True
elif "Left hemiparesis (Lower> Upper)" in symptoms:
    add_lesion("Right motor cortex")
    add_vessel_to_affected("Anterior Cerebral Artery (ACA)") # Standardized name
    suggest_imaging = True

# Rule 2: Aphasia
if "Aphasia" in symptoms:
    add_lesion("Left frontal lobe")
    add_lesion("Left temporal lobe")
    add_lesion("Left parietal lobe")
    add_vessel_to_affected("Middle Cerebral Artery (MCA) - Superior Division") # Standardized
    add_vessel_to_affected("Middle Cerebral Artery (MCA) - Inferior Division") # Standardized
    suggest_imaging = True

# Rule 3: Neglect
if "Neglect" in symptoms:
    add_lesion("Right parietal lobe")
    add_lesion("Right frontal lobe")
    add_lesion("Right thalamus")
    add_lesion("Right subcortical white matter")
    add_vessel_to_affected("Middle Cerebral Artery (MCA) - Inferior Division") # Standardized
    suggest_imaging = True

# Rule 4: Facial Palsy
any_right_hemiparesis = any("Right hemiparesis" in s for s in symptoms)
any_left_hemiparesis = any("Left hemiparesis" in s for s in symptoms)

if "Facial palsy (Upper & Lower face equally affected)" in symptoms:
    add_lesion("Pons (Brainstem)")
    add_lesion("Ipsilateral Facial Nerve (Peripheral palsy)")
    add_vessel_to_affected("Basilar Artery branches (pontine arteries)") # Standardized
    add_vessel_to_affected("External Carotid Artery (ECA)") # Standardized
    ambiguity_notes.add("For upper & lower face palsy, consider Bell's palsy (peripheral) vs. brainstem stroke/lesion.")
    suggest_imaging = True if use_nihss else suggest_imaging

elif "Facial palsy (Lower face only affected)" in symptoms:
    if any_right_hemiparesis:
        add_lesion("Left Motor Cortex")
        add_lesion("Left Internal Capsule (Corticobulbar tract)")
        add_vessel_to_affected("Middle Cerebral Artery (MCA) - Superior Division") # Standardized
        add_vessel_to_affected("Lenticulostriate arteries") # Standardized
    elif any_left_hemiparesis:
        add_lesion("Right Motor Cortex")
        add_lesion("Right Internal Capsule (Corticobulbar tract)")
        add_vessel_to_affected("Middle Cerebral Artery (MCA) - Superior Division") # Standardized
        add_vessel_to_affected("Lenticulostriate arteries") # Standardized
    else:
        add_lesion("Contralateral Motor Cortex or Corticobulbar Tract")
        add_vessel_to_affected("Middle Cerebral Artery (MCA) branches") # General contralateral
        add_vessel_to_affected("Lenticulostriate arteries") # General contralateral
        ambiguity_notes.add("Lower face palsy without hemiparesis might suggest a focal cortical lesion or lacunar infarct.")
    suggest_imaging = True

# Rule 5: Vertigo and Ataxia (Brainstem/Cerebellum)
if "Vertigo" in symptoms:
    add_lesion("Cerebellum")
    add_lesion("Brainstem (Vestibular nuclei)")
    add_vessel_to_affected("Posterior Inferior Cerebellar Artery (PICA)") # Standardized
    add_vessel_to_affected("Anterior Inferior Cerebellar Artery (AICA)") # Standardized
    add_vessel_to_affected("Superior Cerebellar Artery (SCA)") # Standardized
    ambiguity_notes.add("Vertigo can be peripheral (inner ear) or central (brainstem/cerebellum). Consider other brainstem signs for central origin.")
    suggest_imaging = True if "Brainstem (General)" in lesion_locations or "Pons (Brainstem)" in lesion_locations or "Medulla (Brainstem)" in lesion_locations or use_nihss else suggest_imaging
if "Ataxia (Limb)" in symptoms:
    add_lesion("Ipsilateral Cerebellar hemisphere")
    add_lesion("Cerebellar peduncles")
    add_lesion("Brainstem (Pons/Medulla - input/output to cerebellum)")
    add_vessel_to_affected("Superior Cerebellar Artery (SCA)") # Standardized
    add_vessel_to_affected("Anterior Inferior Cerebellar Artery (AICA)") # Standardized
    add_vessel_to_affected("Posterior Inferior Cerebellar Artery (PICA)") # Standardized
    suggest_imaging = True
if "Ataxia (Truncal)" in symptoms:
    add_lesion("Cerebellar vermis")
    add_vessel_to_affected("Superior Cerebellar Artery (SCA)") # Standardized
    add_vessel_to_affected("Posterior Inferior Cerebellar Artery (PICA)") # Standardized
    ambiguity_notes.add("Truncal ataxia is highly suggestive of cerebellar vermis involvement, often associated with gait instability.")
    suggest_imaging = True

# Rule 6: Dysarthria (Multiple locations)
if "Dysarthria" in symptoms:
    add_lesion("Pons (Brainstem)")
    add_lesion("Cerebellum")
    add_lesion("Internal Capsule")
    add_lesion("Motor Cortex (Bilateral lesions)")
    add_vessel_to_affected("Basilar Artery branches (pontine arteries)") # Standardized
    add_vessel_to_affected("Lenticulostriate arteries") # Standardized
    suggest_imaging = True if use_nihss else suggest_imaging

# Rule 7: Seizure (Cortical/Generalized)
if "Partial seizure" in symptoms:
    add_lesion("Focal cortical lesion (e.g. Frontal, Temporal, Parietal, Occipital lobe)")
    add_vessel_to_affected("Middle Cerebral Artery (MCA) branches") # Standardized
    add_vessel_to_affected("Anterior Cerebral Artery (ACA)") # Standardized
    add_vessel_to_affected("Posterior Cerebral Artery (PCA)") # Standardized
    ambiguity_notes.add("Partial seizures require localization of the seizure focus. Imaging is crucial.")
    suggest_imaging = True
if "Generalized seizure" in symptoms:
    add_lesion("Diffuse cortical dysfunction")
    ambiguity_notes.add("Generalized seizures often don't have a single focal lesion on imaging but can be associated with metabolic, toxic, or genetic causes. Imaging may still useful to rule out structural causes.")
    suggest_imaging = True

# Rule 8: Emotional Disturbances (Non-specific, but can be localized)
if "Emotional disturbances" in symptoms:
    add_lesion("Frontal Lobe")
    add_lesion("Temporal Lobe (Amygdala, hippocampus)")
    add_lesion("Limbic System Structures")
    add_vessel_to_affected("Anterior Cerebral Artery (ACA)") # Standardized
    add_vessel_to_affected("Middle Cerebral Artery (MCA) branches") # Standardized
    ambiguity_notes.add("Emotional disturbances are highly non-specific and can result from various neurological or psychiatric conditions. Lesion localization is challenging without other signs.")
    suggest_imaging = True if use_nihss else suggest_imaging

# Rule 9: Vision Loss
if "Vision loss (Homonymous Hemianopia)" in symptoms:
    st.info("For Homonymous Hemianopia, consider the contralateral lesion. e.g. Left HH -> Right Occipital/Optic Radiation.")
    add_lesion("Contralateral Occipital Lobe (Visual cortex)")
    add_lesion("Contralateral Optic radiation (Parietal or Temporal lobe)")
    add_lesion("Contralateral Thalamus (Lateral Geniculate Nucleus)")
    add_vessel_to_affected("Posterior Cerebral Artery (PCA) - Calcarine branch") # Standardized
    add_vessel_to_affected("Middle Cerebral Artery (MCA) branches") # General contralateral for optic radiations
    add_vessel_to_affected("Thalamoperforating arteries") # Standardized
    suggest_imaging = True
elif "Vision loss (Unilateral - optic nerve related)" in symptoms:
    add_lesion("Ipsilateral Optic Nerve")
    add_lesion("Optic Chiasm")
    add_vessel_to_affected("Ophthalmic Artery") # Standardized
    add_vessel_to_affected("Anterior Cerebral Artery (ACA)") # Standardized for optic chiasm
    ambiguity_notes.add("Unilateral vision loss can also be ocular in origin. Neurological causes usually involve optic nerve or chiasm.")
    suggest_imaging = True

# Rule 10: Sensory Loss
if "Sensory loss (Hemibody, all modalities)" in symptoms:
    add_lesion("Contralateral Parietal Lobe (Somatosensory cortex)")
    add_lesion("Contralateral Thalamus")
    add_lesion("Contralateral Internal Capsule (Sensory tracts)")
    add_vessel_to_affected("Middle Cerebral Artery (MCA) branches") # Standardized for parietal
    add_vessel_to_affected("Thalamoperforating arteries") # Standardized
    add_vessel_to_affected("Lenticulostriate arteries") # Standardized
    add_vessel_to_affected("Anterior Choroidal Artery") # Standardized
    suggest_imaging = True
elif "Sensory loss (Dissociated - e.g. pain/temp affected, light touch spared)" in symptoms:
    add_lesion("Brainstem (Lateral Medulla for Wallenberg's syndrome - ipsilateral face/contralateral body pain/temp)")
    add_lesion("Spinal Cord")
    add_vessel_to_affected("Posterior Inferior Cerebellar Artery (PICA)") # Standardized
    add_vessel_to_affected("Spinal Arteries") # Standardized
    ambiguity_notes.add("Dissociated sensory loss strongly suggests a brainstem or spinal cord lesion.")
    suggest_imaging = True

# Rule 11: Tongue Deviation
if "Tongue deviation" in symptoms:
    add_lesion("Ipsilateral Medulla (Hypoglossal nucleus - CN XII)")
    add_lesion("Ipsilateral Hypoglossal Nerve (Peripheral)")
    add_vessel_to_affected("Vertebral Artery") # Standardized
    ambiguity_notes.add("Tongue deviation can be due to central or peripheral lesions. Unilateral weakness causing deviation to the weak side.")
    suggest_imaging = True if use_nihss else suggest_imaging

# Rule 12: Horner’s syndrome
if "Horner’s syndrome" in symptoms:
    add_lesion("Ipsilateral Lateral Medulla (Wallenberg's syndrome)")
    add_lesion("Ipsilateral Pons (Brainstem)")
    add_lesion("Hypothalamospinal Tract")
    add_lesion("Carotid Artery dissection (sympathetic chain involvement)")
    add_vessel_to_affected("Posterior Inferior Cerebellar Artery (PICA)") # Standardized
    add_vessel_to_affected("Basilar Artery branches (pontine arteries)") # Standardized
    add_vessel_to_affected("Internal Carotid Artery (ICA)") # Standardized for dissection
    ambiguity_notes.add("Horner's syndrome requires careful evaluation for the level of sympathetic chain involvement (central, preganglionic, postganglionic).")
    suggest_imaging = True

# Rule 13: Gaze Palsy
if "Gaze palsy (Conjugate, toward lesion)" in symptoms:
    add_lesion("Ipsilateral Frontal Eye Field")
    add_lesion("Ipsilateral Pontine Gaze Center (PPRF)")
    add_vessel_to_affected("Middle Cerebral Artery (MCA) - Superior Division") # Standardized for frontal eye field
    add_vessel_to_affected("Basilar Artery branches (pontine arteries)") # Standardized for PPRF
    suggest_imaging = True
elif "Gaze palsy (Conjugate, away from lesion)" in symptoms:
    add_lesion("Contralateral Frontal Eye Field (Irritative lesion)")
    add_lesion("Basal Ganglia/Thalamus (less common for conjugate deviation)")
    add_vessel_to_affected("Middle Cerebral Artery (MCA) - Superior Division") # Standardized
    add_vessel_to_affected("Lenticulostriate arteries") # Standardized
    add_vessel_to_affected("Thalamoperforating arteries") # Standardized
    suggest_imaging = True
elif "Gaze palsy (Internuclear Ophthalmoplegia - INO)" in symptoms:
    add_lesion("Medial Longitudinal Fasciculus (MLF) in Brainstem (usually Pons)")
    add_vessel_to_affected("Basilar Artery branches (pontine arteries)") # Standardized
    ambiguity_notes.add("INO is highly suggestive of a brainstem lesion, often seen in multiple sclerosis or stroke.")
    suggest_imaging = True

# Rule 14: Chorea
if "Chorea" in symptoms:
    add_lesion("Contralateral Striatum/Subthalamic Nucleus/Thalamus/Basal Ganglia")
    add_vessel_to_affected("Lenticulostriate arteries")
    add_vessel_to_affected("Posterior Cerebral Artery (PCA) perforators")
    suggest_imaging = True

# Rule 15: Hemiballism
if "Hemiballism" in symptoms:
    add_lesion("Contralateral Subthalamic Nucleus")
    add_vessel_to_affected("Lenticulostriate arteries")
    add_vessel_to_affected("Thalamoperforating arteries")
    add_vessel_to_affected("Anterior Choroidal Artery")
    suggest_imaging = True

# Rule 16: Hiccup
if "Hiccup (Persistent/Intractable)" in symptoms:
    add_lesion("Medulla (Nucleus Tractus Solitarius)")
    add_lesion("Phrenic Nerve Nucleus (C3-C5 Spinal Cord)")
    add_lesion("Hypothalamus")
    add_lesion("Brainstem")
    add_vessel_to_affected("Vertebral Artery branches")
    add_vessel_to_affected("Posterior Inferior Cerebellar Artery (PICA)")
    ambiguity_notes.add("Persistent or intractable hiccups can be an important sign of brainstem, spinal cord, or other CNS lesions. Consider metabolic, GI, or autoimmune causes as well.")
    suggest_imaging = True

# Rule 17: Nystagmus
if "Nystagmus" in symptoms:
    add_lesion("Cerebellum") 
    add_lesion("Brainstem (Vestibular Nuclei)")
    add_lesion("Medial Longitudinal Fasciculus (MLF)") 
    add_lesion("Pontine Gaze Center (PPRF)") 
    add_lesion("Vestibular Nerve (Peripheral)")
    add_vessel_to_affected("PICA")
    add_vessel_to_affected("AICA")
    add_vessel_to_affected("Superior Cerebellar Artery")
    add_vessel_to_affected("Basilar Artery branches (pontine arteries)")
    add_vessel_to_affected("Vertebral Artery")
    ambiguity_notes.add("Nystagmus can be central (brainstem/cerebellar) or peripheral. Central Nystagmus is often vertical, purely torsional, or non-fatigable.")
    suggest_imaging = True

# --- Combine for Vascular Territory Analysis (Processing, not direct display) ---
# Special combined rules for common stroke syndromes
if "Right hemiparesis (Upper> Lower)" in symptoms and "Aphasia" in symptoms:
    vascular_analysis.add("Left Middle Cerebral Artery (MCA) - Superior Division (classic for Broca's aphasia and right arm/face weakness)")
    add_lesion("Left Frontal Lobe") # Add with standardization
    add_lesion("Left Parietal Lobe") # Add with standardization
    suggest_imaging = True
elif "Left hemiparesis (Upper> Lower)" in symptoms and "Neglect" in symptoms:
    vascular_analysis.add("Right Middle Cerebral Artery (MCA) - Inferior Division (classic for neglect and left arm/face weakness)")
    add_lesion("Right Parietal Lobe") # Add with standardization
    add_lesion("Right Temporal Lobe") # Add with standardization
    suggest_imaging = True
elif "Vision loss (Homonymous Hemianopia)" in symptoms and "Aphasia" in symptoms:
    vascular_analysis.add("Left Middle Cerebral Artery (MCA) - complete occlusion or Posterior Cerebral Artery (PCA) - with cortical aphasia")
    ambiguity_notes.add("Homonymous hemianopia with aphasia might suggest a large MCA stroke affecting visual pathways or a complex PCA stroke.")
    suggest_imaging = True
elif all(s in symptoms for s in ["Vertigo", "Dysarthria", "Facial palsy (Upper & Lower face equally affected)", "Sensory loss (Dissociated - e.g. pain/temp affected, light touch spared)"]):
    vascular_analysis.add("Vertebrobasilar System - Posterior Inferior Cerebellar Artery (PICA) - for Lateral Medullary (Wallenberg's) Syndrome")
    add_lesion("Lateral Medulla (Brainstem)")
    suggest_imaging = True
elif all(s in symptoms for s in ["Right hemiparesis (Upper & Lower equally)", "Facial palsy (Lower face only affected)", "Sensory loss (Hemibody, all modalities)"]):
    vascular_analysis.add("Left Lenticulostriate arteries (deep branches of MCA) - for Lacunar Syndrome (Pure Motor or Sensorimotor Stroke)")
    add_lesion("Left Internal Capsule")
    add_lesion("Left Basal Ganglia")
    suggest_imaging = True
elif all(s in symptoms for s in ["Left hemiparesis (Upper & Lower equally)", "Facial palsy (Lower face only affected)", "Sensory loss (Hemibody, all modalities)"]):
    vascular_analysis.add("Right Lenticulostriate arteries (deep branches of MCA) - for Lacunar Syndrome (Pure Motor or Sensorimotor Stroke)")
    add_lesion("Right Internal Capsule") # Add with standardization
    add_lesion("Right Basal Ganglia") # Add with standardization
    suggest_imaging = True


# --- Display Results Section ---

if lesion_locations or affected_vessels:
    # 1. Display Likely Lesion Locations
    st.header("Considers")
    if lesion_locations:
        for loc in sorted(list(lesion_locations)):
            st.markdown(f"- {loc}")
    else:
        st.info("No specific lesion locations identified from selected symptoms, but vascular involvement may be suggested below.")

    if ambiguity_notes:
        st.subheader("Considerations/Ambiguities:")
        for note in sorted(list(ambiguity_notes)):
            st.info(f"- {note}")

    # 2. Display Affected Vascular Territory Analysis
    st.header("Territory")
    if vascular_analysis:
        st.subheader("Most Likely Affected Arterial Supply:")
        for vessel_syndrome in sorted(list(vascular_analysis)):
            st.markdown(f"- **{vessel_syndrome}**")

        # Collect standardized vessel names that are ALREADY covered by the syndrome descriptions
        covered_by_syndromes_standardized = set()
        for syndrome_desc in vascular_analysis:
            # We standardize the full syndrome description to get a comparable core vessel name
            # This uses standardize_vessel_name to convert syndrome strings into their canonical vessel parts
            covered_by_syndromes_standardized.add(standardize_vessel_name(syndrome_desc))


        # Filter affected_vessels (which are already standardized by add_vessel_to_affected)
        # to show only truly "additional" ones
        additional_vessels_to_display = set() # Store the *original* standardized names from affected_vessels
        for individual_vessel_standardized in affected_vessels:
            is_covered = False
            
            if individual_vessel_standardized in covered_by_syndromes_standardized:
                is_covered = True
            
            for syndrome_core in covered_by_syndromes_standardized:
                if (syndrome_core == "Middle Cerebral Artery (MCA) - Superior Division" and individual_vessel_standardized == "Middle Cerebral Artery (MCA) branches") or \
                   (syndrome_core == "Middle Cerebral Artery (MCA) - Inferior Division" and individual_vessel_standardized == "Middle Cerebral Artery (MCA) branches") or \
                   (syndrome_core == "Posterior Inferior Cerebellar Artery (PICA)" and individual_vessel_standardized == "Basilar Artery branches (pontine arteries)") or \
                   (syndrome_core == "Anterior Inferior Cerebellar Artery (AICA)" and individual_vessel_standardized == "Basilar Artery branches (pontine arteries)") or \
                   (syndrome_core == "Superior Cerebellar Artery (SCA)" and individual_vessel_standardized == "Basilar Artery branches (pontine arteries)"):
                    is_covered = True
                    break # Break inner loop, as this individual vessel is covered by a syndrome
            
            if not is_covered:
                additional_vessels_to_display.add(individual_vessel_standardized)

        if additional_vessels_to_display:
            st.markdown("---")
            st.info("Additional potentially affected vessels based on symptoms:")
            for vessel in sorted(list(additional_vessels_to_display)):
                st.markdown(f"- {vessel}")
    else:
        # If no specific vascular syndrome matched, just display all identified affected_vessels
        if affected_vessels:
            st.subheader("Potentially Affected Arterial Supply based on symptoms:")
            for vessel in sorted(list(affected_vessels)):
                st.markdown(f"- **{vessel}**")
        else:
            st.info("No specific arterial territory analysis available for selected symptoms.")

    # 3. Next Steps (Imaging Recommendation)
    if suggest_imaging or use_nihss:
        st.subheader("Next Steps:")
        st.success("Given the symptoms and potential vascular involvement, **imaging (CT or MRI scan of the brain)** is highly recommended to confirm the lesion location and etiology.")
        if "Spinal Cord" in str(lesion_locations):
            st.success("If spinal cord involvement is suspected (e.g. dissociated sensory loss), **MRI of the spine** may also be indicated.")
        st.info("Consult with a neurologist for definitive diagnosis and management.")

else:
    st.warning("No specific lesion or vascular territory suggested. Please refine symptom selection.")
    if chief_complaint:
        st.info("If symptoms are vague or non-localizing, consultation is recommended for further evaluation.")


if use_nihss:
    st.header("NIHSS Score Calculator")

    st.markdown("NIHSS calculator is shown because a relevant chief complaint or symptom was entered (e.g.weakness).")

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

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='font-size:10px; color:gray;'>poorly written by thINGamabob, good patriotic techmarine and their evil twin</p>", unsafe_allow_html=True)
