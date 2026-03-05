import csv
from pathlib import Path
import os
import re
import shutil
import uuid
DATA_DIR: Path = Path("../") / "data" 
MEMBER_DIR: Path = DATA_DIR / '4_longcards_membres'
EVENT_DIR: Path = DATA_DIR / "1_cards_événements"
SPLIT_PATTERN: str = r"\s|\'|\-|\_|«|»|,"
IMAGE_PATH = "./avatar.webp"
IGNORE_MEMBER_COLUMNS = ["Nom d'utilisateur", "Prénom et Nom", "Fonction"]

def make_yaml_header_member(name: str, position: str) -> str:
    return (f"---\n" +
            f"uuid: {uuid.uuid4()}\n" +
            f"prettyName: {''.join(re.split(pattern=SPLIT_PATTERN, string=name))}\n\n" +
            f"title: {name}\n" +
            f"abstract: {position}\n" +
            f"---\n\n")


def make_yaml_header_event(title: str, author: str, abstract: str) -> str:
    return (f"---\n" +
            f"uuid: {uuid.uuid4()}\n" +
            f"title: \"{title}\"\n" +
            f"author: \"{author}\"\n" +
            f"event: true\n" +
            f"abstract: \"{abstract}\"\n" +
            f"---\n\n")


def generate_markdown_page_event(event_dict: dict, main_header: str, author_header: str, abstract_header: str, photo_header: str):
    md_page: str = make_yaml_header_event(
        title=event_dict[main_header], author=event_dict[author_header], abstract=event_dict[abstract_header])
    # add photo to page
    if event_dict[photo_header] != "":
        md_page += f"![Picture for {event_dict[main_header]}]()\n\n"
    event_dict.pop(photo_header)
    for key, val in event_dict.items():
        if val != "":
            md_page += f"## {key}\n\n {val}\n\n"
    return md_page


def generate_markdown_page_member(member_dict: dict, main_header: str, position_header: str, photo_header: str):
    md_page: str = make_yaml_header_member(
        name=member_dict[main_header], position=member_dict[position_header])
    # add photo to page
    if member_dict[photo_header] != "":
        md_page += f"![small]({member_dict[photo_header]})\n\n"
    else:
        md_page += f'<img src="{IMAGE_PATH}" width="200px" />\n\n'
    member_dict.pop(photo_header)
    for key, val in member_dict.items():
        if val != "" and key not in IGNORE_MEMBER_COLUMNS:
            md_page += f"## {key}\n\n {val}\n\n"
    return md_page


def csv_to_markdown_members(csv_file: str, main_header: str = "Prénom et Nom", position_header: str = "Fonction", photo_header: str = "Photo"):
    global MEMBER_DIR
    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            # print(row)
            member_name: str = row[main_header]
            member_subdir: Path = MEMBER_DIR / ("_".join(member_name.split())).lower()

            member_subdir.mkdir(parents=True, exist_ok=True)
            if row[photo_header] != '' and os.path.exists('./inputs/photos/' + row[photo_header]):
                shutil.copy('./inputs/photos/' + row[photo_header], str(member_subdir / row[photo_header]))
            else:
                shutil.copy('./resources/avatar.webp', str(member_subdir / 'avatar.webp'))
            with (member_subdir / "index.md").open(mode="w", encoding="utf-8") as md_file:
                md_file.write(generate_markdown_page_member(member_dict=row,
                                                            main_header=main_header, position_header=position_header, photo_header=photo_header))
    return


def csv_to_markdown_events(csv_file: str, main_header: str = "Titre", author_header: str = "Organisateur(s)", abstract_header: str = "Descriptif", photo_header: str = "Photo"):
    global EVENT_DIR
    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            d, m , y = row['Date'].split('/')
            date_str = f'{y}-{m}-{d}'
            title: str = clean_folder_name(row[main_header])
            folder_name = date_str + "_" + title
            event_subdir: Path = EVENT_DIR / folder_name
            event_subdir.mkdir(parents=True, exist_ok=True)
            
            with (event_subdir / "index.md").open(mode="w", encoding="utf-8") as md_file:
                md_file.write(generate_markdown_page_event(event_dict=row, main_header=main_header,
                              author_header=author_header, abstract_header=abstract_header, photo_header=photo_header))
    return


def csv_to_markdown_categories(csv_file_categories):
    with open(csv_file_categories, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')
        
        for row in reader:
            # Construire le chemin du dossier
            group = row['groupe']
            type_ = row['type']
            name = row['nom']
            description = row['description']
            
            folder_name = f"{group}_{type_}_{name}"
            folder_path =  DATA_DIR / folder_name

            if "membres" in folder_name:
                global MEMBER_DIR
                MEMBER_DIR = folder_path

            if "événements" in folder_name:
                global EVENT_DIR
                EVENT_DIR = folder_path
            
            # Créer le dossier s'il n'existe pas
            folder_path.mkdir(exist_ok=True, parents=True)
            
            # Chemin du fichier index.md
            index_file_path = folder_path / 'index.md'
            
            # Écrire le contenu dans index.md
            with index_file_path.open(mode='w', encoding='utf-8') as index_file:
                header = f"---\n" + f"uuid: {uuid.uuid4()}\n" + f"title: \"{name.capitalize()}\"\n" + "---\n"
                content = header + description
                index_file.write(content)

def clean_folder_name(name: str) -> str:
    # Liste des caractères interdits sous Windows pour les noms de fichiers/dossiers
    invalid_chars = r'<>:)([]+"/\\|?«»*'
    cleaned_name = re.sub(f"[{re.escape(invalid_chars)}]", "_", name)
    
    # Supprimer les caractères non imprimables (contrôle ASCII)
    cleaned_name = re.sub(r"[^\x20-\x7E]", "", cleaned_name)
    
    # Supprimer les espaces en début/fin et remplacer les espaces multiples par un seul tiret bas
    cleaned_name = re.sub(r"\s+", "_", cleaned_name.strip())
    
    # Limiter la longueur à 255 caractères (limite commune pour les noms de dossier)
    return cleaned_name[:50].lower()

print("Dossiers et fichiers créés avec succès.")

# Example usage:
csv_file_member = './inputs/members.csv'
csv_file_event = "./inputs/calendar.csv"
csv_file_accueil = "./inputs/accueil.csv"
csv_file_projets = "./inputs/projets.csv"
csv_file_liens = "./inputs/liens_ressources.csv"
csv_file_categories = "./inputs/categories.csv"

csv_to_markdown_categories(csv_file_categories)
csv_to_markdown_events(csv_file_accueil)
csv_to_markdown_members(csv_file_member)
csv_to_markdown_events(csv_file_event)
csv_to_markdown_events(csv_file_projets)
csv_to_markdown_events(csv_file_liens)


