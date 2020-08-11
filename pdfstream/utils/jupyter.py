"""Some useful functions when using jupyter lab."""
from pathlib import Path

import matplotlib.pyplot as plt

LATEX_REF = (
    "\\begin{{figure}}[hptb]\n"
    "\\includegraphics[width=\\columnwidth]{{{}}}\n"
    "\\caption{{{}}}\n"
    "\\label{{fig:{}}}\n"
    "\\end{{figure}}\n"
)


def savefig_factory(figure_dir):
    """
    Create function 'savefig' to save the current figure in the directory.

    Parameters
    ----------
    figure_dir
        The directory to save the figure.

    Returns
    -------
    save_fig
        A function to save current figure.
    """
    figure_dir = Path(figure_dir)
    if not figure_dir.is_dir():
        figure_dir.mkdir()

    def savefig(fname: str,
                dpi=240,
                facecolor=None,
                edgecolor=None,
                orientation='portrait',
                papertype=None,
                fmt='pdf',
                transparent=True,
                bbox_inches=None,
                pad_inches=0.1,
                metadata=None,
                latex=True,
                caption=""):
        """
        The output formats available depend on the backend being used.
        The latex reference will be copied to clipboard.

        Parameters
        ----------

        fname : str or PathLike or file-like object
            A path, or a Python file-like object, or
            possibly some backend-dependent object such as
            `matplotlib.backends.backend_pdf.PdfPages`.

            If *format* is not set, then the output format is inferred from
            the extension of *fname*, if any, and from :rc:`savefig.format`
            otherwise.  If *format* is set, it determines the output format.

            Hence, if *fname* is not a path or has no extension, remember to
            specify *format* to ensure that the correct backend is used.

        dpi : [ *None* | scalar > 0 | 'figure' ]
            The resolution in dots per inch.  If *None*, defaults to
            :rc:`savefig.dpi`.  If 'figure', uses the figure's dpi value.

        facecolor : color spec or None, optional
            The facecolor of the figure; if *None*, defaults to
            :rc:`savefig.facecolor`.

        edgecolor : color spec or None, optional
            The edgecolor of the figure; if *None*, defaults to
            :rc:`savefig.edgecolor`

        orientation : {'landscape', 'portrait'}
            Currently only supported by the postscript backend.

        papertype : str
            One of 'letter', 'legal', 'executive', 'ledger', 'a0' through
            'a10', 'b0' through 'b10'. Only supported for postscript
            output.

        fmt : str
            The file format, e.g. 'png', 'pdf', 'svg', ... The behavior when
            this is unset is documented under *fname*.

        transparent : bool
            If *True*, the axes patches will all be transparent; the
            figure patch will also be transparent unless facecolor
            and/or edgecolor are specified via kwargs.
            This is useful, for example, for displaying
            a plot on top of a colored background on a web page.  The
            transparency of these patches will be restored to their
            original values upon exit of this function.

        bbox_inches : str or `~matplotlib.transforms.Bbox`, optional
            Bbox in inches. Only the given portion of the figure is
            saved. If 'tight', try to figure out the tight bbox of
            the figure. If None, use savefig.bbox

        pad_inches : scalar, optional
            Amount of padding around the figure when bbox_inches is
            'tight'. If None, use savefig.pad_inches

        metadata : dict, optional
            Key/value pairs to store in the image metadata. The supported keys
            and defaults depend on the image format and backend:

            - 'png' with Agg backend: See the parameter ``metadata`` of
              `~.FigureCanvasAgg.print_png`.
            - 'pdf' with pdf backend: See the parameter ``metadata`` of
              `~.backend_pdf.PdfPages`.
            - 'eps' and 'ps' with PS backend: Only 'Creator' is supported.

        latex : bool, optional
            Whether to copy the latex reference into clipboard. The template is in the LATEX_REF.

        caption : str, optional
            The caption for the figure in the latex.
        """
        fname = figure_dir.joinpath(fname)
        plt.savefig(
            fname,
            dpi=dpi,
            facecolor=facecolor,
            edgecolor=edgecolor,
            orientation=orientation,
            papertype=papertype,
            format=fmt,
            transparent=transparent,
            bbox_inches=bbox_inches,
            pad_inches=pad_inches,
            metadata=metadata
        )
        if latex:
            print(
                LATEX_REF.format(fname.name, caption, fname.stem)
            )
        return

    return savefig
