# ScioSpecEIT

## Description

## Schedule

- [x] Set up measurement environment
- [x] Print out the ScioSpec user manual
- [x] First test measurement
- [ ] Review data
- [ ] Proceed and describe further steps

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

### Recommended software

- VSC-Code
- Pythoon
- C
- Java
- ScioSpecEIT
- JupyterLab
- SublimeMerge

## Components

### ScioSpec

Sciospec specializes in solutions for electrical impedance spectroscopy, impedance tomography and other electrochemical/-analytical techniques. Primary applications are bio-analytics, biosensors, material science and process control.

### Measurement PC

For starting, stopping, spectating, and evaluating the measurements.

Installed software:

- [x] Visual-Studio-Code
- [x] ScioSpecEIT
- [x] Sublime Merge
- [x] JupyterLab
- [x] Python3
- [ ] ...

### Measurement Components

- Saline
- ...

## Contributors

- jt292
- lk443
- ss1272


## Acknowledgment

SFB: Funded by the Deutsche Forschungsgemeinschaft (DFG, German Research Founda-
tion) – SFB 1270/2 - 299150580.

## License

 

## Project status

In Progress