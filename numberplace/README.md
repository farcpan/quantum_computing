# numberplace
`Numberplace` solver with D-Wave API. 

You can solve `numberplace` problems which you prepare. 

## Preparation
2 steps of the preparation are necessary to execute the script. 

### Input file
You have to prepare the input CSV file. The example file is placed at `./input/` directory. 
The column with `0` means that the corresponding cell is empty. 

### Ocean environment
It is needed to create the `ocean` environment. Please see [here](https://github.com/dwavesystems/dwave-ocean-sdk) to know details. 

```console
$ source ~/ocean/bin/activate
(ocean)$ 
```

## Execution
You can solve the problem by the following command:

```console
$ python numberplace.py --input ./input/input_example.csv" --sampler "dwave"
```

If you do not specify the input file path, the default path `./input/input_example.csv` will be used. 
If you do not specify the `sampler` option, the tabu search simulator (instead of D-Wave) solves the problem. 
When you specify `--sampler dwave"`, it is necessary to access authority to the D-Wave. 
