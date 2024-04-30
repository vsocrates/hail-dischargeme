# Pipelines

There are three pipelines that we have tried to various degrees described in the main folder here. They are listed below:

1. **BART_pipeline**: This pipeline fine-tunes a BART model and then runs inference on the BHC. This is the one that we are most likely to use for the final submission
2. **gpt35_simple_pipeline**: This pipeline runs GPT 3.5 on the full dataset, taking in preceding text and outputting BHC (2-shot)
3. **gpt35_SOAP_pipeline**: This pipeline runs GPT 3.5 on teh full dataset in steps. We generate SOAP notes from the LLM using structured data and then generate the BHC from the set of SOAP notes. 