import os, sys, glob


def main():
    path = os.environ['MTDATADIR']
    path += "/*bin"
    for name in glob.glob(path):
        execute(name)


def execute(file):
    os.system("python3 quanah_analysis.py junk {}".format(file))


if __name__ == "__main__":
    main()
