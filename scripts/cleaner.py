num_lines = 0
folder_path = __file__.split("scripts")[0]
filename = folder_path + f"data/spotify_tracks_timbre.csv"
cleaned_filename = folder_path + f"data/spotify_tracks_timbre_cleaned.csv"
f = open(cleaned_filename, "w")
f.write("id,status,timbre\n")

with open(filename, "r") as file:
    num_lines = sum(1 for line in file)
    
print("Cleaning file... ")
with open(filename, "r") as file:
    for line in file:
        print(f"\r{num_lines} lines left", end="")
        if ",200," in line: f.write(line)
        num_lines -= 1

f.close()
print("\rDone" + " " * 20)