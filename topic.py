import json, glob

files = []
for file in glob.glob("topicos/*.json"):
    id = file.split("\\")[1].split(".")[0]
    name = id.replace("-", " ").title()
    with open(file, "r") as f:
        data = json.load(f)

    files.append({
        "id": id+".json",
        "name": name,
        "questions": len(data)
    })

with open("topics.json", "w") as file:
    json.dump(files, file, indent=4)
    