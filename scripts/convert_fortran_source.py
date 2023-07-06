import re
import pathlib
from typing import List

import click


@click.command(no_args_is_help=True)    # type: ignore
@click.argument("fortran_files", nargs=-1, required=True, type=click.Path(
            exists=True, file_okay=True, dir_okay=False, readable=True,
            allow_dash=True, resolve_path=True, path_type=pathlib.Path))
def convert(fortran_files: List[pathlib.Path]) -> None:
    """Convert a Fortran file using the old-style Fortran libmuscle API to the new
    object-oriented API.
    """
    for fname in fortran_files:
        print("Replacing in file:", fname)
        indata = fname.read_text()

        for typ in [
                "LIBMUSCLE_Instance",
                "LIBMUSCLE_PortsDescription",
                "LIBMUSCLE_Message",
                "LIBMUSCLE_Data",
                "LIBMUSCLE_DataConstRef",
                "YMMSL_Settings"]:
            # Replace TYPE_create(...) with TYPE()
            indata = re.sub(rf"{typ}_create\(", f"{typ}(", indata)

            # Remove calls to free
            # Note: disabled because GCC does not correctly call the finalizers
            # indata = re.sub(rf"\n\s*call {typ}_free\(.*", "", indata)

            # Replace TYPE_method(instance, ...) with instance%method(...)
            # Note: create_ and free_ methods are not instance methods so are avoided
            indata = re.sub(
                    rf"{typ}_(?!create)(?!free)(.*?)\((\w+),? ?",
                    r"\2%\1(",
                    indata)

        fname.write_text(indata)


if __name__ == "__main__":
    convert()       # type: ignore
