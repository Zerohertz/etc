import os

import matplotlib.pyplot as plt


def get_size(path):
    if os.path.isfile(path):
        return os.path.getsize(path)
    else:
        total = 0
        for filename in os.listdir(path):
            filepath = os.path.join(path, filename)
            if os.path.isfile(filepath):
                total += os.path.getsize(filepath)
            elif os.path.isdir(filepath):
                total += get_size(filepath)
        return total


def get_file_and_directory_sizes(directory="."):
    sizes = {}
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        sizes[filename] = get_size(filepath)
    return sizes


def plot_sizes(sizes):
    labels = []
    sizes_list = []
    etc = 0
    for k, v in sizes.items():
        if v < 0.05 * (1024**3):
            etc += v
        else:
            labels.append(f"{k} ({v / (1024 ** 3):.2f} GB)")
            sizes_list.append(v)
    labels.append(f"Etc. ({etc / (1024 ** 3):.2f} GB)")
    sizes_list.append(v)

    plt.figure(figsize=(15, 10))
    plt.pie(sizes_list, labels=labels, autopct="%1.1f%%")
    plt.savefig("storage.png", dpi=300, bbox_inches="tight")


if __name__ == "__main__":
    plt.rcParams["font.size"] = 20
    plt.rcParams["font.family"] = "Times New Roman"
    directory = input("TARGET DIRECTORY:\t")
    sizes = get_file_and_directory_sizes(directory)
    plot_sizes(sizes)
