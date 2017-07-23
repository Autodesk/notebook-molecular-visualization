## Observing Jupyter with GALILEO

Galileo is a very basic visual regression test framework for Jupyter notebooks.

Currently part of notebook-molecular-visualization, will be refactored into its own npm package when I have time.

### Install

Requires Node > 7.5 and a java runtime.

```
git clone https://github.com/autodesk/notebook-molecular-visualization
cd notebook-molecular-visualization/tests/nb_widget_tester
npm install
npm run selenium
```

### Get started

Create a notebook and name it `test_widgets.ipynb`. Add the following cells:

```python
#! setup
import ipywidgets
```

```python
#! test_float_widget
ipywidgets.FloatWidget('float widget')
```

Run the tests from the same directory that you created this new notebook:

`[PATH_TO_GALILEO]/bin/galileo --launchnb`

If you haven't set a static Jupyter token or password, the token will be printed to the terminal when you first launch Jupyter.


### Visual output

`test_nbwidgets` will, by default, take a screenshot of the WIDGET output area from each test cell. After tests finish (succesfully or not), you can find:
 - `./latest_images/` - a directory containing all screenshots from the latest test run.
 - `./reports/` - a directory containing test output in JUnit XML format.
 - `./latest_visual_results.html` - open this in a webrowser in its current location in order to see all screenshots and regression comparisons. 



### Creating tests in a notebook
Tests are specified using one or more "shebang" (i.e., `#!`) lines at the beginning of a cell.

Each test is specified by a cell in a notebook with a first line of

```python
#! test_[test_name_here]
```

You can specify a global "setup cell" that runs before each test by putting this on the first line of the cell:

```python
#! setup
```

You can also specify named "fixture cells" that can be required to run before any specific tests.

For instance, here's how you would create a "fixture cell" that creates a python dictionary:

```python
#! fixture: create_example_dict
example_dict = {'a': 1, 'b': 2, 'c': 'three'}
```

You can then specify multiple tests that require this fixture with the `#! with_fixture` shebang line:

```python
#! test_len_of_example_dict_is_three
#! with_fixture: create_example_dict
assert len(example_dict) == 3
```

```python
#! test_example_dict_key_a_has_value_1
#! with_fixture: create_example_dict
assert example_dict['a'] == 1
```

