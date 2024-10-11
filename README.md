# Revisor
Students' Revision and Self-Evaluation App



### The Idea
Reinforcing conceptual topics by taking micro MCQ test and analyzing result history.

#### Dependencies
```
pip install flet
```
#### Project Execution
```
flet revisor.py
```

### Planned Features & Requirements
- Record and display Performance Stats (test scores history)
- Create and add questions to Question Bank (with tags: topics, difficulty)
- Testing Section (customization and conduction of test based on # of questions, difficulty and topic selection)
- Settings page ( UI personalization - theme colors, Reset Question bank, Reset Performance Stats )


## Specification & Resources
1. This project is built in python - [Python Docs](https://www.python.org/doc/)
2. Flet is a python framework to create beautiful GUIs and is based on Flutter by Google - [Flet Docs](https://flet.dev/docs)
3. Question bank is a json file with each object having the structure:
   
   ```
   {
    "q":"This is a sample question",
    "t":["easy","u1","Math"],
    "o":["option A","option B","option C","option D"],
    "a":2
   }
   ```

   `q` is the question,
   `t` is a list of tags for the question,
   `o` is a list of options (length of this list must be 4),
   `a` is the index of the correct option in the above list
