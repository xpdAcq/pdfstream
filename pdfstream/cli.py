"""The command line intefrace function."""
import typing as tp
from pathlib import Path

import pdfstream.average as avg
import pdfstream.integration as integ
import pdfstream.io as io


def integrate(poni_file: str, img_files: tp.Union[str, tp.Iterable[str]], *, bg_img_file: str = None,
              output_dir: str = ".", bg_scale: float = None, mask_setting: tp.Union[dict, str] = None,
              integ_setting: dict = None, plot_setting: tp.Union[dict, str] = None,
              img_setting: tp.Union[dict, str] = None) -> None:
    """Azimuthal integration of the two dimensional diffraction image.

    The image will be first subtracted by background if background image file is given. Then, it will be binned
    in azimuthal direction according to the geometry provided by the poni file. The pixels far away from the
    average in each bin will be masked. The mask will be applied on the background subtracted image and the
    image will be integrated again by the pyFAI. The polarization correction and pixel-splitting algorithm will
    be applied according to user settings before the integration. The results are saved as chi files.

    Examples
    --------
    integrate diffraction_image.tiff calibrant.poni --bg_img_file background.tiff --integ_setting {npt: 2048}

    Parameters
    ----------
    poni_file : str
        The path to the poni file. It will be read by pyFAI.

    img_files : str or an iterable of str
        The path to the image file. It will be read by fabio.

    bg_img_file : str
        The path to the background image file. It should have the same dimension as the data image. If None,
        no background subtraction will be done.

    output_dir : str
        The directory to save the image file. Default current working directory.

    bg_scale : float
        The scale of the background. Default 1

    mask_setting : dict
        The settings for the auto-masking. See the arguments for mask_img (
        https://xpdacq.github.io/xpdtools/xpdtools.html?highlight=mask_img#xpdtools.tools.mask_img). To turn
        off the auto masking, enter "OFF".

    integ_setting : dict
        The settings for the integration. See the arguments for integrate1d (
        https://pyfai.readthedocs.io/en/latest/api/pyFAI.html#module-pyFAI.azimuthalIntegrator).

    plot_setting : dict
        The keywords for the matplotlib.pyplot.plot (
        https://matplotlib.org/3.2.1/api/_as_gen/matplotlib.pyplot.plot.html). To turn off the plotting,
        enter "OFF".

    img_setting : dict
        The keywords for the matplotlib.pyplot.imshow (
        https://matplotlib.org/3.2.1/api/_as_gen/matplotlib.pyplot.imshow.html). Besides, there is a key
        'z_score', which determines the range of the colormap. The range is mean +/- z_score * std in the
        statistics of the image. To turn of the image, enter "OFF".
    """
    if integ_setting is None:
        integ_setting = dict()
    if isinstance(img_files, str):
        img_files = [img_files]
    ai = io.load_ai_from_poni_file(poni_file)
    bg_img = io.load_img(bg_img_file) if bg_img_file else None
    for img_file in img_files:
        img = io.load_img(img_file)
        chi_name = Path(img_file).with_suffix('.chi').name
        chi_path = Path(output_dir).joinpath(chi_name)
        integ_setting.update({'filename': str(chi_path)})
        integ.main(ai, img, bg_img, bg_scale=bg_scale, mask_setting=mask_setting, integ_setting=integ_setting,
                   plot_setting=plot_setting, img_setting=img_setting)
    return


def average(out_file: str, img_files: tp.Union[str, tp.List[str]], *, weights: tp.List[float] = None) -> None:
    """Average the single channel image files with weights.

    Parameters
    ----------
    out_file : str
        The output file path. It will be the type as the first image in img_files.

    img_files : str or an iterable of str
        The image files to be averaged.

    weights : an iterable of floats
        The weights for the images. If None, images will not be weighted when averaged.
    """
    if isinstance(img_files, str):
        img_files = [img_files]
    imgs = (io.load_img(_) for _ in img_files)
    avg_img = avg.main(imgs, weights=weights)
    io.write_img(out_file, avg_img, img_files[0])
    return


def iq_to_gr():
    return


def vis_fit():
    return


def vis_data():
    return
