import marimo

__generated_with = "0.1.88"
app = marimo.App()


@app.cell
def __():
    import marimo as mo
    mo.md(
        """
        # Methods
        """
    )
    return mo,


@app.cell
def __(mo):
    mo.md(
        """
        Tulving Tests of memory are administered to Large Language Models (LLM). Two memory tasks are investigated in a simple word-model: *word recognition* and *word recall* from a word list previously memorized.
        
    - Word Recognition: a *cue* word is prompted to the LLM which should answer whether or not the word is included in the list. (A "yes or no" answer.)
    - Word Recall: a cue word is prompted to the LLM which should answer with a word in the list /related/ to the cue or "none" if no such related word is evoked.

    Tests are run either immediately after memorizing the list (immediate tests) or after a delay (delayed test).

    Following the experimental setup of Tulving's book, *Elements of Episodic Memory*, memory performance is tabulated by counting familiar words (in word recognition) and properly identified words (in word recall) actually in the original list, from the LLM's answers to the test prompts.
        """
    )
    return


if __name__ == "__main__":
    app.run()
