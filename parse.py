import pandas as pd
import re
# Definition der korrekten Bereiche (basierend auf Benutzerinfo)
meta_rows = range(6, 13)             # Projekt-Metadaten: Zeile 8–14 (Index 6–12)
project_kw_rows = range(13, 75)      # Projekt-Keywords: Zeile 15–76 (Index 13–74)
deliverable_meta_rows = 3           # Immer 3 Metazeilen pro Deliverable
deliverable_kw_rows = 61            # Danach 61 Zeilen mit Keywords
first_deliverable_start = 75        # Erste Deliverable beginnt in Zeile 77 (Index 76)

def create_kw_dict(labels, values):
    keywords = dict()
    for kw, val in zip(labels, values):
        # Extrahiere Kategorie (z. B. "SOCIAL") vor "Keywords"
        category_match = re.search(r"^(.*?)\s+Keywords", kw)
        # Extrahiere Label (z. B. "Wellbeing") aus eckigen Klammern
        label_match = re.search(r"\[(.*?)\]", kw)
        if category_match and label_match:
            category = category_match.group(1).strip().capitalize()
            label = label_match.group(1).strip()
            keywords[label] = {"category": category, "present": (val == "Yes")}
    return keywords


# Extraktions-Funktion
def extract_projects_for_visualization(df):
    projects_data = []
    for col, colname in enumerate(df.columns[1:]):  # Spalte 0 enthält Fragen
        col+=1
        project = {}

        # Projekt-Metadaten
        meta_keys = df.iloc[meta_rows, 0].values
        meta_vals = df.iloc[meta_rows, col].values
        project["name"] = df.iloc[7, col]  # [Project Name]
        project["acronym"] = df.iloc[8, col]  # [Project Acronym]
        project["metadata"] = dict(zip(meta_keys, meta_vals))

        # Projekt-Keywords
        kw_labels = df.iloc[project_kw_rows, 0].values
        kw_values = df.iloc[project_kw_rows, col].fillna("").astype(str).values
        project["keywords"] = create_kw_dict(kw_labels, kw_values)

        # Deliverables
        deliverables = []
        row = first_deliverable_start
        while row + deliverable_meta_rows + deliverable_kw_rows <= df.shape[0]:
            # Metadaten
            d_meta_keys = df.iloc[row:row+deliverable_meta_rows, 0].values
            d_meta_vals = df.iloc[row:row+deliverable_meta_rows, col].values
            # if pd.isna(d_meta_vals[0]) or d_meta_vals[0] == "":
            #     break  # kein weiteres Deliverable
            d_metadata = dict(zip(d_meta_keys, d_meta_vals))

            # Keywords
            d_kw_labels = df.iloc[row+deliverable_meta_rows:row+deliverable_meta_rows+deliverable_kw_rows, 0].values
            d_kw_values = df.iloc[row+deliverable_meta_rows:row+deliverable_meta_rows+deliverable_kw_rows, col].fillna("").astype(str).values

            deliverables.append({
                "metadata": d_metadata,
                "keywords": create_kw_dict(d_kw_labels, d_kw_values)
            })

            row += deliverable_meta_rows + deliverable_kw_rows  # Nächster Block

        project["deliverables"] = deliverables
        projects_data.append(project)

    return projects_data





if __name__ == "__main__":
    # Anwendung der Funktion
    df = pd.read_excel("results2.xlsx")
    p = extract_projects_for_visualization(df)

    # Vorschau
    p[0]

