from __future__ import annotations


import hist
from hist import Hist
import numpy as np



def to_yoda_1d(input: dict[str, Hist]) -> str:
    res = ""
    for path, h in input.items():
        if isinstance(h, Hist):
            res += _to_single_yoda_1d(path, h) + "\n\n"

    return res


def to_yoda_2d(input: dict[str, Hist]) -> str:
    res = ""
    for path, h in input.items():
        if isinstance(h, Hist):
            res += _to_single_yoda_2d(path, h) + "\n\n"
    return res


def print_line_1d(lower: str | float, upper: str | float, sumw: float, sumw2: float, sumwx:float , sumwx2: float, num_entries: float) -> str:
    if isinstance(lower, float):
        lower = format(lower, ".6e")
    if isinstance(upper, float):
        upper = format(upper, ".6e")
    return f"{lower:8}\t{upper:8}\t{sumw:.6e}\t{sumw2:.6e}\t{sumwx:.6e}\t{sumwx2:.6e}\t{num_entries:.6e}\n"

def print_line_2d(lower: str | float, upper: str | float, sumw: float, sumw2: float, sumwx:float , sumwx2: float, sumwy:float, sumwy2:float,sumwxy:float, num_entries: float) -> str:
    if isinstance(lower, float):
        lower = format(lower, ".6e")
    if isinstance(upper, float):
        upper = format(upper, ".6e")
    return f"{lower:8}\t{upper:8}\t{sumw:.6e}\t{sumw2:.6e}\t{sumwx:.6e}\t{sumwx2:.6e}\t{sumwy:.6e}\t{sumwy2:.6e}\t{sumwxy:.6e}\t{num_entries:.6e}\n"

def _to_single_yoda_1d(path: str, h: Hist) -> str:
    # Unpack single axis & values from histogram
    (axis,) = h.axes
    data = h.values()

    res = f"BEGIN YODA_HISTO1D_V2 {path}\n"
    res += f"Path: {path}\n"
    res += f"Title: {h.name}\n"
    res += "Type: Histo1D\n"
    res += "some: stuff\n"

    # Add histogram data
    res += "---\n"

    # Calculate area and mean
    area = h.sum(flow=True)
    mean = np.sum(axis.centers * data) / np.sum(data)

    # Add area and mean to YODA string
    res += f"# Mean: {mean:.6e}\n"
    res += f"# Area: {area:.6e}\n"

    res += "# ID\tID\tsumw\tsumw2\tsumwx\tsumwx2\tnumEntries\n"
    res += print_line_1d("Total", "Total", area, area, mean, mean, area)
    res += print_line_1d("Underflow", "Underflow", h[hist.underflow], h[hist.underflow], h[hist.underflow], h[hist.underflow], h[hist.underflow])
    res += print_line_1d("Overflow", "Overflow", h[hist.overflow], h[hist.overflow], h[hist.overflow], h[hist.overflow], h[hist.overflow])

    res += "# xlow\txhigh\tsumw\tsumw2\tsumwx\tsumwx2\tnumEntries\n"

    # Add histogram bins
    for xlow, xhigh, value in zip(axis.edges[:-1], axis.edges[1:], data):
        res += print_line_1d(xlow, xhigh, value, value, (xlow + xhigh) * 0.5 * value, (xlow + xhigh) * 0.5 * value ** 2, value)

    res += "END YODA_HISTO1D_V2\n"
    return res


def _to_single_yoda_2d(path: str, h: Hist) -> str:
    res = "BEGIN YODA_HISTO2D_V2 " + path + "\n"
    res += "Path: " + path + "\n"
    res += "Title: " + h.name + "\n"
    res += "Type: Histo2D\n"
    res += "some: stuff\n"

    # Add histogram data
    res += "---\n"
    
    (x_axis, y_axis) = h.axes
    data = h.values()

    # Calculate mean and volume
    mean_x = np.sum(x_axis.centers * data) / np.sum(data)
    mean_y = np.sum(y_axis.centers * data) / np.sum(data)
    volume = np.sum(data) * x_axis.widths[0] * y_axis.widths[0]
    

    # Add mean, volume, and ID to YODA string
    res += f"# Mean: ({mean_x:.6e}, {mean_y:.6e})\n"
    res += f"# Volume: {volume:.6e}\n"
    res += "# ID\tID\tsumw\tsumw2\tsumwx\tsumwx2\tsumwy\tsumwy2\tsumwxy\tnumEntries\n"
    res += print_line_2d("Total", "Total", volume, volume, mean_x * volume, mean_x * volume, mean_y * volume, mean_y * volume, volume, volume)
    res += "# xlow\txhigh\tylow\tyhigh\tsumw\tsumw2\tsumwx\tsumwx2\tsumwy\tsumwy2\tsumwxy\tnumEntries\n"

    # Add histogram bins
    x_bin_edges = h.axes[0].edges
    y_bin_edges = h.axes[1].edges

    for i in range(len(x_bin_edges) - 1):
        for j in range(len(y_bin_edges) - 1):
            xlow, xhigh = x_bin_edges[i], x_bin_edges[i + 1]
            ylow, yhigh = y_bin_edges[j], y_bin_edges[j + 1]
            sumw = data[i, j]
            sumw2 = sumw * sumw
            sumwx = sumw * (xlow + xhigh) * 0.5
            sumwx2 = sumw * (xlow + xhigh) * 0.5 * (xlow + xhigh) * 0.5
            sumwy = sumw * (ylow + yhigh) * 0.5
            sumwy2 = sumw * (ylow + yhigh) * 0.5 * (ylow + yhigh) * 0.5
            sumwxy = sumw * (xlow + xhigh) * 0.5 * (ylow + yhigh) * 0.5
            numEntries = data[i, j]
            res += f"{xlow:.6e}\t{xhigh:.6e}\t{ylow:.6e}\t{yhigh:.6e}\t{sumw:.6e}\t{sumw2:.6e}\t{sumwx:.6e}\t{sumwx2:.6e}\t{sumwy:.6e}\t{sumwy2:.6e}\t{sumwxy:.6e}\t{numEntries:.6e}\n"

    res += "END YODA_HISTO2D_V2\n"
    return res


# Reading the yoda format
def read_yoda(input) -> dict[str, tuple[str, str]]:
    yoda_dict = {}
    lines = input.split("\n")
    num_lines = len(lines)
    i = 0
    while i < num_lines:
        line = lines[i]

        if line.startswith("BEGIN"):
            path = line.split()[2]
            class_name = line.split()[1][:-3]

            body = line + "\n"  # to include the "BEGIN" line
            i += 1
            while i < num_lines and not lines[i].startswith("END"):
                body += lines[i] + "\n"
                i += 1

            body += lines[i] + "\n"  # to include the "END" line
            yoda_dict[path] = (class_name, body)
            return body

        i += 1

    return yoda_dict


# --------------------------------------------------------------------------------
# Sample input data for 1D
h1d = {
    "/some_h1d": Hist(hist.axis.Variable([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]), name="Histogram 1D")
}

h1d["/some_h1d"].fill(np.linspace(1,10,100))
yoda_file1D = to_yoda_1d(h1d)

yoda_data = read_yoda(yoda_file1D)
print(yoda_data)

# --------------------------------------------------------------------------------
# Sample input data for 2D
h2d = {
    "/some_h2d": Hist(
        hist.axis.Variable([1.0, 2.0, 3.0, 4.0, 5.0]),
        hist.axis.Variable([6.0, 7.0, 8.0, 9.0, 10.0]),
        name="Histogram 2D")
}

x_data = np.random.uniform(1, 5, 100)  
y_data = np.random.uniform(6, 10, 100)  

h2d["/some_h2d"].fill(x_data, y_data)
yoda_file2D = to_yoda_2d(h2d)

yoda_data2D = read_yoda(yoda_file2D)
print(yoda_data2D)




