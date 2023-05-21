from argparse import ArgumentParser
from math import e
from scipy.optimize import curve_fit
from numpy import log
from matplotlib import pyplot as plt
import re

DESTINATION = ""


def first_order_polynom(x, a, b):
    return a*x + b


def second_order_polynom(x, a, b, c):
    return a*(x**2) + b*x + c


def third_order_polynom(x, a, b, c, d):
    return a*(x**3) + b*(x**2) + c*x + d


def log_like(x, a, b, c):
    return b*(log(x) / log(a))+c  # `log(x) / log(a)` to get log with `a` base. Got errors there, so don't used it


def elog_like(x, a, b):
    return a*log(x)+b


def exp_like(x, a, b):
    return a*(e**x) + b


def main() -> None:
    process_key()
    x_data, y_data = parse_input(DESTINATION)
    popt1, _ = curve_fit(first_order_polynom, x_data, y_data)
    popt2, _ = curve_fit(second_order_polynom, x_data, y_data)
    popt3, _ = curve_fit(third_order_polynom, x_data, y_data)
    popt4, _ = curve_fit(elog_like, x_data, y_data)
    popt5, _ = curve_fit(exp_like, x_data, y_data)

    plt.plot(x_data, y_data, 'bo', label='y - original')
    plt.plot(x_data, list(map(lambda x: first_order_polynom(x, popt1[0], popt1[1]), x_data)), label='first_order_polynom')
    plt.plot(x_data, list(map(lambda x: second_order_polynom(x, popt2[0], popt2[1], popt2[2]), x_data)), label='second_order_polynom')
    plt.plot(x_data, list(map(lambda x: third_order_polynom(x, popt3[0], popt3[1], popt3[2], popt3[3]), x_data)), label='third_order_polynom')
    plt.plot(x_data, list(map(lambda x: elog_like(x, popt4[0], popt4[1]), x_data)), label='elog_like')
    plt.plot(x_data, list(map(lambda x: exp_like(x, popt5[0], popt5[1]), x_data)), label='exp_like')
    plt.legend(loc='best', fancybox=True, shadow=True)
    plt.grid(True)
    plt.show()


def parse_input(file_name: str) -> (list[float], list[float]):
    x_data = list()
    y_data = list()
    x_y_data = list()
    parse_regex = re.compile("([\d,]+)[ \t]+(\d+)")
    with open(file_name, mode="r") as file:
        for line in file.readlines():
            pair = parse_regex.search(line)
            x_y_data.append((float(pair.group(1).replace(",", ".")), float(pair.group(2).replace(",", "."))))

    x_y_data.sort(key=lambda e: e[0])
    for pair in x_y_data:
        x_data.append(pair[0])
        y_data.append(pair[1])
    return x_data, y_data


def process_key() -> None:
    def configure_arg_parser() -> None:
        arg_parser.add_argument("-d", "--destination", dest="destination", required=True)

    global DESTINATION
    arg_parser = ArgumentParser()
    configure_arg_parser()
    args = arg_parser.parse_args()
    DESTINATION = args.destination


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
    finally:
        input("\nFor exit press Enter...")
