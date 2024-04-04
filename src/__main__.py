from pointage import Pointage


def main():
    pointage = Pointage()
    args = pointage.parse()
    args.func(args)


if __name__ == "__main__":
    main()
