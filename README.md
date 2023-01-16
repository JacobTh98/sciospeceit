# ScioSpecEIT

## Description

## Schedule

- [x] Set up measurement environment
- [x] Print out the ScioSpec user manual
- [x] First test measurement
- [x] Review data
- [x] Proceed and describe further steps
- [ ] Write a `sciopy` module to convert .eit data and record data using a serial connection
- [ ] Record first experimental data

## Repository

### Clone
 ```
git clone https://gitlab.elaine.uni-rostock.de/b06/sciospeceit.git
 ```

### Branches

- `main` Merge of successful development steps
- `jac_dev` Developing branch for [jt292](https://gitlab.elaine.uni-rostock.de/jt292)

### Push and Merge from `own_branch` to `main`

```
git branch backup_branch
git checkout backup_branch

git branch -d own_branch
git branch own_branch
git checkout own_branch

git reset main
git add .
git commit -a -m "all i wanna say"
git push origin own_branch

git branch -d backup_branch

```

## Recommended software

- VSC-Code
- Pythoon
- C
- Java
- ScioSpecEIT
- JupyterLab
- SublimeMerge

# ScioSpec EIT Device

Sciospec specializes in solutions for electrical impedance spectroscopy, impedance tomography and other electrochemical/-analytical techniques. Primary applications are bio-analytics, biosensors, material science and process control.

## Start ScioSpec Software from PowerShell

- Plug in USB-Connection inside ScioSpec `USB-FS` and turn it on
- Navigate to directory (`C:\Users\ScioSpecEIT\Desktop\Sciospec EIT`)
- Right `shift`+ `right mouse click` and `Open in PowerSehell`
- Insert: `.\jre\bin\java.exe -jar .\Sciospec_EIT_Software_v1.19.jar 3.1416` or `.\jre\bin\java.exe -jar .\Sciospec_EIT_Software_v1.19.jar`
- Press `Enter` and the GUI opens
- Select `Serial` and the right `COM<n>`-port and press `OK` and `CONNECT`
- Inside the new window select `create setup` and insert your individual setup configuration e.g. Amplitude 1.0, Range[V] +/-5, Min f[Hz]=10k, Max f[Hz] = 10k,  Steps=1, Scale=LINEAR and press next.
- Select number of electrodes and the pattern.
- Continue with own measurement configuration
- ...

## ScioSpec Communication Interface

The Sciospec Communication Interface (COMinterface) enables the user to access all functions of the device by 
using any of the available master interfaces. The actual command structure is identical in all connection types.

### Syntax
The general structure of each communication with a Sciospec device:
The communication is done by frames
Each communication frame is constructed as follows
- 1 byte command-Tag (Frame-Start)
- 1 byte number of data-bytes (0...255) 0...255 data-bytes
- 1 byte Command-Tag (Frame-End)
- The command-tag identifies the command (see Command list)
- Frame-Start and –End must be identical

# Setup ScioSpec Measurement 

## Connection opportunities

**USB**
- Named "USB-HS" (USB High Speed) on the backplate of the ScioSpecEIT device
- Not galvanically isolated

**Ethernet**
- Not galvanically isolated
- Use for long distances
- High communication data rate, use local network (switch)

**Serial**
- Named "USB-FS" (USB Full Speed) on the backplate of the ScioSpecEIT device
- Data rates up to 1MB/s
- Galvanically isolated

## Framerate
It can be set near zero up to 100.

## Burst Count
Set the number of measurements that has to be done. If `0` the system measures until you press the measurement button again.

## Frequency
The defineable variables are `f_min`, `f_max`, `count` and `scale`.
- `f_min` is the start frequency
- `f_max` is the stop frequency 
- If `f_min` < `f_max` the `count` defines the equdistant steps between the min and max values
- `scale` can be selected as LINEAR or LOGARITHMIC. It has a direct impact to the `count` values 

## Switch

**ReedRelay**

Are much slower in switching ~600µs, but the parasitic capacitance and parasitic resistance are very low.

**Semiconductor**

The switch is used in fast measurements, because of its switching time of less than some ns. The disadvantage is high parasitic capacitance and parasitic resistance. 

## Measurement Mode

In any mode except "SingleEnded" the complex potentials are measured and saved to the .eit frame.
For E.g. the opposite drive pattern the mode has to be implemented on our own. For computing, the voltage data from complex potentials see the next chapter.

## Termination

The operator **Intern**  includes only measurement data of the defined electrode range. **Extern** records the external potential data too.

## Compute Voltage from Complex Potentials
Pay attention. The following order must be observed:
- Subtract the real and imaginary parts of the corresponding electrodes
- Compute the absolute value 


# Measurement PC

For starting, stopping, spectating, and evaluating the measurements.

Installed software:

- [x] Visual-Studio-Code
- [x] ScioSpecEIT
- [x] Sublime Merge
- [ ] JupyterLab
- [x] Python3.11

## Measurement Components

- [x] Saline
- [ ] Different object geometries
- [ ] ...

# Contributors

- jt292
- lk443
- ss1272

# Acknowledgment

Funded by the Deutsche Forschungsgemeinschaft (DFG, German Research Founda-
tion) – SFB 1270/2 - 299150580.

# License

 *TBD*

# Project status
In Progress