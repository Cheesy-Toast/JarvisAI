class Print:
    """Print values to a stream with configurable separators and terminators."""

    def __init__(self, stream=None, sep=" ", end="\n"):
        self.stream = stream if stream is not None else __import__("sys").stdout
        self.sep = sep
        self.end = end

    def __call__(self, *values, sep=None, end=None):
        separator = self.sep if sep is None else sep
        terminator = self.end if end is None else end
        self.stream.write(separator.join(str(value) for value in values) + terminator)
        self.stream.flush()


if __name__ == "__main__":
    printer = Print()
    printer("Hello", "world", sep="-", end="!\n")
