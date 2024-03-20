from utils import Pointage


def main():
    pointage = Pointage()
    args = pointage.parse()
    try:
        args.func(args)
    except:
        pass


if __name__ == "__main__":
    main()
