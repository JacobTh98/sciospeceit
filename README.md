# ScioSpec EIT

Tools and documentation for electrical impedance tomography (EIT)
measurements with a ScioSpec device.

## Resources

- **Measurement data:** [Zenodo dataset](https://zenodo.org/records/8133612)
- **Paper:** [IEEE Xplore](https://ieeexplore.ieee.org/abstract/document/10781524)
- **Related repository:** [3dIT](https://github.com/JacobTh98/3dIT)

Please cite the paper when using this project or its data.

## Setup

The measurement workstation uses:

- [ScioSpec EIT Software](https://www.sciospec.com/)
- Python 3.11
- [Visual Studio Code](https://code.visualstudio.com/)
- [JupyterLab](https://jupyter.org/)

Connect the device through the `USB-FS` port, select the correct serial
port, and configure the electrode pattern and measurement parameters in the
software.

Measurement configurations (`*.pkl`) and temporary data in
`pyender/tmp_data/` are generated locally and excluded from Git.

## Acknowledgment

Funded by the Deutsche Forschungsgemeinschaft (DFG, German Research
Foundation), SFB 1270/2 - 299150580.

## License

TBD
