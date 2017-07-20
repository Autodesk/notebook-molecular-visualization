/*
This module:
1) Collects all notebooks that match notebooks/test_*.ipynb
2) Examines their internal JSON to create tests
3) Exports all tests given their internal names
 */
const glob = require('glob');
const fs = require('fs');
const assert = require('assert');
const dayguard = require('dayguard');

function collectTestsFromNotebooks() {
  /* Drives all test collection*/

  const notebookPaths = glob.sync('notebooks/*.ipynb');

  let tests = [];
  notebookPaths.forEach(function (path) {
    tests.push.apply(tests, makeTests(path));  // equivalent of list.extend in python
  });
  return tests;
}


function makeTests(path){
  /* Parses a notebook and creates tests from it */
  const nbjson = JSON.parse(fs.readFileSync((path)));

  let setupCellId = null;  // the current setup cell
  let fixtureCellIds = {};
  let fixtureDependency = {};
  let testSpecs = [];

  for (let cell_and_idx of nbjson.cells.entries()){ // loop over every cell in the notebook
    let cell = cell_and_idx[1];
    let idx = cell_and_idx[0];

    if(cell.cell_type != "code") continue;

    let spec = parseCodeCell(path, cell, idx);  // parses test specification

    if(spec.isSetup) setupCellId = idx;

    if(spec.isFixture != null){
      let name = spec.isFixture;
      assert(! (name in fixtureCellIds), "Fixture '" + name + "' defined twice");
      fixtureCellIds[name] = idx;
    }

    if(spec.needsFixture != null) fixtureDependency[idx] = spec.needsFixture;
    if(spec.isTest != null) testSpecs.push(spec);

  }

  let tests = {};
  testSpecs.forEach(function(spec){
    // Actually create the test and add it to the list:
    let name = spec.isTest;
    assert(! (name in tests), "Test '" + name + "' defined twice");
    tests[name] = makeTest(spec, fixtureCellIds, fixtureDependency, setupCellId);
  });

  testList = Object.values(tests);
  console.log('Found ' + testList.length + ' tests in ' + path + '.');
  return testList;
}


function makeTest(spec, fixtureCellIds, fixtureDependency, setupCellId){
  let test = {
    'name': spec.isTest,
    'cellIdx': spec.cellIdx,
    'path': spec.path
  };

  let cellsToRun = [];

  if(setupCellId != null){
    cellsToRun.push(setupCellId);
  }

  function getFixtureCellIds(idx) {
    if (!(idx in fixtureDependency)) return [];

    assert(fixtureDependency[idx] in fixtureCellIds,
      'Cell ' + idx + ' in file "' + spec.path + '" requests undefined fixture "'
      + fixtureDependency[idx] + '".');

    let fixtureIdx = fixtureCellIds[fixtureDependency[idx]];
    return getFixtureCellIds(fixtureIdx).concat([fixtureIdx])
  }

  cellsToRun.push.apply(cellsToRun, getFixtureCellIds(spec.cellIdx));
  test.setupCells = cellsToRun;
  return test;
}


function parseCodeCell(path, cell, idx){
  let spec = {
    path: path,
    isFixture: null,
    needsFixture: null,
    isTest: null,
    isSetup: false,
    cellIdx: idx};

  cell.source.forEach(function(l){
    if (l.substring(0, 2) != '#!') return spec;  // return on first non-shebang line
    let line = l.trim();
    fields = line.substring(2).match(/\S+/g);

    if (fields == null){
      return;
    }
    else if(fields.length == 1 && fields[0] == 'setup'){
      spec.isSetup = true;
    }
    else if(fields.length == 1 && fields[0].substring(0, 5) == 'test_'){
      assert(spec.isTest == null, 'Multiple test definitions for cell ' + idx);
      spec.isTest = fields[0];
    }
    else if(fields.length == 2 && fields[0] == 'with_fixture:'){
      assert(spec.needsFixture == null, "Only a single fixture dependency is allowed.");
      spec.needsFixture = fields[1];
    }
    else if (fields.length == 2 && fields[0] == 'fixture:') {
      assert(spec.isFixture == null, "Multiple fixture definitions for cell " + idx);
      spec.isFixture = fields[1];
    }
    else{
      assert(false, "Unrecognized shebang line: '" + line + "' in cell " + idx);
    }
  });

  return spec;
}


function makeTestFunctions() {
  let testDescriptions = collectTestsFromNotebooks();
  restarted = {};
  testDescriptions.forEach(function(td){restarted[td.path] = false});

  let testFunctions = {};

  testDescriptions.forEach(function (testDescription) {
    testFunctions[testDescription.name] = function (client) {
      console.log('Starting test: ' + JSON.stringify(testDescription));
      const targetIdName = testDescription.name+'_target';


      client.openNotebook(testDescription.path);

      if (restarted[testDescription.path]) {
        client.clearNbOutputs();
      } else {
        client.restartKernel(60000);  // currently we restart the kernel every time
        restarted[testDescription.path] = true;
      }

      testDescription.setupCells.forEach(function (cellNum) { client.executeCell(cellNum) });

      client.executeCell(testDescription.cellIdx)
        .pause(500)
        .tagCellOutputsWithId(testDescription.cellIdx, targetIdName)
        .takeScreenshotFromElement('#' + targetIdName + '_widgetarea', testDescription.name.substring(5));

      //client.pause(6000000);

      client.end();
    }
  });

  return testFunctions;
}


module.exports = makeTestFunctions();
