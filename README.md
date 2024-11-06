# PyWMCpuStat

Remote CPU stat. Each cpu represented as a box.
Green to Red color to show load.

Supports up to 128cpu's 

## Setup
System uses SSH to remotely run command on `remote` and then takes the result for further processing.

## Example

```bash
./pywmcpustat.py --name boba --remote boba.conrock.arpa
```

[<img src="assets/screenshot.png">]
