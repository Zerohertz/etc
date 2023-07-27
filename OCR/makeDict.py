import pickle


if __name__ == "__main__":
    with open('dict.txt', 'r') as f:
        tmp = f.readlines()[0]
    print(len(tmp))
    with open('../dict', 'wb') as f:
        pickle.dump(tmp, f)