import sys


def main(argv):
    global eventNum
    inputFiles = argv[1:]
    eventNum = inputFiles[-1].split("/")[-1].split(".")[0].split("n")[1]


if __name__ == "__main__":
    eventNum = 0
    main(sys.argv[1:])
    print(eventNum)
