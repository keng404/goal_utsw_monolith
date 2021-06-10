# goal_consortium_monolith

Docker monolith containing all scripts and binaries for v1.0.9 GOAL DNA pipeline.

Based off of https://github.com/bcantarel/school

Using scripts from https://github.com/bcantarel/process_scripts

## main files
- Docker.monolith ( refactoring needed ) --- current 'production image' is  keng404/goal_consortium_dna_monolith:1.3.9cm
```bash
docker build -f Docker.monolith -t {YOUR_IMAGE_NAME} .
```
- bamqc.sh 
- delly_v0.8.2_linux_x86_64bit ( downloaded delly binary to avoid installation breaking)
- goalConsensus.nf (added robustness to process resubmissions and made every process locally-executed)
- sequenceqc_dna.pl (added print statements and conditions)
- tool_wrapper_nf.py ( python wrapper that invokes goalConsensus.nf)
- design.txt ( tumor-only design file)
- somatic_design/design.txt (somatic design file)

## Running this in ICA
- [Pipeline diagram](https://github.com/keng404/goal_utsw_monolith/blob/main/UTSW_dna_monolith_tool.png)
- [CWL](https://github.com/keng404/goal_utsw_monolith/blob/main/utsw_dna_monolith.nextflow.cwl) of this tool/pipeline
