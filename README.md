# TulvingTest

Electronic Supplementary Material for 

The repository contains result data for the direct comparison Tulving Test performance by Large Language Models `mistral-7b-instruct-v0 ` without fine tuning, and a few instances by `orca-mini-3b`. All result data files are located in the `output`directory.

The repository contains Python scripts to perform the tests, in immediate or delayed form, for the recognition task (prefix `reco` in arguments or file names); for recall task with associative cues (prefix `reca` in arguments of file names) and recall task with ordinal cues (prefix `ord` in arguments or file names). Batch files (file name extension `.bat`) for Windows are also provided.

The repository contains Python scripts to tabulate results from result data files in `output`.

## Data Repository
The general template for result data file name is:
`merge\_TASK\_CHRONO\_MODEL\_session\_ID.csv`
where:
  *  TASK is one of *reco*, *reca* or *ord*
  *  CHRONO is one of *imm* for immediate or *del* for delayed
  *  MODEL is the id of the model used, here either _mistral_ or _orcamini_
  *  ID is a session identifier, e.g here a number in 6...17

The result data files are CSV-formatted with the following columns:
  * tbrword: target word from the study list to be remembered
  * result: result of the test, _1_ for OK, _0_ for fail
  * fp: result of the test counting only response words that appear in the study list (which counts false positives for non-copy cues that are otherwise scored _0_ in column `result`)
  * cue: cue word
  * response: LLM text response when relevant. (Occasionally the response is off-base: repeating or ignoring the question; these deviants are not recorded.)
  * cue_type: one of the following class of cue word
    * copy: a word from the study list
    * ncaw: a non-copy strongly associated word to the target in the study list, may contain synonyms or antonyms
    * ncrw: a non-copy cue word rhyming with the target word
    * ordn: an ordinal cue word (from _first_ to _twentieth_)
    * none: a distractor cue word, not included in the study list and unrelated to any such words
  * duration: the duration in ms of the LLM latency (computed by the Python `time`library).
  
## Script Repository
The Python scripts are as follows:

  * `cues.py` is used before a session to randomize 32 cue words for a test from the 48 words of the study list and assorted cues of different types.
  * `tulving_test.py` and variants, `tulving_test_imm.py`, `tulving_ord_del_test.py`, `tulving_ord_imm_test.py` runs a single test for given task, chronology and model, outputting a CSV-formatted table (see options `python tulving_test.py -h`).
  * `tulving_tabulate.py` tabulates aggregated results from result data files, generally outputting or-mode formatted text.
  * `words.py` and `resjoin.py` are utilities to query online dictionaries, and merge batches of result data files in unique CSV-formatted files, respectively.


<p xmlns:cc="http://creativecommons.org/ns#" >This work is licensed under <a href="http://creativecommons.org/licenses/by-sa/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">CC BY-SA 4.0<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/sa.svg?ref=chooser-v1"></a></p>
