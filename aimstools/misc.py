import logging
import matplotlib.pyplot as plt


def setup_custom_logger(name):
    formatter = logging.Formatter(fmt="{levelname:8s} | {message:s}", style="{")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger


logger = setup_custom_logger("root")


def set_verbosity_level(verbosity):
    logger = logging.getLogger("root")
    if verbosity == 0:
        level = "WARNING"
    elif verbosity == 1:
        level = "INFO"
    else:
        level = "DEBUG"
        formatter = logging.Formatter(
            fmt="{levelname:8s} {module:20s} {funcName:20s} |\n {message:s}", style="{"
        )
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)


def set_global_plotsettings():
    from matplotlib import rcParams
    import matplotlib.font_manager

    plt.style.use("seaborn-ticks")
    rcParams["legend.handlelength"] = 0.8
    rcParams["legend.framealpha"] = 0.8
    rcParams["font.size"] = 12
    rcParams["legend.fontsize"] = 12
    rcParams["legend.handlelength"] = 1
    # rcParams["font.sans-serif"] = "Arial"
    rcParams["font.family"] = "sans-serif"
    rcParams["text.usetex"] = False
    rcParams["mathtext.fontset"] = "stixsans"


set_global_plotsettings()

# color_definitions
mutedblack = "#1a1a1a"
fermi_color = "#D62728"
fermi_alpha = 1
darkgray = "#636363"
mpllinewidth = 2.0


class AxesContext:
    """ Base axes context.

    Args:
        main (bool): Helper value to identify execution orders in nested contexts to save/show the figure only in the main context.

    """

    def __init__(
        self,
        ax: "matplotlib.axes.Axes" = None,
        filename: str = None,
        figsize: tuple = (5, 4),
        main: bool = False,
        title: str = None,
    ) -> None:
        self.ax = ax
        self.filename = filename
        self.figure = None
        self.figsize = figsize
        self.main = main
        self.title = title

    def __enter__(self) -> "matplotlib.axes.Axes":
        if self.ax is None:
            self.figure, self.ax = plt.subplots(figsize=self.figsize)
            self.show = True
        else:
            self.figure = plt.gcf()
            plt.sca(self.ax)
            self.show = False
        logger.debug("Is main context: {}".format(self.main))
        if self.title != None:
            self.ax.set_title(str(self.title), loc="center")
        return self.ax

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        if (exc_type is None) and (self.main):
            # If there was no exception, display/write the plot as appropriate
            if self.figure is None:
                raise Exception("Something went wrong initializing matplotlib figure.")
            if self.show:
                plt.show()
            if self.filename is not None:
                self.figure.savefig(
                    self.filename,
                    dpi=300,
                    facecolor="white",
                    transparent=False,
                    bbox_inches="tight",
                )
        return None

