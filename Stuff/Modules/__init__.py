def main():
    import os

    total = 0
    for file in os.listdir(os.getcwd()):
        if file[-3:] == ".py":
            infile = open(file)
            for count, line in enumerate(infile, 1):
                continue
            print(file + "\t" + str(count))
            total += count
    print(total)
    input("")
    
if __name__ == "__main__": main()
